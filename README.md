# Computer assisted KNIME grading (CAKG)

**CAKG** is a grading tool that assist instructors with their grading of KNIME workflows.
The CAKG grading tool extracts data from submitted workflows and returns the instructor with a summary in the form of a csv file.
The summary provides the instructor with metrics that measures the completion of tasks within a workflow and is accompanied with further details to pinpoint the areas of improvement.

This library is under development and is built from a modified [knime(py)](https://github.com/knime/knimepy), the Python toolkit for KNIME.

## Getting started

CAKG works directly in anaconda prompt with no installation of any packages required. 
There are no hard dependencies other than Python 3.6+ and the Python standard library itself.

### For typical use

[Download](https://github.com/zunction/computer-assisted-knime-grading/archive/refs/heads/main.zip) and extract the downloaded zip file  or clone this repository.
Navigate to the extracted/cloned folder in anaconda prompt to send commands.

## Commands



### Basic commands

```
python workflowgrader.py *your_knime_workspace* *your_reference_workflow*
```
Example

```
python workflowgrader.py C:\Users\*staff_id*\knime-workspace\lab5t1 ref_wf_lab5t1
```

### Advanced commands

#### Specifying save location of the result

```
python workflowgrader.py *your_knime_workspace* *your_reference_workflow* --save-dir *result_save_location*
```


## Future work

- Summarizing workflows when reference workflow is not provided
- Mark/grade assignment to graded workflow