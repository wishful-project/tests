import os
import yaml
from common.local_agent_managers import *
from common.remote_agent_managers import *

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2017, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


def get_remote_hosts_dict():
    remote_hosts = {}

    dir_path = os.path.dirname(os.path.realpath(__file__))
    f = open(dir_path + "/remote_hosts.yaml")
    remote_hosts = yaml.load(f)

    return remote_hosts


def skip_if_not_enough_remote_nodes(nodeType, requiredNodeNum):
    remote_hosts_yaml = get_remote_hosts_dict()
    nodeNum = 0
    if remote_hosts_yaml and nodeType in remote_hosts_yaml:
        nodeNum = len(remote_hosts_yaml[nodeType])

    print("Number of available '{}' nodes: {}".format(nodeType, nodeNum))

    if nodeNum < requiredNodeNum:
        return True
    else:
        return False
