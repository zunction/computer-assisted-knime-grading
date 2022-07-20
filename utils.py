import knime
import pandas as pd
import numpy as np
from pathlib import Path
import os, re
import glob
from tqdm import tqdm
import xml.etree.ElementTree as ET
import sys, traceback, logging
from datetime import datetime
import itertools


def display_process_start(verbose):
    print('  {} {} - {}'.format(*current_datetime(),verbose))

def display_process_output(verbose):
    print('      -> {}'.format(verbose))

def current_datetime():
    now = datetime.now()
    return now.strftime('%d-%m-%Y'), now.strftime('%H:%M:%S')

def collect_workflow_nodes(path_to_knime_workflow):
    """
    Collect the list of nodes of the workflow in the provided path to a KNIME workflow.
    Returns a dictionary which describes the count of the various nodes in the workflow.

    """
    nodes = []
    for settings_filepath in Path(path_to_knime_workflow).glob("*/settings.xml"):
        node = re.split('[\(\)]',os.path.basename(settings_filepath.parent))[0].strip()
        nodes.append(node)    

    return dict(zip(*np.unique(nodes,return_counts=True)))

def collect_workflow_outputs(path_to_knime_workflow, exec_path = None):
    """
    Collect all the outputs of the workflow in the provided path to a KNIME workflow.
    Returns a dictionary where (key,value) = (node annotation,output table)
    """
    if not None:
        wf = knime.Workflow(path_to_knime_workflow)
        wf.execute()        
    else:
        knime.executable_path = exec_path
        wf = knime.Workflow(path_to_knime_workflow)
        wf.execute()
    if all([e == None for e in wf.COT_annotation]):
        return dict(zip(list(range(len(wf.COT_annotation))),wf.data_table_outputs)), wf.file_reader_data_path
    else:
        return dict(zip(wf.COT_annotation,wf.data_table_outputs)), wf.file_reader_data_path
  
def compare_COT_annotation(d1,d2):
    """
    Compares the annotation of the COT nodes based on the dictionaries 
    from `collect_workflow_outputs`. The dictionary d1 is the reference
    which d2 is compared against. 
    
    Note that this function does not commutes.
    
    Args:
        d1, d2: dictionaries of form {node_annotation: dataframe_from_COT}.
    Returns:
        missing_ann: list of annotations of d1 which are not in d2.
        foreign_ann: list of annotations of d2 which are not in d1.
    """
    foreign_ann = []
    missing_ann = []
    for k in d1:
        if k not in list(d2.keys()):
            missing_ann.append(k)
    for k in d2:
        if k not in list(d1.keys()):
            foreign_ann.append(k)
    return missing_ann, foreign_ann    

def assisted_question_inference(d, missing, foreign):
        """
        Performed assisted question inference when the both missing 
        and foreign questions are exactly one. When len(missing) and 
        len(foreign) are both 1, performs automatic update of the 
        dictionary key from the question observed in foreign to the 
        one observed in missing.
        
        Args:
            d: the dictionary of outputs with the form 
                {node_annotation: dataframe_from_COT}.
            missing: the list of missing questions from the submission
            foreign: the list of foreign questions observed in the submission
        Returns:
            feedback: computer generated qualitative feedback for the student
        """
        if len(missing) == 1 and len(foreign) == 1:
            d[missing[0]] = d[foreign[0]]
            del d[foreign[0]]
        
def move_col_to_front(df, suffix='_summary'):
    """
    Move columns in a dataframe with a given suffix to the 
    left of a dataframe.    
    """
    move_col = []
    for c in df.columns:
        if suffix in c:
            move_col.append(c)
    move_col.reverse()
    for c in move_col:
        first_column = df.pop(c)
        df.insert(0, c, first_column)

