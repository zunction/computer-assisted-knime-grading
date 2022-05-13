import knime
import pandas as pd
import numpy as np
import os
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

def compare_varnames(df1, df2):
    """
    Compares the variable names of the dataframes.
    The dataframe df1 is the reference which df2 is compared against. 
    
    Note that this function does not commutes.

    Args:
        df1, df2: dataframes extracted from COT nodes.
    Returns:
        missing_vars: list of variable names which are in df1 but not in df2.
        matched_vars: list of variable names which are in df1 and also in df2.
        score: a number in [0,1] to indicate the fraction of correctly matched variable names.
    """
    df1_col = df1.columns
    df2_col = df2.columns
    missing_vars = []
    foreign_vars = []
    for varname in df1_col:
        if not (varname in df2_col):
            missing_vars.append(varname)
    for varname in df2_col:
        if not (varname in df1_col):
            foreign_vars.append(varname)
    return missing_vars, foreign_vars, (len(df1_col)-len(missing_vars))/len(df1_col)

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

# class workflowgrader():
#     """
    
#     """
#     def __init__(self, gradespace, reference_workflow):
#         # directory with the workflows to be graded    
#         self.gradespace = gradespace
#         # workflow to be used as a reference for grading
#         self.reference_workflow = reference_workflow
#         # retrieve abspath of workflows to be graded
#         self.workflow_paths = glob.glob(os.path.join(gradespace,'[0-9]*'))
        
#         # assume that workflows are named using student ids
#         self.student_ids = os.path.basename(self.workflow_paths)  
#         self.ref_output = collect_workflow_outputs(os.path.join(gradespace,reference_workflow))
#         self.question_keys() = self.ref_output.keys()

        # assume no directories except for example workflows folder
        
    def compare_df_varnames(df1, df2):
        """
        Compares the variable names of the dataframes.
        The dataframe df1 is the reference which df2 is compared against. 
        
        Note that this function does not commutes.

        Args:
            df1, df2: dataframes extracted from COT nodes.
        Returns:
            missing_vars: list of variable names which are in df1 but not in df2.
            matched_vars: list of variable names which are in df1 and also in df2.
            score: a number in [0,1] to indicate the fraction of correctly matched variable names.
        """
        df1_col = df1.columns
        df2_col = df2.columns
        missing_vars = []
        foreign_vars = []
        for varname in df1_col:
            if not (varname in df2_col):
                missing_vars.append(varname)
        for varname in df2_col:
            if not (varname in df1_col):
                foreign_vars.append(varname)
        return missing_vars, foreign_vars

    def compare_df_dtypes(df1, df2, missing_var, foreign_var):
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

    def compare_COT_annotation(self,d2):
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
        for k in self.ref_output:
            if not (k in list(d2.keys())):
                missing_ann.append(k)
        for k in d2:
            if not (k in list(self.ref_output.keys())):
                foreign_ann.append(k)
        return missing_ann, foreign_ann     
    
    

    def compare_varnames(self, d2):
        """
        
        """
        mfv_by_question_keys = []
        for k in self.question_keys:
            mfs_list.append(compare_df_varnames(self.ref_output[v],d2[v]))
    return dict(zip(self.question_keys,mfs_list))

    # def compare_dtypes(self, d2):
    #     """
        
    #     """
    #     mfs = self.compare_varnames(d2)
        
    #     for k in self.question_keys:


    #     compare_df_dtypes()

    
    # return dict(zip(self.question_keys,mfs_list))
        
    
    # def grade(self):
    #     """

    #     """