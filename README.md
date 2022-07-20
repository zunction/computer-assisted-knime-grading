# Computer assisted KNIME grading (CAKG)

**CAKG** is a grading tool that assist instructors with their grading of KNIME workflows.
The CAKG grading tool helps to extract data from submitted workflows and returns the instructor with a summary in the form of a `.csv` file.
The summary provides the instructor with metrics that measures the completion of tasks within a workflow and is accompanied with further details to pinpoint the areas of improvement.

This library is under development and is built from a modified [knime(py)](https://github.com/knime/knimepy), the Python toolkit for KNIME.

## Getting started

The requirements for running CAKG is [**Anaconda 3**](https://www.anaconda.com/).
It works directly in anaconda prompt with no installation of any packages required. 
There are no hard dependencies other than Python 3.6+ and the Python standard library itself.


### For typical use

[Download](https://github.com/zunction/computer-assisted-knime-grading/archive/refs/heads/main.zip) and extract the downloaded zip file  or clone this repository.
Navigate to the extracted/cloned folder in anaconda prompt to send commands to process the workflows.


### Usage examples

The *first step* to using CAKG is to set up a worksplace containing the workflows to be processed.
Your workflows in the workspace can be organised in one of the two ways described below:

#### Setup of workspace

##### Workflows in a workspace

<img src="/images/gradespace.png" width="300">

The setting in the workspace above has all the workflows in the same `LOCAL (Local Workspace)` directory.
Here the `a1, a2, b1, b2, b3` are workflows to be processed and `ref_wf` is the workflow used as a reference for the processing.
This setup is suitable when grading workflows for a *single class*.


##### Workflows in folders in a workspace

<img src="/images/folderspace.png" width="300">

For this workspace setting, there are folders (called *workflowsets*) `a` and `b` in the `LOCAL (Local Workspace)` directory which is used to separate workflows of different classes apart.
The workflows are processed with `ref_wf` as the reference, which is located in the `LOCAL (Local Workspace)` directory.
This setup is recommended when grading the *same* workflows for a *more than one class* as it consolidates all the workflows in a single workspace.

#### Processing commands

The commands to process workflows are the same regardless of your workspace setup.
To process the workflow, the arguments needed are:
1. workspace directory
2. reference workflow
3. (Optional) save directory, which is the location to save the outputs 

when the save directory is *not provided*, the outputs are saved to the workspace or the respective folders.

**Example 1**

To process workflows in the workspace `gradespace` (workflows in a workspace) using the reference workflow `ref_wf`:
```
python workflowgrader.py C:\Users\123\knime-workspace\gradespace ref_wf
```

**Result**

```
(base) C:\Users\123\computer-assisted-knime-grading>python workflowgrader.py \
                              C:\Users\123\knime-workspace\gradespace ref_wf
  20-07-2022 15:13:46 - Detecting workflowsets from C:\Users\123\knime-workspace\gradespace...
      -> No workflowsets detected. Processing workflows in workspace gradespace.
  20-07-2022 15:13:46 - Reading reference workflow...
      -> reading of ref_wf is completed.
  20-07-2022 15:13:58 - Processing GRADESPACE...
    Extracting data from b3.knwf: 100%|=========================| 5/5 [01:02<00:00, 12.47s/it]
    Checking outputs from b3.knwf: 100%|########################| 5/5 [00:00<00:00, 1992.92it/s]
    Checking data from b3.knwf: 100%|#############################| 2/2 [00:00<00:00, 81.84it/s]
      -> gradespace.csv is saved at C:\Users\123\knime-workspace\gradespace

  A total 5 workflows were graded in 74.0 seconds
```

**Example 2**

To process workflows in the workspace `folderspace` (workflows in folders in a workspace) using the reference workflow `ref_wf` and save the outputs to `Desktop`:
```
python workflowgrader.py C:\Users\123\knime-workspace\folderspace ref_wf --save-dir C:\Users\123\Desktop
```

**Result**

```
(base) C:\Users\123\computer-assisted-knime-grading>python workflowgrader.py \
                       C:\Users\123\knime-workspace\folderspace ref_wf \
                       --save-dir C:\Users\123\Desktop
  20-07-2022 13:35:38 - Detecting workflowsets from C:\Users\123\knime-workspace\folderspace...
      -> detected workflowset A.
      -> detected workflowset B.
  20-07-2022 13:35:38 - Reading reference workflow...
      -> reading of ref_wf is completed.
  20-07-2022 13:35:51 - Processing A...
    Extracting data from a2.knwf: 100%|========================| 3/3 [00:32<00:00, 10.87s/it]
    Checking outputs from a2.knwf: 100%|#######################| 3/3 [00:00<00:00, 1333.36it/s]
    Checking data from a2.knwf: 100%|##########################| 2/2 [00:00<00:00, 105.22it/s]
      -> a.csv is saved at C:\Users\123\Desktop
  20-07-2022 13:36:24 - Processing B...
    Extracting data from b3.knwf: 100%|========================| 4/4 [00:45<00:00, 11.30s/it]
    Checking outputs from b3.knwf: 100%|#######################| 4/4 [00:00<00:00, 1338.54it/s]
    Checking data from b3.knwf: 100%|##########################| 2/2 [00:00<00:00, 126.53it/s]
      -> b.csv is saved at C:\Users\123\Desktop

  A total 7 workflows were graded in 91.0 seconds
```

**Note**: Please ensure that there are *no* workflows are open in KNIME before processing them. When attempting to process a workflow opened in KNIME, the error message `ChildProcessError: Workflow is locked by another KNIME instance` will be returned.

#### Summary output

The output `.csv` file provides the following information on the workflows it has processed:




| S/N | Attribute | Description | Datatype | Remarks |
|:---:|:---:|:---:|:---:|---|
| 1 | index | A unique identifier for each submitted workflow | string |  |
| 2 | question_completion | A value between [0,1] to indicate proportion of questions attempted. | float |  |
| 3 | *_var_completion | A value between [0,1] to indicate proportion of variables with names matching the reference workflow. | float |  |
| 4 | *_dtype_completion | A value between [0,1] to indicate proportion of variables with datatype matching the reference workflow. | float |  |
| 5 | *_data_completion | A value between [0,1] to indicate proportion of variables with data matching the reference workflow. | float |  |
| 6 | node_completion | A value to indicate number of nodes used relative to the reference workflow. Values which are <1 and >1 indicates lesser nodes and more nodes used relative to the reference workflow respectively.  | float |  |
| 7 | missing_questions | A list of strings to indicate the questions which are missing from the submission. | list |  |
| 8 | foreign_questions | A list of strings to indicate the unexpected questions which are observed in the workflow. | list |  |
| 9 | *_missing_var | A variable for each COT node output which provides a list of missing variables from the output. | list |  |
| 10 | *_incorrect_var_dtype | A variable for each COT node output which provides a list of variables with incorrect datatype from the output. | list |  |
| 11 | *_incorrect_var_values | A variable for each COT node output which provides a list of variables with incorrect values from the output. | list |  |
| 12 | Names of nodes, e.g. File Reader, Statistics, Box Plot | Number of nodes used with respect to the name of the node. | int |  |
| 13 | node_count | Total number of nodes found in the workflow. The node might not be connected, executed and purely just exists in the workflow. | int |  |
| 14 | data_filepaths | The filepaths which the data is loaded from using CSV Table Reader, Excel Table Reader or File Reader node.
 |  |  |



The filepaths which the data is loaded from using CSV Table Reader, Excel Table Reader or File Reader node.
## Possible explorations

- Summarizing workflows when reference workflow is not provided
- Mark/grade assignment to graded workflow