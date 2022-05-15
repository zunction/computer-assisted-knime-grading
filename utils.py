import knime
import pandas as pd
import numpy as np
import os
import glob
from tqdm import tqdm
import xml.etree.ElementTree as ET


def collect_workflow_outputs(path_to_knime_workflow):
    """
    Collect all the outputs of the workflow in the provided path to a KNIME workflow.
    Returns a dictionary where (key,value) = (node annotation,output table)
    """
    wf = knime.Workflow(path_to_knime_workflow)
    wf.execute()
    return dict(zip(wf.COT_annotation,wf.data_table_outputs))

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
        
        # to generate feedbacks later
        #     feedback = "Expected question {} is missing but received foreign {} instead. Answer for foreign question is inferred as answer for missing question.".format(missing,foreign)
        # else:
        #     feedback = "Expected questions {} are missing but received {} instead".format(missing,foreign)
        # return feedback

# def compare_df_varnames(df1, df2):
#     """
#     Compares the variable names of the dataframes.
#     The dataframe df1 is the reference which df2 is compared against. 
    
#     Note that this function does not commutes.

#     Args:
#         df1, df2: dataframes extracted from COT nodes.
#     Returns:
#         missing_vars: list of variable names which are in df1 but not in df2.
#         matched_vars: list of variable names which are in df1 and also in df2.
        
#     """
#     df1_col = df1.columns
#     df2_col = df2.columns
#     missing_vars = []
#     foreign_vars = []
#     for varname in df1_col:
#         if not (varname in df2_col):
#             missing_vars.append(varname)
#     for varname in df2_col:
#         if not (varname in df1_col):
#             foreign_vars.append(varname)
#     return missing_vars, foreign_vars


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
        self.ref_output = collect_workflow_outputs(os.path.join(gradespace,ref_workflow))
        self.question_keys = self.ref_output.keys()
        
        # outputs from submissions
        self.sub_outputs = None

        # missing and foreign questions
        self.check_question_results = None
        # feedbacks for questions
        # self.question_sub_feedbacks = None

        # missing and foreign variables
        self.check_var_results = None
        # incorrect datatypes
        
    def __len__(self):
        """
        Returns the number of 
        """
        return len(self.sub_outputs)
    
    def accumulate_workflow_outputs(self):
        """
        Accumulates the outputs from the workflows in gradspace.
        
        Args:
            Nil
        Returns:
            self.sub_outputs: a dictionary of submitted outputs of the form {student_id : workflow_output}.
        
        """
        
        sub_outputs = []

        for wfp in tqdm(self.sub_workflows):
            sub_outputs.append(collect_workflow_outputs(wfp))
        
        self.sub_outputs = dict(zip(self.student_ids,sub_outputs))
        
        return self.sub_outputs
    
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
            bij: list of 3-tuple with form (variable_name, tar_var, obs_var)
        
        self.var_check_results can be converted to a pandas dataframe with `pd.Dataframe.from_dict()`.
        """
        var_check_results = []
        
        # for question q 
        for q in tqdm(self.ref_output.keys()):
            # print(q)
            
            var_check_result = []

            # for student s
            for s in self.student_ids:
                # print(s)

                missing_vars = []
                incorrect_dtype_vars = []

                try:
                    self.sub_outputs[s][q]
                except:
                    missing_vars = None
                    incorrect_dtype_vars = None
                    var_check_result.append((missing_vars,incorrect_dtype_vars))
                    # print('Grading not done for {} as it was not submitted by {}.'.format(q,s))
                    break

                for tar_var, tar_dtype in zip(self.ref_output[q].columns,self.ref_output[q].dtypes):
                    try:
                        if not self.sub_outputs[s][q][tar_var].dtype == tar_dtype:
                            incorrect_dtype_vars.append((tar_var,tar_dtype,self.sub_outputs[s][q][tar_var].dtype))
                            # print('variable {} has different {} dtype from expected {} dtype.'.format(tar_var,self.sub_outputs[s][q][tar_var].dtype,tar_dtype))
                    except:
                        missing_vars.append(tar_var)
                        # print('{} variable is not found in submission.'.format(tar_var))
                var_check_result.append((missing_vars,incorrect_dtype_vars))
            
            var_check_results.append(dict(zip(self.student_ids,var_check_result)))
        
        self.check_var_results = dict(zip(self.ref_output.keys(),var_check_results))
        return self.check_var_results



def compare_dict_df(d1,d2):
    """
    Checks equality the dataframes in the dictionaries d1, d2 based
    on the keys using the `.equals()` pandas function. The dictionary d1 
    is the reference which d2 is compared against. 
    
    Note that this function does not commutes.
    
    Args:
        d1, d2: dictionaries of form {node_annotation: dataframe_from_COT}.
    Returns:
        err_df: list of output annotations with not equal dataframe.
    """
    err_df = []
    for k in d2:
        if not (d2[k].equals(d1[k])):
            err_df.append(k)
    return err_df


def compare_dtypes(df1, df2, missing_var, foreign_var):
    """
    Returns a list of tuples which describe the variable name together
    with the expected and incorrect datatype.
    
    Note that this function does not commutes.

    Args:
        df1: dataframe output which is reference
        df2: dataframe output from a submission
        missing_var: list of missing variables from df1
        foreign_var: list of foreign variables in df2
    
    Returns:
        var_incorrect_dtype: list of 3-tuple of the form (variable_name, expected_dtype, actual_dtype)
    """
    df1 = df1.drop(columns=missing_var)
    df2 = df2.drop(columns=foreign_var)
    var_incorrect_dtype = []
    for v in df1.columns:
        if not (df1.dtypes[v] == df2.dtypes[v]):
            var_incorrect_dtype.append((v,df1.dtypes[v],df2.dtypes[v]))
    return var_incorrect_dtype

def compare_df_col(df1, df2, missing_var):
    """
    Returns a list of variable 
    """
    err_data_col = []
    
    for v in df1.drop(columns=missing_var).columns:
        if not df1[v].equals(df2[v]):
            err_data_col.append(v)
    return err_data_col

  