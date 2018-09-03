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
    helper = 'AzureBatch.py -s <script_name> [-e <experiment_name>] [-f <framework>] [-b <backend>] ' \
             '[-t <training_data>,<testing_data>]'
    script_name = None
    dataset = None
    experiment_name = datetime.utcnow().strftime('exp_%m_%d_%Y_%H%M%S')
    framework = Framework.KERAS_TENSORFLOW  # default set Keras Tensorflow
    backend = Backend.TENSORFLOW

    try:
        opts, args = getopt.getopt(argv,"hs:e:f:b:t:",["help"])
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
        elif opt == "-t":
            dataset = arg.split(',')

    if framework == Framework.KERAS_TENSORFLOW and backend == Backend.CNTK:
        framework = Framework.KERAS_CNTK

    return framework, script_name, experiment_name, dataset


def run_exp():
    # Load configuration
    cfg = utils.config.Configuration('configuration.json')

    # Init job name
    job_name = datetime.utcnow().strftime('job_%m_%d_%Y_%H%M%S')

    framework, script, experiment, dataset = read_args(sys.argv[1:])

    if script == None:
        exit(2)

    # Choose framework and run experiment
    if framework == Framework.KERAS_TENSORFLOW:
        exp.create_keras_exp(cfg, script, experiment, job_name, 'tensorflow')
    elif framework == Framework.KERAS_CNTK:
        exp.create_keras_exp(cfg, script, experiment, job_name, 'cntk')
    elif framework == Framework.CNTK:
        exp.create_cntk_exp(cfg, script, experiment, job_name, dataset)


read_args(sys.argv[1:])
run_exp()