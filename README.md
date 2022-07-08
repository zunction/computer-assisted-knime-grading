# computer-assisted-knime-grading

![Alt Text]https://github.com/zunction/computer-assisted-knime-grading/blob/main/imgs/cakg.gif)

## Introduction 


```
python workflowgrader.py *your_knime_workspace* *your_reference_workflow*
```
Example

```
python workflowgrader.py C:\Users\*staff_id*\knime-workspace\lab5t1 ref_wf_lab5t1
```


```
08-07-2022 08:37:51 - Detecting workflowsets from C:\Users\s11006381\knime-workspace\folderspace...
      -> detected workflowset A.
      -> detected workflowset B.
  08-07-2022 08:37:51 - Reading reference workflow...
      -> reading of ref_wf is completed.
  08-07-2022 08:38:04 - Processing A...
    Extracting data from 2120823.knwf: 100%|=================================================================================================| 2/2 [00:30<00:00, 15.09s/it]
    Checking outputs from 2120823.knwf: 100%|########################################################################################################| 2/2 [00:00<?, ?it/s]
    Checking data from 2120823.knwf: 100%|##################################################################################################| 2/2 [00:00<00:00, 256.04it/s]
      -> a.csv is saved at C:\Users\s11006381\Desktop
  08-07-2022 08:38:35 - Processing B...
    Extracting data from 2121741.knwf: 100%|=================================================================================================| 3/3 [00:41<00:00, 13.80s/it]
    Checking outputs from 2121741.knwf: 100%|#############################################################################################| 3/3 [00:00<00:00, 10573.88it/s]
    Checking data from 2121741.knwf: 100%|##################################################################################################| 2/2 [00:00<00:00, 353.95it/s]
      -> b.csv is saved at C:\Users\s11006381\Desktop

  A total 5 workflows were graded in 85.0 seconds
```