class workflowgrader():
    """
    
    """
    def __init__(self, workspace, ref_workflow, exec_path, workflowsets):
        # directory with the workflows to be graded    
        self.workspace = workspace
        # workflow to be used as a reference for grading
        self.ref_workflow = ref_workflow
        # fullpaths of workflowsets to iterate, if None, fullpath to workspace is provided
        # self.fullpath_workflowsets = [workspace] if not workflowsets else [os.path.join(workspace,i) for i in workflowsets]
        self.fullpath_workflowsets = [os.path.join(workspace,i) for i in workflowsets]

        # assume that workflows are named using student ids
        self.student_ids = {}

        # knime executable path
        self.exec_path = exec_path

        # list of fullpaths to folders with workflows
        # self.workflowsets = workflowsets
        self.workflowsets = [os.path.basename(workspace)] if not workflowsets else workflowsets

        # reference based on reference workflow
        self.ref_output, _ = collect_workflow_outputs(os.path.join(workspace,ref_workflow))
        self.ref_node_dist = collect_workflow_nodes(os.path.join(workspace,ref_workflow))
        self.question_keys = self.ref_output.keys()
        
        # outputs from submissions
        self.sub_outputs = {}
        self.sub_node_dists = {}
        self.sub_data_paths = {}

        # missing and foreign questions
        self.check_question_results = {}
   
        # missing and foreign variables
        self.check_var_results = {}
        # incorrect datatypes
        self.check_data_results = {}


    def __len__(self):
        """
        Returns the number of workflows that are graded in the workflowgrader.
        """
        return sum(len(workflowset) for workflowset in self.sub_outputs.values() )

    def cmp_var_dtype(self, workflowset, s, q, v):
        """
        Comparison of the variable datatype for question q and variable v of
        sub_outputs by submission s to ref_output to return a boolean value.
        """
        return self.ref_output[q][v].dtype == self.sub_outputs[workflowset][s][q][v].dtype

    def cmp_var_data(self, workflowset, s, q, v):
        """
        Comparison of the variable data for question q and variable v of
        sub_outputs by submission s to ref_output using pandas .equals 
        function to return a boolean value.
        """
        return self.ref_output[q][v].equals(self.sub_outputs[workflowset][s][q][v])

    def extract_workflow_data(self, workflowset):
        """
        Extracts node, output and data path information from the workflows
        found in the workflowset.
        """
        nodes = []
        sub_outputs = []
        data_paths = []
        student_ids = []
        # fullpath_workflowset = os.path.join(self.workspace,workflowset)

        if (len(self.workflowsets) == 1) and os.path.basename(self.workspace) == self.workflowsets[0]:
            fullpath_workflowset = self.workspace
        else:
            fullpath_workflowset = os.path.join(self.workspace,workflowset)

        progress = tqdm(glob.glob(os.path.join(fullpath_workflowset,'[ab0-9]*')), ascii=' >=')
        for wfp in progress:
            progress.set_description('    Extracting data from {}'.format(os.path.basename(wfp)+'.knwf'))
            student_ids.append(os.path.basename(wfp))
            
            # extraction of node information
            d = collect_workflow_nodes(wfp)
            # compare keys and create missing keys
            for k in self.ref_node_dist.keys():
                if k not in d.keys():
                    d[k] = 0
            nodes.append(d)

            # extraction of output and data path information
            try:
                sub_output, data_path = collect_workflow_outputs(wfp,self.exec_path)
                sub_outputs.append(sub_output)
                data_paths.append(data_path)
            except:
                logging.exception('Error encountered with {}'.format(wfp))
                sub_outputs.append({})
                data_paths.append('')

        self.student_ids[workflowset] = student_ids
        self.sub_node_dists[workflowset] = dict(zip(student_ids,nodes))
        self.sub_outputs[workflowset] = dict(zip(student_ids,sub_outputs))
        self.sub_data_paths[workflowset] = dict(zip(student_ids,data_paths))
        
    def check_question_by_workflowset(self, workflowset):
        """
        Checks the questions submitted by students based on the 
        annotations and outputs generated by `collect_workflow_outputs`.
        Checks are made with respect to self.ref_output.
            
        Returns:
            self.question_check_results : a dictionary of form {student_id: (missing, foreign)}
            self.question_sub_feedbacks : a dictionary of form {student_id: *feedback*}
        """

        try:
            self.sub_outputs[workflowset].keys()
        except:
            print("Need to accumulate workflow outputs with `accumulate_workflow_outputs` first.")
        question_check_results = []
        
        progress = tqdm(self.student_ids[workflowset], ascii=True)
        for s in progress:
            progress.set_description('    Checking outputs from {}'.format(s+'.knwf'))
            missingq, foreignq = compare_COT_annotation(self.ref_output,self.sub_outputs[workflowset][s])
            feedback = assisted_question_inference(self.sub_outputs[workflowset][s], missingq, foreignq)
            
            question_check_results.append(compare_COT_annotation(self.ref_output,self.sub_outputs[workflowset][s]))
       
        self.check_question_results[workflowset] = dict(zip(self.student_ids[workflowset],question_check_results))

    def check_variable_and_data_by_workflowset(self,workflowset):
        """
        Returns self.var_check_results dictionary with the format

            {'q1': {'stu1': (a11,b11), 'stu2': (a12,b12)}, 'q2': {'stu1': (a21,b21), 'stu2': (a22,b2)}}
        
        where
            aij: list of missing variables in student j submission of question i
            bij: list of 2-tuple with form (variable_name, obs_var)
        
        when question i is not submitted by student j, (aij, bij) = 'UNGRADED'


        self.var_check_results can be converted to a pandas dataframe with `pd.Dataframe.from_dict()`.
        """

        var_check_results = []
        data_check_results = []
        # for question q 
        q_progress = tqdm(self.ref_output.keys(), ascii=True)
        for q in q_progress:
        # for q in self.ref_output.keys():
            var_check_result = []
            data_check_result = []

            for s in self.student_ids[workflowset]:
                q_progress.set_description('    Checking data from {}'.format(s+'.knwf'))
                missing_vars = []
                incorrect_var_dtype = []
                incorrect_var_data = []

                try:
                    # check if student s has question q
                    self.sub_outputs[workflowset][s][q]
                except:
                    # if not we label it as ungraded and move on to the next student
                    missing_vars = ['UNGRADED']
                    incorrect_var_dtype = ['UNGRADED']
                    var_check_result.append((missing_vars,incorrect_var_dtype))

                    incorrect_var_data = ['UNGRADED']
                    data_check_result.append(incorrect_var_data)
                    
                    continue
                # when question q is available iterate over target variables and target dtypes
                for tar_var, tar_dtype in zip(self.ref_output[q].columns,self.ref_output[q].dtypes):
                    try:
                        # check if variable dtype can be accessed and equal to target variable dtype

                        if not self.cmp_var_dtype(workflowset, s, q, tar_var):
                            incorrect_var_dtype.append((tar_var,self.sub_outputs[workflowset][s][q][tar_var].dtype))

                    except:
                        # if variable dtype cannot be accessed, variable is taken to be missing
                        missing_vars.append(tar_var)
                
                var_check_result.append((missing_vars,incorrect_var_dtype))  
                
                for tar_var in self.ref_output[q].columns:
                    try:
                        if not self.cmp_var_data(workflowset, s, q, tar_var):
                            incorrect_var_data.append(tar_var)
                    except:
                        continue
                data_check_result.append(incorrect_var_data)


            var_check_results.append(dict(zip(self.student_ids[workflowset],var_check_result)))
            data_check_results.append(dict(zip(self.student_ids[workflowset],data_check_result)))
      
        self.check_var_results[workflowset] = dict(zip(self.ref_output.keys(),var_check_results))
        self.check_data_results[workflowset] = dict(zip(self.ref_output.keys(),data_check_results))

    def generate_csv_by_workflowset(self, workflowset, save_dir):
        """
        Processes the data collected into a single pandas dataframe.
        """
        # filepath df
        fp_df = pd.Series(self.sub_data_paths[workflowset],name='data_filepaths')

        # check question df
        cqr_df = pd.DataFrame.from_dict(self.check_question_results[workflowset],orient='index',columns=['missing_questions','foreign_questions'])
        cqr_df['question_summary'] = cqr_df['missing_questions'].apply(lambda x : 1-(len(x)/len(self.ref_output.keys())))

        # check variables df
        cvr_df = pd.DataFrame.from_dict(self.check_var_results[workflowset])
        # print(cvr_df)
        for i in cvr_df.columns:
            cvr_df[i+'_var_summary'] = cvr_df[i].apply(lambda x : 1-(len(x[0])/len(self.ref_output[i].columns)) if 'UNGRADED' not in x[0] else x[0][0])
            cvr_df[i+'_dtype_summary'] = cvr_df[i].apply(lambda x : 1-(len(x[0])/len(self.ref_output[i].columns)) if 'UNGRADED' not in x[0] else x[0][0])
            cvr_df[[i+'_missing_var',i+'_incorrect_var_dtype']] = pd.DataFrame(cvr_df[i].to_list(),index=cvr_df.index)
            del cvr_df[i] 

        # check data df
        cdr_df = pd.DataFrame.from_dict(self.check_data_results[workflowset])
        for i in cdr_df.columns:
            cdr_df[i+'_data_summary'] = cdr_df[i].apply(lambda x : 1-(len(x)/len(self.ref_output[i].columns)) if x!=['UNGRADED'] else x[0])
            cdr_df[i+'_incorrect_var_values'] = cdr_df[i]
            del cdr_df[i] 

        # node distribution df
        n_df = pd.DataFrame.from_dict(self.sub_node_dists[workflowset],orient='index')
        n_df['node_count'] = n_df.sum(axis=1)
        n_df['node_summary'] = n_df['node_count']/sum(self.ref_node_dist.values())


        # combined df
        combined_df = pd.merge(cqr_df,cvr_df,left_index=True,right_index=True)
        combined_df = pd.merge(combined_df,cdr_df,left_index=True,right_index=True,suffixes=('_var_dtype','_data'))
        combined_df = pd.merge(combined_df,n_df,left_index=True,right_index=True,suffixes=('_var_dtype','_data'))
        combined_df = pd.merge(combined_df,fp_df,left_index=True,right_index=True)

        # move columns
        move_col_to_front(combined_df)
        combined_df.reset_index(inplace=True)

        # saving dataframe to csv file 
        combined_df.to_csv(os.path.join(save_dir,workflowset+'.csv'))

        display_process_output('{} is saved at {}'.format(workflowset+'.csv',save_dir))







