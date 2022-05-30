import knime
import pandas as pd
import numpy as np
import os
import argparse
from datetime import datetime
from utils import workflowgrader
import time


def parse_args():
    parser = argparse.ArgumentParser(description='Grades KNIME workflows.')
    parser.add_argument('--exec-path', default=None, help='Not required unless KNIME is installed in non-standard location.')
    parser.add_argument('--workspace',required=True, help='KNIME workspace with the workflows to be graded.')
    parser.add_argument('--ref-workflow',required=True, help='Name of the reference workflow to be used.')
    parser.add_argument('--save-name',default=None ,help='Name of grading results to be saved as.')
    parser.add_argument('--save-dir',default=None, help='Directory to save the grading results to. Saved to workspace if not provided.')
   
    args = parser.parse_args()
    
    return args

def current_datetime():
    now = datetime.now()
    return now.strftime('%d-%m-%Y'), now.strftime('%H:%M:%S')

def main():
    args = parse_args()


    print('\n {} {} - Start initialisation of workflowgrader:'.format(*current_datetime()))
    print('  Workspace         : {}'.format(args.workspace))
    print('  Reference workflow: {}'.format(args.ref_workflow))
    wfg = workflowgrader(args.workspace,args.ref_workflow, args.exec_path)
    
    print('\n {} {} - Collect nodes used in the submitted workflows'.format(*current_datetime()))
    _ = wfg.accumulate_workflow_nodes()

    print('\n {} {} - Collect data outputs of the submitted workflows'.format(*current_datetime()))
    _, _ = wfg.accumulate_workflow_outputs()

    print('\n {} {} - Check submitted questions'.format(*current_datetime()))
    _ = wfg.check_question()

    print('\n {} {} - Check variables of the outputs'.format(*current_datetime()))
    _ = wfg.check_variable()

    print('\n {} {} - Check data of the outputs'.format(*current_datetime()))
    _ = wfg.check_data()

    if not args.save_name:
        args.save_name = os.path.basename(args.workspace)

    args.save_name = args.save_name+'.csv'

    if not args.save_dir:
        wfg.generate_csv(save_dir=args.workspace, save_as=args.save_name)
        print('\n {} {} - Results {} is saved at {}'.format(*current_datetime(),args.save_name,args.workspace))
    else:
        wfg.generate_csv(save_dir=args.save_dir, save_as=args.save_name)
        print('\n {} {} - Results {} is saved at {}'.format(*current_datetime(),args.save_name,args.save_dir))

    print('\n A total {} workflows were graded in {} seconds'.format(len(wfg),round(time.time() - start_time,0))) 

if __name__ == '__main__':
    start_time = time.time()
    main()    
