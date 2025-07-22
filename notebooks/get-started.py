#!/usr/bin/env python
# coding: utf-8

# ## MLFLow Tracking Server

# In[4]:


import mlflow
import os

#os.environ["MLFLOW_TRACKING_USERNAME"] = "user"
#os.environ["MLFLOW_TRACKING_PASSWORD"] = "xxx"



# In[5]:


mlflow.set_tracking_uri("https://mlflow.new-nation.church")


# In[6]:


mlflow.set_experiment("Check localhost connection2")

with mlflow.start_run():
    mlflow.log_metric("test",1)
    mlflow.log_metric("Krish",2)


# In[7]:


with mlflow.start_run():
    mlflow.log_metric("test1",1)
    mlflow.log_metric("Krish1",2)


# In[8]:


with mlflow.start_run():
    mlflow.log_metric("test2",1)
    mlflow.log_metric("Krish2",2)


# In[ ]:




