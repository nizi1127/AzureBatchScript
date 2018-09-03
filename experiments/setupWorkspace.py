from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.storage.file import FileService
import azure.mgmt.batchai as batchai
import azure.mgmt.batchai.models as models
import utilities as utils


def create_batch_ai_client_and_resource(config):
    # Create Batch AI client
    creds = ServicePrincipalCredentials(client_id=config.aad_client_id, secret=config.aad_secret_key, tenant=config.aad_tenant)
    batchai_client = batchai.BatchAIManagementClient(credentials=creds, subscription_id=config.subscription_id)

    # Create a resource group
    resource_management_client = ResourceManagementClient(
        credentials=creds, subscription_id=config.subscription_id)
    resource = resource_management_client.resource_groups.create_or_update(
        config.workspace_resource_group, {'location': config.location})

    return batchai_client, resource


# Prepare Azure file share
def prepare_azure_file_share_service(config, dataset_directory='dataset_directory'):
    # Create a file share
    service = FileService(config.storage_account_name, config.storage_account_key)
    service.create_share(config.workspace_file_share, fail_on_exist=False)

    # Create a directory in the file share
    service.create_directory(config.workspace_file_share, dataset_directory, fail_on_exist=False)

    return service


# Download the sample package and unzip into the current directory.
# The following code uploads required files into Azure File share:
def upload_training_files_to_azure(service, train_file_name, test_file_name, model_file_name, config,
                                   azure_dataset_directory='dataset_directory'):
    for f in [train_file_name, test_file_name, model_file_name]:
         service.create_file_from_path(config.workspace_file_share, azure_dataset_directory, f, f)


def upload_script_to_azure(service, model_file_name, config, azure_dataset_directory='dataset_directory'):
     service.create_file_from_path(config.workspace_file_share, azure_dataset_directory, model_file_name, model_file_name)


def prepare_batch_ai_workspace(client, service, config):
    # Create Batch AI workspace
    client.workspaces.create(config.workspace_resource_group,
                             config.workspace,
                             config.location)

    # Create GPU cluster
    parameters = models.ClusterCreateParameters(
        # VM size. Use N-series for GPU
        vm_size=config.workspace_vm_size,
        # Configure the ssh users
        user_account_settings=models.UserAccountSettings(
            admin_user_name=config.admin,
            admin_user_password=config.admin_password),
        # Number of VMs in the cluster
        scale_settings=models.ScaleSettings(
            manual=models.ManualScaleSettings(target_node_count=config.workspace_node_count)
        ),
        # Configure each node in the cluster
        node_setup=models.NodeSetup(
            # Mount shared volumes to the host
            mount_volumes=models.MountVolumes(
                azure_file_shares=[
                    models.AzureFileShareReference(
                        account_name=config.storage_account_name,
                        credentials=models.AzureStorageCredentialsInfo(
                            account_key=config.storage_account_key),
                        azure_file_url='https://{0}/{1}'.format(
                            service.primary_endpoint, config.workspace_file_share),
                        relative_mount_path=config.workspace_relative_mount_path)],
            ),
        ),
    )
    client.clusters.create(config.workspace_resource_group, config.workspace, config.workspace_cluster, parameters).result()


# Get cluster status
def get_cluster_status(client, config):
    cluster = client.clusters.get(config.workspace_resource_group, config.workspace, config.workspace_cluster)
    print('Cluster state: {0} Target: {1}; Allocated: {2}; Idle: {3}; '
          'Unusable: {4}; Running: {5}; Preparing: {6}; Leaving: {7}'.format(
        cluster.allocation_state,
        cluster.scale_settings.manual.target_node_count,
        cluster.current_node_count,
        cluster.node_state_counts.idle_node_count,
        cluster.node_state_counts.unusable_node_count,
        cluster.node_state_counts.running_node_count,
        cluster.node_state_counts.preparing_node_count,
        cluster.node_state_counts.leaving_node_count))
    return cluster


# Create experiment and training job
def create_experiment(client, config, experiment_name):
    experiment = client.experiments.create(config.workspace_resource_group, config.workspace, experiment_name)
    return experiment


def create_exp_job(client, config, experiment_name, job_name, parameters):
    # create experiment
    create_experiment(client, config, experiment_name)

    # create job
    client.jobs.create(config.workspace_resource_group, config.workspace, experiment_name, job_name,
                       parameters).result()
    print('Created Job {0} in Experiment {1}'.format(job_name, experiment_name))


# Monitor job
def monitor_job(client, config, experiment_name, job_name, backend='tensorflow'):
    job = client.jobs.get(config.workspace_resource_group,
                          config.workspace,
                          experiment_name,
                          job_name)

    print('Job state: {0} '.format(job.execution_state))

    if backend == 'tensorflow':
        read_file = 'stdout-wk-0.txt'
    elif backend == 'cntk':
        read_file = 'stdout.txt'
    utils.job.wait_for_job_completion(client, config.workspace_resource_group, config.workspace,
                                      experiment_name, job_name, config.workspace_cluster, 'stdouterr', read_file)


def delete_cluster(client, config):
    client.clusters.delete(config.workspace_resource_group, config.workspace, config.workspace_cluster)