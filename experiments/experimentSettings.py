import azure.mgmt.batchai.models as models


def get_cntk_parameters(cluster, config, model_file_name, dataset_directory='dataset_directory'):
    parameters = models.JobCreateParameters(
        # The cluster this job will run on
        cluster=models.ResourceId(id=cluster.id),
        # The number of VMs in the cluster to use
        node_count=config.workspace_node_count,
        # Write job's standard output and execution log to Azure File Share
        std_out_err_path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(
            config.workspace_relative_mount_path),
        # Configure location of the training script and dataset
        input_directories=[models.InputDirectory(
            id='SAMPLE',
            path='$AZ_BATCHAI_MOUNT_ROOT/{0}/{1}'.format(
                config.workspace_relative_mount_path, dataset_directory))],
        # Specify location where generated model will be stored
        output_directories=[models.OutputDirectory(
            id='MODEL',
            path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(config.workspace_relative_mount_path),
            path_suffix="Models")],
        # Container configuration
        container_settings=models.ContainerSettings(
            image_source_registry=models.ImageSourceRegistry(
                image='microsoft/cntk:2.1-gpu-python3.5-cuda8.0-cudnn6.0')),
        # Toolkit specific settings
        cntk_settings=models.CNTKsettings(
            python_script_file_path='$AZ_BATCHAI_INPUT_SAMPLE/{0}'.format(model_file_name),
            command_line_args='$AZ_BATCHAI_INPUT_SAMPLE $AZ_BATCHAI_OUTPUT_MODEL'))

    return parameters


def get_keras_parameters(cluster, config, model_name,
                         dataset_directory='dataset_directory', backend='tensorflow'):
    if backend == 'cntk':
        parameters = models.JobCreateParameters(
            location=config.location,
            cluster=models.ResourceId(id=cluster.id),
            node_count=config.workspace_node_count,
            container_settings=models.ContainerSettings(
                image_source_registry=models.ImageSourceRegistry(
                    image='microsoft/cntk:2.5.1-gpu-python2.7-cuda9.0-cudnn7.0')),
            mount_volumes=models.MountVolumes(
                azure_file_shares=[
                    models.AzureFileShareReference(
                        account_name=config.storage_account_name,
                        credentials=models.AzureStorageCredentialsInfo(
                            account_key=config.storage_account_key),
                        azure_file_url='https://{0}.file.core.windows.net/{1}'.format(
                            config.storage_account_name, config.workspace_file_share),
                        relative_mount_path=config.workspace_relative_mount_path)
                ]
            ),
            std_out_err_path_prefix='$AZ_BATCHAI_JOB_MOUNT_ROOT/{0}'.format(config.workspace_relative_mount_path),
            cntk_settings=models.CNTKsettings(
                python_script_file_path='$AZ_BATCHAI_JOB_MOUNT_ROOT/{0}/{1}/{2}'.format(config.workspace_relative_mount_path,
                                                                                        dataset_directory,
                                                                                        model_name)))
    if backend == 'tensorflow':
        parameters = models.JobCreateParameters(
            location=config.location,
            cluster=models.ResourceId(id=cluster.id),
            node_count=config.workspace_node_count,
            job_preparation=models.JobPreparation(command_line='pip install keras'),
            container_settings=models.ContainerSettings(
                image_source_registry=models.ImageSourceRegistry(image='tensorflow/tensorflow:1.8.0-gpu')),
            mount_volumes=models.MountVolumes(
                azure_file_shares=[
                    models.AzureFileShareReference(
                        account_name=config.storage_account_name,
                        credentials=models.AzureStorageCredentialsInfo(
                            account_key=config.storage_account_key),
                        azure_file_url='https://{0}.file.core.windows.net/{1}'.format(
                            config.storage_account_name, config.workspace_file_share),
                        relative_mount_path=config.workspace_relative_mount_path)
                ]
            ),
            std_out_err_path_prefix='$AZ_BATCHAI_JOB_MOUNT_ROOT/{0}'.format(config.workspace_relative_mount_path),
            tensor_flow_settings=models.TensorFlowSettings(
                python_script_file_path='$AZ_BATCHAI_JOB_MOUNT_ROOT/{0}/{1}/{2}'.format(config.workspace_relative_mount_path,
                                                                                        dataset_directory,
                                                                                        model_name)))

        return parameters
