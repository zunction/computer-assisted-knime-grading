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

To process workflows in the workspace `gradespace` (workflows in a workspace) using the reference workflow `ref_wf`:
```
python workflowgrader.py C:\Users\123\knime-workspace\gradespace ref_wf
```

```
(base) C:\Users\123\Documents\Learnings\computer-assisted-knime-grading>python workflowgrader.py C:\Users\123\knime-workspace\gradespace ref_wf
  20-07-2022 15:13:46 - Detecting workflowsets from C:\Users\123\knime-workspace\gradespace...
      -> No workflowsets detected. Processing workflows in workspace gradespace.
  20-07-2022 15:13:46 - Reading reference workflow...
      -> reading of ref_wf is completed.
  20-07-2022 15:13:58 - Processing GRADESPACE...
    Extracting data from b3.knwf: 100%|======================================================================================================| 5/5 [01:02<00:00, 12.47s/it]
    Checking outputs from b3.knwf: 100%|###################################################################################################| 5/5 [00:00<00:00, 1992.92it/s]
    Checking data from b3.knwf: 100%|########################################################################################################| 2/2 [00:00<00:00, 81.84it/s]
      -> gradespace.csv is saved at C:\Users\123\knime-workspace\gradespace

  A total 5 workflows were graded in 74.0 seconds
```


To process workflows in the workspace `folderspace` (workflows in folders in a workspace) using the reference workflow `ref_wf` and save the outputs to `Desktop`:
```
python workflowgrader.py C:\Users\123\knime-workspace\folderspace ref_wf --save-dir C:\Users\123\Desktop
```

```
(base) C:\Users\123\computer-assisted-knime-grading>python workflowgrader.py C:\Users\s11006381\knime-workspace\folderspace ref_wf --save-dir C:\Users\123\Desktop
  20-07-2022 13:35:38 - Detecting workflowsets from C:\Users\123\knime-workspace\folderspace...
      -> detected workflowset A.
      -> detected workflowset B.
  20-07-2022 13:35:38 - Reading reference workflow...
      -> reading of ref_wf is completed.
  20-07-2022 13:35:51 - Processing A...
    Extracting data from a2.knwf: 100%|======================================================================================================| 3/3 [00:32<00:00, 10.87s/it]
    Checking outputs from a2.knwf: 100%|###################################################################################################| 3/3 [00:00<00:00, 1333.36it/s]
    Checking data from a2.knwf: 100%|#######################################################################################################| 2/2 [00:00<00:00, 105.22it/s]
      -> a.csv is saved at C:\Users\123\Desktop
  20-07-2022 13:36:24 - Processing B...
    Extracting data from b3.knwf: 100%|======================================================================================================| 4/4 [00:45<00:00, 11.30s/it]
    Checking outputs from b3.knwf: 100%|###################################################################################################| 4/4 [00:00<00:00, 1338.54it/s]
    Checking data from b3.knwf: 100%|#######################################################################################################| 2/2 [00:00<00:00, 126.53it/s]
      -> b.csv is saved at C:\Users\123\Desktop

  A total 7 workflows were graded in 91.0 seconds
```

**Note**: If the workflows to be processed are open in KNIME, the following error will be encountered:
```
ChildProcessError: Workflow is locked by another KNIME instance
```

#### Test
![Alt Text](https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif)

A typical command which grade workflows in the workspace `lab5t1` using the reference workflow `ref_wf_lab5t1`.

```
python workflowgrader.py C:\Users\123\knime-workspace\lab5t1 ref_wf_lab5t1
```

By default the csv output(s) of the process is saved in the KNIME workspace directory or within the folders in the KNIME workspace.
An alternative to consolidate all the outputs at a single location like the Desktop is possible with the `--save-dir` optional argument.
Below is the command for grading the same workflows above with the output saved to `C:\Users\123\Desktop`.

```
python workflowgrader.py C:\Users\123\knime-workspace\lab5t1 ref_wf_lab5t1 --save-dir C:\Users\123\Desktop
```

## 


## Future work

- Summarizing workflows when reference workflow is not provided
- Mark/grade assignment to graded workflow