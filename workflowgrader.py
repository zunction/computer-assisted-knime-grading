import knime
import pandas as pd
import numpy as np
import os
import argparse
from datetime import datetime
from utils import workflowgrader
import time
import sys, traceback, logging


def parse_args():
    parser = argparse.ArgumentParser(description='Grades KNIME workflows.')
    parser.add_argument('workspace', help='KNIME workspace with the workflows to be graded.')
    parser.add_argument('ref_workflow', help='Name of the reference workflow to be used.')
    # parser.add_argument('-c','--classes', default=None, nargs='*', help='classes to be graded in the workspace')
    parser.add_argument('--exec-path', default=None, help='Not required unless KNIME is installed in non-standard location.')
    # parser.add_argument('--workspace',required=True, help='KNIME workspace with the workflows to be graded.')
    # parser.add_argument('--ref-workflow',required=True, help='Name of the reference workflow to be used.')
    parser.add_argument('--save-name',default=None ,help='Name of grading results to be saved as.')
    parser.add_argument('--save-dir',default=None, help='Directory to save the grading results to. Saved to workspace if not provided.')
   
    args = parser.parse_args()
    
    return args

def current_datetime():
    now = datetime.now()
    return now.strftime('%d-%m-%Y'), now.strftime('%H:%M:%S')

def detect_workflowset(workspace):
    """
    Scans for workflowsets (folders containing workflow) in the give knime workspace. 
    Returns a (possibly empty) list of fullpaths to the detected workflowsets.
    """
    fullpath_workflowsets = []

    for i in os.listdir(workspace):
        if os.path.isdir(os.path.join(workspace,i)) and i != 'Example Workflows':
            wfs = os.path.exists(os.path.join(os.path.join(workspace,i),'workflowset.meta'))
            wfsvg = os.path.exists(os.path.join(os.path.join(workspace,i),'workflow.svg'))
            if  wfs and not wfsvg:
                print('detected {} workflowset'.format(i.upper()))
                fullpath_workflowsets.append(os.path.join(workspace,i))

    return fullpath_workflowsets

def process_workflowset(workflowset):
    


def main():
    args = parse_args()

    if not args.save_name:
        args.save_name = os.path.basename(args.workspace)
    if not args.save_dir:
        args.save_dir = args.workspace

    logging.basicConfig(filename=os.path.join(args.save_dir,args.save_name+'.log'), filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    # print('\n {} {} - Start initialisation of workflowgrader:'.format(*current_datetime()))
    print('\n')
    print('  KNIME WORKSPACE   : {}'.format(args.workspace))
    print('  REFERENCE WORKFLOW: {}'.format(args.ref_workflow))
    
    print('\n  {} {} - Initialising workflowgrader...'.format(*current_datetime()))
    # print('\n {} {} - Start initialisation of workflowgrader:'.format(*current_datetime()))
    wfg = workflowgrader(args.workspace,args.ref_workflow, args.exec_path)

    fullpath_workflowsets = detect_workflowset(args.workspace)

    
    print('\n  {} {} - Extract nodes used in the submitted workflows'.format(*current_datetime()))
    _ = wfg.accumulate_workflow_nodes()

    print('\n  {} {} - Extract data outputs of the submitted workflows'.format(*current_datetime()))
    _, _ = wfg.accumulate_workflow_outputs()

    print('\n  {} {} - Examine submitted questions'.format(*current_datetime()))
    _ = wfg.check_question()

    print('\n  {} {} - Examine variables of the outputs'.format(*current_datetime()))
    _ = wfg.check_variable()

    print('\n  {} {} - Examine data of the outputs'.format(*current_datetime()))
    _ = wfg.check_data()

    # if not args.save_name:
    #     args.save_name = os.path.basename(args.workspace)

    args.save_name = args.save_name+'.csv'

    wfg.generate_csv(save_dir=args.save_dir, save_as=args.save_name)
    print('\n  {} {} - Results {} is saved at {}'.format(*current_datetime(),args.save_name,args.save_dir))


    # if not args.save_dir:
    #     wfg.generate_csv(save_dir=args.workspace, save_as=args.save_name)
    #     print('\n {} {} - Results {} is saved at {}'.format(*current_datetime(),args.save_name,args.workspace))
    # else:
    #     wfg.generate_csv(save_dir=args.save_dir, save_as=args.save_name)
    #     print('\n {} {} - Results {} is saved at {}'.format(*current_datetime(),args.save_name,args.save_dir))

    print('\n  A total {} workflows were graded in {} seconds'.format(len(wfg),round(time.time() - start_time,0))) 

if __name__ == '__main__':
    start_time = time.time()
    main()    
