#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 10:58:53 2020

@author: antonio
PARSE ANN
"""

import os
import pandas as pd

def parse_ann(datapath, labels_to_ignore = [], with_notes=False):
    '''
    DESCRIPTION: parse information in .ann files.
    
    Parameters
    ----------
    datapath: str. 
        Route to the folder where the files are. 
           
    Returns
    -------
    df: pandas DataFrame 
        It has information from ann files. Columns: 'annotator', 'filename',
        'mark', 'label', 'offset', span', 'code'
    filenames: list 
        list of filenames
    '''
    info = []
    ## Iterate over the files and parse them
    filenames = []
    for root, dirs, files in os.walk(datapath):
         for filename in files:
             if filename[-3:] != 'ann':
                 continue # get only ann files
             #print(os.path.join(root,filename))
             
             info, filenames = parse_one_ann(info, filenames, root, filename)

    # Save parsed .ann files
    if with_notes == True:
        df = pd.DataFrame(info, columns=['annotator', 'filename', 'mark',
                                         'label','offset', 'span', 'code'])
    else:
        df = pd.DataFrame(info, columns=['annotator', 'filename', 'mark',
                                         'label','offset', 'span'])
    
    #return df, filenames
    return df


def parse_one_ann(info, filenames, root, filename, labels_to_ignore = [],
                  ignore_related=False, with_notes=False):
    '''
    DESCRIPTION: parse information in one .ann file.
    
    Parameters
    ----------
           
    Returns
    -------
    
    '''
    f = open(os.path.join(root,filename)).readlines()
    filenames.append(filename)
    # Get annotator and bunch
    annotator = root.split('/')[-1]
    
    # Parse .ann file
    related_marks = []     
    if ignore_related == True:   
        # extract relations
        for line in f:
            if line[0] != 'R':
                continue
            related_marks.append(line.split('\t')[1].split(' ')[1].split(':')[1])
            related_marks.append(line.split('\t')[1].split(' ')[2].split(':')[1])
            
    mark2code = {}
    if with_notes == True:
        # extract notes
        for line in f:
            if line[0] != '#':
                continue
            line_split = line.split('\t')
            mark2code[line_split[1].split(' ')[1]] = line_split[2].strip()
    
    for line in f:
        if line[0] != 'T':
            continue
        splitted = line.split('\t')
        if len(splitted)<3:
            print('Line with less than 3 tabular splits:')
            print(root + filename)
            print(line)
            print(splitted)
        if len(splitted)>3:
            print('Line with more than 3 tabular splits:')
            print(root + filename)
            print(line)
            print(splitted)
        mark = splitted[0]
        if mark in related_marks:
            continue
        label_offset = splitted[1]
        label = label_offset.split(' ')[0]
        if label in labels_to_ignore:
            continue
        offset = ' '.join(label_offset.split(' ')[1:])
        span = splitted[2].strip()
        
        if with_notes == False:
            info.append([annotator, filename, mark, label,
                         offset, span])
            continue
        
        if mark in mark2code.keys():
            code = mark2code[mark]
            info.append([annotator, filename, mark, label,
                         offset, span, code])
            
    return info, filenames