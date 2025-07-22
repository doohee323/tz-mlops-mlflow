#!/usr/bin/env python
# coding: utf-8

# ### Getting Started With ML Project With MLFLOW
# 
# - Installing MLflow.
# 
# - Starting a local MLflow Tracking Server.
# 
# - Logging and registering a model with MLflow.
# 
# - Loading a logged model for inference using MLflow’s pyfunc flavor.
# 
# - Viewing the experiment results in the MLflow UI.

# In[1]:


import pandas as pd
from sklearn import datasets
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import mlflow
from mlflow.models import infer_signature
import os

# os.environ["MLFLOW_TRACKING_USERNAME"] = "user"
# os.environ["MLFLOW_TRACKING_PASSWORD"] = "xxx"


# In[2]:


## set the tracking uri
# mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")
mlflow.set_tracking_uri("https://mlflow.new-nation.church")


# In[3]:


## load the dataset
X,y=datasets.load_iris(return_X_y=True)
# split the data into training and test sets
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.20)

# Define the model hyperparameters
params = {"penalty":"l2","solver": "lbfgs", "max_iter": 1000, "multi_class": "auto", "random_state": 8888}

##train the model

lr=LogisticRegression(**params)
lr.fit(X_train,y_train)


# In[4]:


X_test


# In[4]:


## Prediction on the test set
y_pred=lr.predict(X_test)
y_pred


# In[5]:


accuracy=accuracy_score(y_test,y_pred)
print(accuracy)


# ### MLFLOW Tracking

# In[7]:


### MLFLOW tracking
# mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")
mlflow.set_tracking_uri("https://mlflow.new-nation.church")

##create a new MLFLOW experiment
mlflow.set_experiment("MLFLOW Quickstart")

## Sstart an MLFLOW run
with mlflow.start_run():
    ## log the hyperparameters
    mlflow.log_params(params)

    ## Log the accuracy metrics
    mlflow.log_metric("accuracy",accuracy)

    # Set a tag that we can use to remind ourselves what this run was for
    mlflow.set_tag("Training Info", "Basic LR model for iris data")

    ## Infer the model signature

    signature=infer_signature(X_train,lr.predict(X_train))

    ## log the model
    model_info=mlflow.sklearn.log_model(
        sk_model=lr,
        artifact_path="iris_model",
        signature=signature,
        input_example=X_train,
        registered_model_name="tracking-quickstart",

    )


    


# In[8]:


# Define the model hyperparameters
params = {"solver": "newton-cg", "max_iter": 1000, "multi_class": "auto", "random_state": 1000}

##train the model

lr=LogisticRegression(**params)
lr.fit(X_train,y_train)


# In[9]:


y_pred=lr.predict(X_test)
y_pred


# In[10]:


accuracy=accuracy_score(y_test,y_pred)
print(accuracy)


# In[11]:


## Sstart an MLFLOW run
with mlflow.start_run():
    ## log the hyperparameters
    mlflow.log_params(params)

    ## Log the accuracy metrics
    mlflow.log_metric("accuracy",accuracy)

    # Set a tag that we can use to remind ourselves what this run was for
    mlflow.set_tag("Training Info", "Basic LR model for iris data")

    ## Infer the model signature

    signature=infer_signature(X_train,lr.predict(X_train))

    ## log the model
    model_info=mlflow.sklearn.log_model(
        sk_model=lr,
        artifact_path="iris_model",
        signature=signature,
        input_example=X_train,
        registered_model_name="tracking-quickstart",

    )


# In[12]:


model_info.model_uri


# ## Inferencing And Validating Model

# In[13]:


from mlflow.models import validate_serving_input

model_uri = model_info.model_uri

