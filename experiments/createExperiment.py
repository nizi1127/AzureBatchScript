from experiments import setupWorkspace as workspace
from experiments import experimentSettings as settings


def prepare_workspace_env(config, script, dataset=None):
    client, resource = workspace.create_batch_ai_client_and_resource(config)
    service = workspace.prepare_azure_file_share_service(config)
    if dataset is not None:
        for data in dataset:
            workspace.upload_script_to_azure(service, data, config)
    workspace.upload_script_to_azure(service, script, config)
    workspace.prepare_batch_ai_workspace(client, service, config)
    cluster = workspace.get_cluster_status(client, config)

    return client, cluster


def create_keras_exp(config, script_name, experiment_name, job_name, backend='tensorflow'):
    # prepare workspace environment
    client, cluster = prepare_workspace_env(config, script_name)

    # start exp job
    parameter = settings.get_keras_parameters(cluster, config, script_name, backend=backend)
    workspace.create_exp_job(client, config, experiment_name, job_name, parameter)

    # monitor exp status
    workspace.monitor_job(client, config, experiment_name, job_name, backend=backend)

    # remove created cluster in workspace
    workspace.delete_cluster(client, config)


def create_cntk_exp(config, script_name, experiment_name, job_name, dataset=None):
    # prepare workspace environment
    client, cluster = prepare_workspace_env(config, script_name, dataset)

    # start exp job
    parameter = settings.get_cntk_parameters(cluster, config, script_name)
    workspace.create_exp_job(client, config, experiment_name, job_name, parameter)

    # monitor exp status
    workspace.monitor_job(client, config, experiment_name, job_name, backend='cntk')

    # remove created cluster in workspace
    workspace.delete_cluster(client, config)
