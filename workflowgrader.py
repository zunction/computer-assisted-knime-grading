import knime
import pandas as pd
import numpy as np
import os
import argparse
import tqdm

args.model_workflow
args.executable_path

def parse_args():
    parser = argparse.ArgumentParser(description='Grades KNIME workflows.')
    parser.add_argument('--exec-path',type='str', help='not required unless KNIME is installed in non-standard location.')
    parser.add_argument('--ref-workflow',default='C5_Lab5_Task1_Data_prep_clean_with_COT',type='str',help='path to the workflow which is the grading is based on.')
    parser.add_argument('--grading-workspace',default='C:\Users\s11006381\knime-workspace\gradespace',type='str',help='workspace with workflows to be graded.')
    parser.add_argument('--grading-results', default='C:\Users\s11006381\Desktop',type='str',help='location to save the results of the graded workflows.')
   
    args = parser.parse_args()
    
    return args

def main():
    args = parse_args()

    