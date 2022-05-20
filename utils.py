import knime
import pandas as pd
import numpy as np
from pathlib import Path
import os, re
import glob
from tqdm import tqdm
import xml.etree.ElementTree as ET


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

def collect_workflow_outputs(path_to_knime_workflow):
    """
    Collect all the outputs of the workflow in the provided path to a KNIME workflow.
    Returns a dictionary where (key,value) = (node annotation,output table)
    """
    wf = knime.Workflow(path_to_knime_workflow)
    wf.execute()

    # to extract file reader data path at in this function
    # wf.file_reader_data_path
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
        if not (k in list(d2.keys())):
            missing_ann.append(k)
    for k in d2:
        if not (k in list(d1.keys())):
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
        

class workflowgrader():
    """
    
    """
    def __init__(self, gradespace, ref_workflow):
        # directory with the workflows to be graded    
        self.gradespace = gradespace
        # workflow to be used as a reference for grading
        self.ref_workflow = ref_workflow
        # retrieve abspath of workflows to be graded
        self.sub_workflows = \
        glob.glob(os.path.join(gradespace,'[0-9]*'))
        # assume that workflows are named using student ids
        self.student_ids = [os.path.basename(p) for p in self.sub_workflows]

        # reference based on reference workflow
        self.ref_output, _ = collect_workflow_outputs(os.path.join(gradespace,ref_workflow))
        self.ref_node_dist = collect_workflow_nodes(os.path.join(gradespace,ref_workflow))
        self.question_keys = self.ref_output.keys()
        
        # outputs from submissions
        self.sub_outputs = None
        self.sub_node_dists = None
        self.sub_data_paths = None

        # missing and foreign questions
        self.check_question_results = None
        # feedbacks for questions
        # self.question_sub_feedbacks = None

        # missing and foreign variables
        self.check_var_results = None
        # incorrect datatypes
        self.check_data_results = None


    def __len__(self):
        """
        Returns the number of workflows that are graded in the workflowgrader.
        """
        return len(self.sub_outputs)

    def cmp_var_dtype(self, s, q, v):
        """
        
        """
        return self.ref_output[q][v].dtype == self.sub_outputs[s][q][v].dtype

    def cmp_var_data(self, s, q, v):
        """

        """
        return self.ref_output[q][v].equals(self.sub_outputs[s][q][v])

    
    def accumulate_workflow_nodes(self):
        """

        """

        nodes = []

        for wfp in tqdm(self.sub_workflows):
            d = collect_workflow_nodes(wfp)
            # compare keys and create missing keys
            for k in self.ref_node_dist.keys():
                if k not in d.keys():
                    d[k] = 0
            nodes.append(d)
            # nodes_in_workflow = collect_workflow_nodes(wfp)
        self.sub_node_dists = dict(zip(self.student_ids,nodes))
        return self.sub_node_dists


    def accumulate_workflow_outputs(self):
        """
        Accumulates the outputs from the workflows in gradspace.
        
        Args:
            Nil
        Returns:
            self.sub_outputs: a dictionary of submitted outputs of the form {student_id : workflow_output}.
        
        """
        
        sub_outputs = []
        data_paths = []

        for wfp in tqdm(self.sub_workflows):
            sub_output, data_path = collect_workflow_outputs(wfp)
            sub_outputs.append(sub_output)
            data_paths.append(data_path)
        
        self.sub_outputs = dict(zip(self.student_ids,sub_outputs))
        self.sub_data_paths = dict(zip(self.student_ids,data_paths))
        return self.sub_outputs, self.sub_data_paths
    
    def check_question(self):
        """
        Checks the questions submitted by students based on the 
        annotations and outputs generated by `collect_workflow_outputs`.
        Checks are made with respect to self.ref_output.
            
        Returns:
            self.question_check_results : a dictionary of form {student_id: (missing, foreign)}
            self.question_sub_feedbacks : a dictionary of form {student_id: *feedback*}
        """
        try:
            self.sub_outputs.keys()
        except:
            print("Need to accumulate workflow outputs with `accumulate_workflow_outputs` first.")
        question_check_results = []
        
        for s in tqdm(self.student_ids):
            missingq, foreignq = compare_COT_annotation(self.ref_output,self.sub_outputs[s])
            feedback = assisted_question_inference(self.sub_outputs[s], missingq, foreignq)
            
            question_check_results.append(compare_COT_annotation(self.ref_output,self.sub_outputs[s]))
            # question_sub_feedbacks.append(feedback)
        
        self.check_question_results = dict(zip(self.student_ids,question_check_results))
        # self.question_sub_feedbacks = dict(zip(self.student_ids,question_sub_feedbacks))
        
        return self.check_question_results
    
    def check_variable(self):
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
        
        # for question q 
        for q in tqdm(self.ref_output.keys()):
            
            var_check_result = []

            # for student s
            for s in self.student_ids:

                missing_vars = []
                incorrect_var_dtype = []
                # incorrect_var_data = []

                try:
                    # check if student s has question q
                    self.sub_outputs[s][q]
                except:
                    # if not we label it as ungraded and move on to the next student
                    missing_vars = ['UNGRADED']
                    incorrect_var_dtype = ['UNGRADED']
                    var_check_result.append((missing_vars,incorrect_var_dtype))
                    
                    continue
                # when question q is available iterate over target variables and target dtypes
                for tar_var, tar_dtype in zip(self.ref_output[q].columns,self.ref_output[q].dtypes):
                    try:
                        # check if variable dtype can be accessed and equal to target variable dtype

                        if not self.cmp_var_dtype(s, q, tar_var):
                            incorrect_var_dtype.append((tar_var,self.sub_outputs[s][q][tar_var].dtype))

                    except:
                        # if variable dtype cannot be accessed, variable is taken to be missing
                        missing_vars.append(tar_var)
                
                var_check_result.append((missing_vars,incorrect_var_dtype))

            var_check_results.append(dict(zip(self.student_ids,var_check_result)))
        
        self.check_var_results = dict(zip(self.ref_output.keys(),var_check_results))
        return self.check_var_results

    def check_data(self):
        """
        
        """

        data_check_results = []

        for q in tqdm(self.ref_output.keys()):
            data_check_result = []

            for s in self.student_ids:

                incorrect_var_data = []

                try:
                    self.sub_outputs[s][q]
                except:
                    data_check_result.append('UNGRADED')
                    continue
                
                for tar_var in self.ref_output[q].columns:
                    try:
                        if not self.cmp_var_data(s, q, tar_var):
                            incorrect_var_data.append(tar_var)
                    except:
                        continue
                data_check_result.append(incorrect_var_data)
            data_check_results.append(dict(zip(self.student_ids,data_check_result)))
        self.check_data_results = dict(zip(self.ref_output.keys(),data_check_results))
        return self.check_data_results

    def generate_csv(self):
        """

        """
        # file path dataframe
        fp_df = pd.DataFrame.from_dict(wfg.sub_data_paths, orient='index')

        # check question dataframe
        cqr_df = pd.DataFrame.from_dict(cqr,orient='index',columns=['missing_questions','foreign_questions'])
        cqr_df['question_completion'] = cqr_df['missing_questions'].apply(lambda x : 1-(len(x)/len(wfg.ref_output.keys())))

        # check variable dataframe
        cvr_df = pd.DataFrame.from_dict(cvr)
        for i in cvr_df.columns:
            cvr_df[[i+'_missing_var',i+'_incorrect_var_dtype']] = pd.DataFrame(cvr_df[i].to_list(),index=cvr_df.index)
            del cvr_df[i]
        

        
        # check data dataframe
        cdr_df = pd.DataFrame.from_dict(cdr)
        for i in cdr_df.columns:
            cdr_df[i+'_incorrect_var_data'] = cdr_df[i]
            del cdr_df[i]
        
        # node distribution dataframe
        n_df = pd.DataFrame.from_dict(wfg.sub_node_dists,orient='index')
        n_df['total_node_count'] = n_df.sum(axis=1)







