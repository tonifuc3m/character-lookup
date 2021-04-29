#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 12:21:53 2020

@author: antonio
FUNCTION USED TO DEAL WITH BRAT FILES
"""

from shutil import copyfile
import os

def modify_copied_files(new_annots, out_path, with_notes=False):
    '''
    DESCRIPTION: add suggestions (newly discovered annotations) to ann files.
    
    Parameters
    ----------
    new_annots: python dict 
        It has new annotations and the file they belong to. 
        {filename: [annotation1, annotatio2, ]}
    out_path: str
        Path to files.
    with_notes: bool
        whether we are predicting codes, or not
    '''
    files_new_annot = list(new_annots.keys())
    
    for root, dirs, files in os.walk(out_path):
        for filename in files:
            if filename not in files_new_annot:
                continue
            if filename[-3:] != 'txt':
                continue
            filename_ann = filename[0:-3]+ 'ann'
            
            # Get highest mark in ann
            if os.path.exists(os.path.join(root, filename_ann)) == 0:
                mark = 0
                mode = "w"
            else:
                with open(os.path.join(root,filename_ann),"r") as file:
                    lines = file.readlines()
                    if lines:
                        # Get marks
                        marks = list(map(lambda x: int(x.split('\t')[0][1:]),
                                         filter(lambda x: x[0] == 'T', lines)))
                    
                        # 2. Get highest mark
                        mark = max(marks)
                    else:
                        # 2. Get last mark
                        mark = 0
                mode = "a"
           
            # 2. Write new annotationsgit 
            new_annotations = new_annots[filename]
            with open(os.path.join(root,filename_ann),mode) as file:
                for a in new_annotations:
                    mark = mark + 1
                    file.write('T' + str(mark) + '\t' + '_SUG_' +  a[0] + 
                               ' ' + str(a[1]) + ' ' + str(a[2]) + 
                               '\t' + a[3] + '\n') 
                    if with_notes == False:
                        continue
                    file.write('#' + str(mark) + '\t' + 'AnnotatorNotes' +
                               ' T' + str(mark) + '\t' + a[4] + '\n')  
                            
def get_highest_mark_ann(r, filename):
    '''
    Get highest mark in ANN file
    Parameters
    ----------
    r: str.
        Directory where file is
    filename: str. 
        
    Returns
    ----------
    mark: int
    '''
    with open(os.path.join(r,filename),"r") as file:
        lines = file.readlines()
        if not lines: 
            return 0
        # Get marks
        marks = list(map(lambda x: int(x.split('\t')[0][1:]), 
                         filter(lambda x: x[0] == 'T', lines)))
        # 2. Get highest mark
        mark = max(marks)
    return mark

def copy_dir_structure(datapath, output_path_new_files):
    '''
    DESCRIPTION: copy folders structure in a new route.
    From https://stackoverflow.com/a/40829525
            
    Parameters
    ----------
    datapath: str.
        Directory whose structure I want to replicate
    output_path_new_files: str. 
        Root directory on which I want to re-create the sub-folder structure.
    '''
    for dirpath, dirnames, filenames in os.walk(datapath):
        structure = os.path.join(output_path_new_files, dirpath[len(datapath):])
        print(structure)
        if not os.path.isdir(structure):
            os.mkdir(structure)
        else:
            print("Folder does already exist!")
            
def copy_all_files(datapath, output_path_new_files):
    '''
    DESCRIPTION: copy files from one directory to another. It respects folder 
        structure. 
        
    Parameters
    ----------
    datapath: str.
        Source directory.
    output_path_new_files: str. 
        Target directory.
    '''
    for root, dirs, files in os.walk(datapath):
        for filename in files:
            copyfile(os.path.join(root,filename), 
                     os.path.join(output_path_new_files, root[len(datapath):],
                                  filename))

def remove_redundant_suggestions(datapath):
    '''
    DESCRIPTION: 
    Parameters
    ----------
    datapath : str
        path to folder where Brat files are.
    Returns
    -------
    c : int
        Number of removed suggestions.
    '''
    c = 0
    for root, dirs, files in os.walk(datapath):
        for filename in files:
            if filename[-3:]!= 'ann':
                continue
            # get only ann files
            f = open(os.path.join(root,filename)).readlines()
            offsets = []
            to_delete = []
            
            # 1. Get position of confirmed annotations
            for line in f:
                if (line[0] != 'T') | (line.split('\t')[1][0:5] == '_SUG_'):
                    continue
                splitted = line.split('\t')
                label_offset = splitted[1].split(' ')
                if ';' in label_offset[1:][1]:
                    continue # Do not store discontinuous annotations
                offsets.append([label_offset[0], int(label_offset[1:][0]),
                                int(label_offset[1:][1]), splitted[0]])
                        
            # 2.1 Get position of suggestions.
            # 2.2 Check suggestions are not contained in any confirmed annotation
            # (with the same label)
            offsets_sug = []
            for line in f:
                if (line[0] != 'T') | (line.split('\t')[1][0:5] != '_SUG_'):
                    continue
                splitted = line.split('\t')
                label_offset = splitted[1].split(' ')
                new_offset = [label_offset[0], int(label_offset[1:][0]), 
                              int(label_offset[1:][1]), splitted[0]]
                offsets_sug.append(new_offset)
                if any(map(lambda x: ((x[0] == new_offset[0][5:]) & # same label
                                      (x[1] <= new_offset[1]) & # contained
                                      (x[2] >= new_offset[2])), offsets)): # contained
                    to_delete.append(splitted[0])
                    c = c +1
               
            # 3. Check suggestions are not contained in any other suggestion
            # (with the same label)!!!!
            for sug, idx in zip(offsets_sug,range(len(offsets_sug))):
                # Get list with all offsets_sug except the current one
                offsets_sug_subs = offsets_sug[:idx] + offsets_sug[idx+1:]
                
                if any(map(lambda x: ((x[0] == sug[0]) & # same label
                                      (x[1] <= sug[1]) & # contained
                                      (x[2] >= sug[2])), offsets_sug_subs)): # contained
                    to_delete.append(sug[3])
                    c = c + 1
                pass
                
            # 4. Re-write ann without suggestions that were contained in a
            # confirmed annotation
            with open(os.path.join(root,filename), 'w') as fout:
                for line in f:
                    if line.split('\t')[0] in to_delete:
                        continue
                    fout.write(line)
    return c