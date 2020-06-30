#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 10:57:04 2020

@author: antonio
"""


from utils.general_utils import (argparser, parse_tsv)
from utils.brat_utils import (copy_dir_structure, copy_all_files, modify_copied_files, 
                              remove_redundant_suggestions)
from utils.parse_ann import parse_ann
from compute_lookup import main
import os
import pandas as pd


if __name__ == '__main__':
    print('\n\nParsing script arguments...\n\n')
    datapath, lookup_information, out_datapath = argparser()
        
    ######## Get lookup information ########
    print('\n\nParsing input lookup information...\n\n')    
    if lookup_information.split('.')[-1] == 'tsv':
        df_annot = parse_tsv(lookup_information)
    else:
        df_annot = parse_ann(lookup_information)
        df_annot = df_annot.drop(['annotator', 'mark', 'offset'], axis=1)
    len_ = df_annot.apply(lambda x: len(x['span']), axis=1)
    df_annot = df_annot.assign(length = len_.values)
    
    ######## Main ########
    print('\n\nExecuting character lookup...\n\n')
    # Execute lookup
    ann = []
    for r, d, f in os.walk(datapath):
        for filename in f:
            print(filename)
            if filename[-3:] != 'txt': # get only txt files
                continue
            ann = ann + main(r, filename, df_annot)
            #print(ann[filename])
            
    # Remove duplicates
    df_new = pd.DataFrame.from_records(ann, 
                                       columns=['fname','m','label','p0','p1','span'])
    df_new = df_new.drop_duplicates(subset=['fname','label','p0','p1','span'])
    ann_dedupl = (df_new.groupby('fname')[['m','label','p0','p1','span']].
                  apply(lambda g: list(map(tuple, g.values.tolist()))).to_dict())   
    
    ######## Write output files ########
    print('\n\nWriting output ANN and TXT files...\n\n')
    # Copy directory structure
    copy_dir_structure(datapath, out_datapath)  
    # Copy all files           
    copy_all_files(datapath, out_datapath)
    # Modify annotated files
    modify_copied_files(ann_dedupl, out_datapath)

    ######## Remove redundant suggestions ########
    # TODO: check this is correct: 1) remove suggestions already in annotation, 
    # 2) Not duplicated suggestions (in case I re-run this code twice with different
    # input information)
    print("\n\nRemoving redundant suggestions...\n\n")
    remove_redundant_suggestions(out_datapath)