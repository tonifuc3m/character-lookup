#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 12:28:49 2020

@author: antonio
"""
from utils.general_utils import Flatten
from Levenshtein import distance as levenshtein_distance
from string import punctuation, whitespace
import re
import os

def get_windows(text, w_length): 
    '''
    Get sliding windows from string.
    
    Parameters
    ----------
    text: string
    w_length: int
        window length
    
    Returns
    -------
    windows: list
        Sliding windows
    '''
    windows = [text[i:i+w_length] for i in range(len(text)-(w_length-1))]
    return windows

def process_list(list_, ref_len):
    '''
    Process list of string of equal length: strip, remove elements with \n 
    inside and remove elements with length shorter than reference length.
    
    Parameters
    ----------
    list_: list
        List of strings to process
    ref_len: int
        Reference length. Items in list shorter than this length will be removed
    
    Returns
    -------
    list_processed: list
        List of processed strings
    '''
    punctuation_list = list(punctuation)
    punctuation_list.remove('(')
    punctuation_list.remove(')')
    punctuation_subs = ''.join(punctuation_list)
    # Strip windows
    list_stripped = list(map(lambda x: x.strip(), list_))
    # remove windows with \n INSIDE (.strip()) it
    list_filtered = list(filter(lambda x: '\n' not in x.strip(), list_stripped)) 
    # remove leading and trailing punctuation and blankspaces
    list_stripped = list(map(lambda x: x.strip(whitespace + punctuation_subs), 
                             list_filtered))
    # Remove duplicates
    list_deduplicated = list(set(list_stripped))
    # Remove windows with length smaller than original_len
    list_processed = list(filter(lambda x: len(x) >= ref_len, list_deduplicated))
    return list_processed


def distance(string, lista, threshold):
    '''
    Return elements in list whose Levenshtein distance to a string is smaller
    than a threshold.
    
    Parameters
    ----------
    string: string
    lista: list
        List of strings
    threshold: int
    
    Returns
    -------
    matches: list
        List of items in lista whose Levenshtein distance to the input string
        is smaller than the threshold
    '''
    matches = []
    for a in lista:
        if levenshtein_distance(a, string)<threshold:
            matches.append(a)
    return matches

def main(r, filename, df, threshold=2):
    '''
    Computes lookup.
    
    Parameters
    ----------
    r: string
        route to directory where files are stored
    filename: string
        TXT filename
    df: pandas dataframe
        Dataframe with Lookup information. It has four columns: 
            filename, label, span, length
    threshold: int
        Levenshtein distance threshold
    
    Returns
    -------
    ann: list
        ANN annotations (T#     label pos0 pos1     span)
    '''
    # Initialize
    t = 0
    ann = []
    
    # Get text
    text = open(os.path.join(r, filename)).read()
    # Get annotations not in this text
    filename_ann = '.'.join(filename.split('.')[0:-1]) + '.ann'
    df_this = df.loc[df['filename'] != filename_ann,:].drop_duplicates(subset = ['label', 'span'])
    for idx, row in df_this.iterrows():
        length = df_this.loc[idx, 'length']
        span = df_this.loc[idx, 'span']
        label = df_this.loc[idx, 'label']
        
        # Get windows
        windows = get_windows(text, length+threshold-1)
        windows = process_list(windows, length)
        
        # Calculate matches   
        matches_this = distance(span, windows, threshold)
        try:
            positions = list(map(lambda x: [(m.start(), m.end(), m.group()) for m in
                                            re.finditer(x, text)], matches_this))
        except:
            # Add re.escape() to avoid parenthesis to be considered as regex pattern
            positions = list(map(lambda x: [(m.start(), m.end(), m.group()) for m in
                                re.finditer(re.escape(x), text)], matches_this))
        positions = Flatten(positions)
        
        # Add to ANN
        for pos in positions:
            t = t + 1
            # Check that there are no alphanumeric characters before and after
            # the new annotation
            if pos[0] > 0: 
                if text[pos[0]-1].isalnum():
                    continue
            if pos[1]<len(text):
                if text[pos[1]].isalnum():
                    continue
            '''ann.append('T' + str(t) + '\t' + '_SUG_' + label + ' ' +
                       str(pos[0]) + ' ' + str(pos[1]) + '\t' + pos[2])'''
            ann.append([filename, t, label, pos[0], pos[1], pos[2]])
    return ann