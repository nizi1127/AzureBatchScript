# AzureBatchScript
Run azure batch in one command line

## Prerequisites
1. Create an Azure subscription
2. Setup Python SDK  - See [installation instruction](https://docs.microsoft.com/en-us/python/azure/python-sdk-azure-install?view=azure-python)
3. Create a storage account on Azure portal - See [How to create an Azure storage account](https://docs.microsoft.com/en-us/azure/storage/common/storage-create-storage-account)
4. Regist Azure Active Directory service principal credentials - See [How to create a service principal with the CLI](https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli?view=azure-cli-latest)
5. Register the Batch AI resource provider once for your subscription using Azure Cloud Shell or the Azure CLI. A provider registration can take up to 15 minutes.
```
az provider register -n Microsoft.BatchAI
```
6. requirements: 
    - azure-mgmt-batchai==2.0.0
    - azure==3.0.0
    - requests==2.18.4
    - six==1.11.0
    - jsonschema==2.6.0
    - numpy==1.14.3
    - futures==3.2.0

## Update Configuration.json with above information
- Set subscription id
- Set aad client id, password and tenant
- Recommended location is eastus2
- Set storage account name an key
- Admin uset name and password is used to login created cluster nodes
- Choose proper vm_size and node_cout

## Run Command
Require script file name, which is target deep learning python file.
And default framework is Keras with TensorFlow backend.
```
AzureBatch.py -s <script_name> [-e <experiment_name>] [-f <framework>] [-b <backend>] [-t <training_data>,<testing_data>]
```
### Supported Framework
- Keras with TensorFlow backend
- Keras with CNTK backend
- CNTK

### Example
Run MNIST script with Keras(TensorFlow)
```
AzureBatch.py -s mnist_cnn.py -e Keras_MNIST_Exp
```

Run MNIST script with Keras(CNTK)
```
AzureBatch.py -s mnist_cnn.py -e Keras_MNIST_Exp -f Keras -b cntk
```