# The model is logged with an input example. MLflow converts
# it into the serving payload format for the deployed model endpoint,
# and saves it to 'serving_input_payload.json'
serving_payload = """{
  "inputs": [
    [
      5.7,
      3.8,
      1.7,
      0.3
    ],
    [
      4.8,
      3.4,
      1.6,
      0.2
    ],
    [
      5.6,
      2.9,
      3.6,
      1.3
    ],
    [
      5.4,
      3.7,
      1.5,
      0.2
    ],
    [
      6.7,
      3.3,
      5.7,
      2.5
    ],
    [
      6.5,
      3.0,
      5.8,
      2.2
    ],
    [
      5.1,
      2.5,
      3.0,
      1.1
    ],
    [
      7.7,
      3.0,
      6.1,
      2.3
    ],
    [
      5.2,
      4.1,
      1.5,
      0.1
    ],
    [
      5.0,
      3.3,
      1.4,
      0.2
    ],
    [
      4.6,
      3.6,
      1.0,
      0.2
    ],
    [
      4.5,
      2.3,
      1.3,
      0.3
    ],
    [
      5.6,
      2.8,
      4.9,
      2.0
    ],
    [
      6.2,
      3.4,
      5.4,
      2.3
    ],
    [
      6.3,
      3.4,
      5.6,
      2.4
    ],
    [
      4.8,
      3.4,
      1.9,
      0.2
    ],
    [
      5.8,
      2.7,
      5.1,
      1.9
    ],
    [
      7.2,
      3.0,
      5.8,
      1.6
    ],
    [
      5.4,
      3.9,
      1.7,
      0.4
    ],
    [
      6.9,
      3.2,
      5.7,
      2.3
    ],
    [
      6.5,
      3.0,
      5.5,
      1.8
    ],
    [
      7.7,
      2.6,
      6.9,
      2.3
    ],
    [
      6.4,
      3.1,
      5.5,
      1.8
    ],
    [
      5.2,
      3.5,
      1.5,
      0.2
    ],
    [
      6.3,
      2.9,
      5.6,
      1.8
    ],
    [
      4.9,
      3.1,
      1.5,
      0.2
    ],
    [
      7.9,
      3.8,
      6.4,
      2.0
    ],
    [
      5.5,
      4.2,
      1.4,
      0.2
    ],
    [
      6.1,
      3.0,
      4.9,
      1.8
    ],
    [
      5.0,
      3.2,
      1.2,
      0.2
    ],
    [
      4.9,
      3.0,
      1.4,
      0.2
    ],
    [
      6.0,
      2.2,
      4.0,
      1.0
    ],
    [
      5.0,
      3.6,
      1.4,
      0.2
    ],
    [
      4.6,
      3.4,
      1.4,
      0.3
    ],
    [
      6.9,
      3.1,
      5.1,
      2.3
    ],
    [
      5.0,
      3.5,
      1.3,
      0.3
    ],
    [
      5.8,
      2.8,
      5.1,
      2.4
    ],
    [
      4.9,
      3.1,
      1.5,
      0.1
    ],
    [
      5.6,
      2.7,
      4.2,
      1.3
    ],
    [
      7.0,
      3.2,
      4.7,
      1.4
    ],
    [
      6.3,
      2.7,
      4.9,
      1.8
    ],
    [
      5.0,
      3.4,
      1.5,
      0.2
    ],
    [
      5.8,
      2.7,
      5.1,
      1.9
    ],
    [
      6.1,
      2.9,
      4.7,
      1.4
    ],
    [
      7.2,
      3.6,
      6.1,
      2.5
    ],
    [
      6.7,
      3.1,
      5.6,
      2.4
    ],
    [
      6.3,
      3.3,
      6.0,
      2.5
    ],
    [
      6.3,
      2.5,
      4.9,
      1.5
    ],
    [
      4.8,
      3.1,
      1.6,
      0.2
    ],
    [
      6.4,
      2.8,
      5.6,
      2.1
    ],
    [
      6.2,
      2.9,
      4.3,
      1.3
    ],
    [
      5.7,
      2.5,
      5.0,
      2.0
    ],
    [
      6.0,
      3.4,
      4.5,
      1.6
    ],
    [
      5.2,
      3.4,
      1.4,
      0.2
    ],
    [
      5.7,
      4.4,
      1.5,
      0.4
    ],
    [
      5.0,
      2.3,
      3.3,
      1.0
    ],
    [
      6.2,
      2.2,
      4.5,
      1.5
    ],
    [
      6.3,
      2.3,
      4.4,
      1.3
    ],
    [
      6.3,
      2.8,
      5.1,
      1.5
    ],
    [
      5.1,
      3.3,
      1.7,
      0.5
    ],
    [
      6.0,
      2.9,
      4.5,
      1.5
    ],
    [
      6.5,
      3.0,
      5.2,
      2.0
    ],
    [
      5.3,
      3.7,
      1.5,
      0.2
    ],
    [
      6.8,
      2.8,
      4.8,
      1.4
    ],
    [
      5.9,
      3.0,
      5.1,
      1.8
    ],
    [
      4.7,
      3.2,
      1.6,
      0.2
    ],
    [
      5.5,
      3.5,
      1.3,
      0.2
    ],
    [
      6.7,
      3.0,
      5.2,
      2.3
    ],
    [
      5.7,
      2.6,
      3.5,
      1.0
    ],
    [
      5.8,
      2.7,
      4.1,
      1.0
    ],
    [
      5.5,
      2.5,
      4.0,
      1.3
    ],
    [
      5.1,
      3.8,
      1.9,
      0.4
    ],
    [
      5.7,
      2.8,
      4.5,
      1.3
    ],
    [
      6.7,
      3.1,
      4.4,
      1.4
    ],
    [
      6.4,
      3.2,
      5.3,
      2.3
    ],
    [
      7.7,
      2.8,
      6.7,
      2.0
    ],
    [
      5.5,
      2.6,
      4.4,
      1.2
    ],
    [
      5.7,
      2.9,
      4.2,
      1.3
    ],
    [
      7.4,
      2.8,
      6.1,
      1.9
    ],
    [
      7.6,
      3.0,
      6.6,
      2.1
    ],
    [
      6.3,
      3.3,
      4.7,
      1.6
    ],
    [
      5.4,
      3.0,
      4.5,
      1.5
    ],
    [
      6.2,
      2.8,
      4.8,
      1.8
    ],
    [
      4.4,
      3.2,
      1.3,
      0.2
    ],
    [
      6.6,
      2.9,
      4.6,
      1.3
    ],
    [
      7.2,
      3.2,
      6.0,
      1.8
    ],
    [
      4.7,
      3.2,
      1.3,
      0.2
    ],
    [
      5.7,
      2.8,
      4.1,
      1.3
    ],
    [
      5.5,
      2.3,
      4.0,
      1.3
    ],
    [
      5.1,
      3.8,
      1.5,
      0.3
    ],
    [
      6.1,
      2.6,
      5.6,
      1.4
    ],
    [
      4.6,
      3.2,
      1.4,
      0.2
    ],
    [
      6.7,
      3.3,
      5.7,
      2.1
    ],
    [
      6.7,
      3.1,
      4.7,
      1.5
    ],
    [
      5.6,
      2.5,
      3.9,
      1.1
    ],
    [
      5.1,
      3.5,
      1.4,
      0.2
    ],
    [
      5.0,
      3.4,
      1.6,
      0.4
    ],
    [
      5.1,
      3.5,
      1.4,
      0.3
    ],
    [
      4.8,
      3.0,
      1.4,
      0.1
    ],
    [
      6.1,
      2.8,
      4.7,
      1.2
    ],
    [
      5.9,
      3.0,
      4.2,
      1.5
    ],
    [
      5.0,
      3.5,
      1.6,
      0.6
    ],
    [
      6.1,
      3.0,
      4.6,
      1.4
    ],
    [
      6.8,
      3.0,
      5.5,
      2.1
    ],
    [
      5.1,
      3.8,
      1.6,
      0.2
    ],
    [
      5.7,
      3.0,
      4.2,
      1.2
    ],
    [
      4.4,
      2.9,
      1.4,
      0.2
    ],
    [
      4.4,
      3.0,
      1.3,
      0.2
    ],
    [
      5.4,
      3.4,
      1.5,
      0.4
    ],
    [
      7.7,
      3.8,
      6.7,
      2.2
    ],
    [
      5.0,
      2.0,
      3.5,
      1.0
    ],
    [
      6.4,
      2.9,
      4.3,
      1.3
    ],
    [
      6.0,
      2.2,
      5.0,
      1.5
    ],
    [
      4.6,
      3.1,
      1.5,
      0.2
    ],
    [
      5.8,
      2.7,
      3.9,
      1.2
    ],
    [
      4.9,
      2.5,
      4.5,
      1.7
    ],
    [
      4.8,
      3.0,
      1.4,
      0.3
    ],
    [
      5.4,
      3.9,
      1.3,
      0.4
    ],
    [
      6.4,
      3.2,
      4.5,
      1.5
    ],
    [
      6.3,
      2.5,
      5.0,
      1.9
    ]
  ]
}"""

