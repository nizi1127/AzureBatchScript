from experiments import createExperiment as exp
from datetime import datetime
import utilities as utils
import sys
import getopt
from enum import Enum

class Framework(Enum):
    CNTK = 1,
    KERAS_TENSORFLOW = 2,
    KERAS_CNTK = 3,
    TENSORFLOW = 4


class Backend(Enum):
    TENSORFLOW = 1,
    CNTK = 2,
    NONE = 3


def read_args(argv):
    helper = 'test.py -s <script_name> -e <experiment_name> -f <framework> -b <backend> ' \
             '-train <training_data> -test <testing_data>'
    script_name = None
    training_data = None
    testing_data = None
    experiment_name = datetime.utcnow().strftime('exp_%m_%d_%Y_%H%M%S')
    framework = Framework.KERAS_TENSORFLOW  # default set Keras Tensorflow
    backend = Backend.TENSORFLOW

    try:
        opts, args = getopt.getopt(argv,"hs:e:f:b:",["train=", "test=", "help"])
    except getopt.GetoptError:
        print(helper)
        sys.exit(2)

    for opt, arg in opts:
        if opt == ("-h", "--help"):
            print(helper)
            sys.exit()
        elif opt == "-s":
            script_name = arg
        elif opt == "-e":
            experiment_name = arg
        elif opt == "-f":
            framework = {
                'keras' : Framework.KERAS_TENSORFLOW,
                'cntk' : Framework.CNTK,
                'tensorflow' : Framework.TENSORFLOW
            }[arg.lower()]
        elif opt == "-b":
            backend = {
                'cntk': Backend.CNTK,
                'tensorflow': Backend.TENSORFLOW
            }[arg.lower()]
        elif opt == "-train":
            training_data = arg
        elif opt == "-test":
            testing_data = arg

    if framework == Framework.KERAS_TENSORFLOW and backend == Backend.CNTK:
        framework = Framework.KERAS_CNTK

    return framework, script_name, experiment_name, training_data, testing_data


def run_exp():
    # Load configuration
    cfg = utils.config.Configuration('configuration.json')

    # Init job name
    job_name = datetime.utcnow().strftime('job_%m_%d_%Y_%H%M%S')

    framework, script, experiment, training_data, testing_data = read_args(sys.argv[1:])

    if script == None:
        exit(2)

    # Choose framework and run experiment
    if framework == Framework.KERAS_TENSORFLOW:
        exp.create_keras_exp(cfg, script, experiment, job_name, 'tensorflow')
    elif framework == Framework.KERAS_CNTK:
        exp.create_keras_exp(cfg, script, experiment, job_name, 'cntk')
    elif framework == Framework.CNTK:
        exp.create_cntk_exp(cfg, script, experiment, job_name, [training_data, testing_data])


read_args(sys.argv[1:])
run_exp()

# Experiment
#experiment_name='myexperiment'
#job_name = datetime.utcnow().strftime('job_%m_%d_%Y_%H%M%S')

#cfg = utils.config.Configuration('configuration.json')

# create keras mnist exp
#exp.create_keras_exp(cfg, 'mnist_cnn.py', experiment_name, job_name, 'cntk')

# create cntk mnist exp
#exp.create_cntk_exp(cfg, 'ConvNet_MNIST.py', experiment_name, job_name, ['Train-28x28_cntk_text.txt', 'Test-28x28_cntk_text.txt', ])


# Delete resources
#client.jobs.delete(workspace_resource_group, workspace, experiment_name, job_name)
#client.clusters.delete(workspace_resource_group, workspace, cluster)
#resource_management_client.resource_groups.delete('myresourcegroup')


