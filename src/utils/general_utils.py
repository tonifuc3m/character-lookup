#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 11:00:32 2020

@author: antonio
GENERAL UTILS USED IN DISTANCE-LOOKUP REPO
"""
import string
import unicodedata
import re
import argparse
from spacy.lang.es import Spanish
import pandas as pd

def tokenize(text):
    '''
    Tokenize a string in Spanish
    Parameters
    ----------
    text : str
        Spanish text string to tokenize.
    Returns
    -------
    tokenized : list
        List of tokens (includes punctuation tokens).
    '''
    nlp = Spanish()
    doc = nlp(text)
    token_list = []
    for token in doc:
        token_list.append(token.text)
    return token_list


def Flatten(ul):
    '''
    DESCRIPTION: receives a nested list and returns it flattened
    
    Parameters
    ----------
    ul: list
    
    Returns
    -------
    fl: list
    '''
    
    fl = []
    for i in ul:
        if type(i) is list:
            fl += Flatten(i)
        else:
            fl += [i]
    return fl

def argparser():
    '''
    DESCRIPTION: Parse command line arguments
    '''
    
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-i", "--input-annot", required = True, dest = "input_annot", 
                        help = "absolute path to already annotated brat files or TSV with 4 columns: filename, label, span")
    parser.add_argument("-d", "--datapath", required = True, dest = "datapath", 
                        help = "absolute path to already brat files")
    parser.add_argument("-o", "--output-brat", required =  True, 
                        dest="output_path_new_files", 
                        help = "absolute path to output brat files")
    
    args = parser.parse_args()
    
    datapath = args.datapath
    input_annotations = args.input_annot
    output_path_new_files = args.output_path_new_files
    
    return datapath, input_annotations, output_path_new_files


def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.printable)


def parse_tsv(input_path_old_files):
    '''
    DESCRIPTION: Get information from ann that was already stored in a TSV file.
    
    Parameters
    ----------
    input_path_old_files: string
        path to TSV file with columns: ['annotator', 'bunch', 'filename', 
        'mark','label', 'offset1', 'offset2', 'span']
        Additionally, we can also have the path to a 3 column TSV: ['filename', 'label', 'span']
    
    Returns
    -------
    df_annot: pandas DataFrame
        It has 3 columns: 'filename', 'label', 'span'.
    '''
    
    df_annot = pd.read_csv(input_path_old_files, sep='\t', header=None)
    if len(df_annot.columns) == 8:
        df_annot.columns=['annotator', 'bunch', 'filename', 'mark',
                      'label', 'offset1', 'offset2', 'span']
    else:
        df_annot.columns = ['filename', 'label', 'span']
    return df_annot


            
            
def normalize_str(annot, min_upper):
    '''
    DESCRIPTION: normalize annotation: lowercase, remove extra whitespaces, 
    remove punctuation and remove accents.
    
    Parameters
    ----------
    annot: string
    min_upper: int. 
        It specifies the minimum number of characters of a word to lowercase 
        it (to prevent mistakes with acronyms).
    
    Returns
    -------
    annot_processed: string
    '''
    # Lowercase
    annot_lower = ' '.join(list(map(lambda x: x.lower() if len(x)>min_upper else x, annot.split(' '))))
    
    # Remove whitespaces
    annot_bs = re.sub('\s+', ' ', annot_lower).strip()

    # Remove punctuation
    annot_punct = annot_bs.translate(str.maketrans('', '', string.punctuation))
    
    # Remove accents
    annot_processed = remove_accents(annot_punct)
    
    return annot_processed