# Validate the serving payload works on the model
validate_serving_input(model_uri, serving_payload)


# ## Load the model back for prediction as a generic python function model

# In[14]:


loaded_model=mlflow.pyfunc.load_model(model_info.model_uri)
predictions=loaded_model.predict(X_test)

iris_features_name=datasets.load_iris().feature_names

result=pd.DataFrame(X_test,columns=iris_features_name)
result["actual_class"]=y_test
result["predcited_class"]=predictions


# In[15]:


result[:5]


# ### Model Registry
# 
# The MLflow Model Registry component is a centralized model store, set of APIs, and UI, to collaboratively manage the full lifecycle of an MLflow Model. It provides model lineage (which MLflow experiment and run produced the model), model versioning, model aliasing, model tagging, and annotations.

# In[ ]:





# In[16]:


## log the model
model_info=mlflow.sklearn.log_model(
    sk_model=lr,
    artifact_path="iris_model",
    signature=signature,
    input_example=X_train,
    registered_model_name="tracking-quickstart",

)


# In[17]:


##create a new MLFLOW experiment
mlflow.set_experiment("MLFLOW Quickstart")

## Sstart an MLFLOW run
with mlflow.start_run():
    ## log the hyperparameters
    mlflow.log_params(params)

    ## Log the accuracy metrics
    mlflow.log_metric("accuracy",1.0)

    # Set a tag that we can use to remind ourselves what this run was for
    mlflow.set_tag("Training Info2", "Basic LR model for iris data")

    ## Infer the model signature

    signature=infer_signature(X_train,lr.predict(X_train))

    ## log the model
    ## log the model
    model_info=mlflow.sklearn.log_model(
        sk_model=lr,
        artifact_path="iris_model",
        signature=signature,
        input_example=X_train,

    )


# In[18]:


## Inferencing from model from model registry

import mlflow.sklearn
model_name="tracking-quickstart"
model_version="latest"

model_uri=f"models:/{model_name}/{model_version}"

model=mlflow.sklearn.load_model(model_uri)
model


# In[19]:


model_uri


# In[20]:


y_pred_new=model.predict(X_test)
y_pred_new


# In[ ]:




