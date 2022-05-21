import knime
import pandas as pd
import numpy as np
import os
import argparse
from datetime import datetime
from utils import workflowgrader


def parse_args():
    parser = argparse.ArgumentParser(description='Grades KNIME workflows.')
    parser.add_argument('--exec-path', default=None, help='Not required unless KNIME is installed in non-standard location.')
    parser.add_argument('--workspace', help='KNIME workspace with the workflows to be graded.')
    parser.add_argument('--ref-workflow', help='Name of the reference workflow to be used.')
    parser.add_argument('--save-name',default='out' ,help='Name of grading results to be saved as.')
    parser.add_argument('--save-dir',default=None, help='Directory to save the grading results to. Saved to workspace if not provided.')
   
    args = parser.parse_args()
    
    return args

def main():
    args = parse_args()

    print('Initialising workflowgrader...')
    wfg = workflowgrader(args.workspace,args.ref_workflow, args.exec_path)
    
    print('\n Collecting nodes used in the submitted workflows...')
    _ = wfg.accumulate_workflow_nodes()

    print('\n Collecting data outputs of the submitted workflows...')
    _, _ = wfg.accumulate_workflow_outputs()

    print('\n Checking submitted questions...')
    _ = wfg.check_question()

    print('\n Checking variables of the outputs...')
    _ = wfg.check_variable()

    print('\n Checking data of the outputs...')
    _ = wfg.check_data()

    args.save_name = args.save_name+'.csv'

    if not args.save_dir:
        wfg.generate_csv(save_dir=args.workspace, save_as=args.save_name)
        print('\n Grading results {} is saved at {}'.format(args.save_name,args.workspace))
    else:
        wfg.generate_csv(save_dir=args.save_dir, save_as=args.save_name)
        print('\n Grading results {} is saved at {}'.format(args.save_name,args.save_dir))

if __name__ == '__main__':
    main()    