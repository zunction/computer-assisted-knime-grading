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


#### Workflows in a workspace

<img src="/images/gradespace.png" width="300">

![Alt Text](/images/gradespace.png)



#### Workflows in folders in a workspace

<img src="/images/folderspace.png" width="300">

![Alt Text](/images/folderspace.png)


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