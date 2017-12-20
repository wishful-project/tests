import os
import pytest
import wishful_module_gitar
import wishful_module_generic
import wishful_module_ipv6
import wishful_module_taisc
import wishful_module_lpl_csma
import wishful_module_nullrdc_csma
import subprocess
from logging import log

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2017, Ghent University - imec - idlab"
__version__ = "0.1.0"
__email__ = "peter.ruckebusch@ugent.be"


def skip_if_no_contiki_devices():
    motelist_output = subprocess.check_output(["../../agent_modules/contiki/communication_wrappers/bin/motelist", "-c"], universal_newlines=True).strip()
    if motelist_output == "No devices found.":
        # check if there are cooja devices!
        try:
            cooja_devs = subprocess.check_output("ls -1v /dev/cooja_rm090* 2>/dev/null", shell=True, universal_newlines=True).strip().split("\n")
            if len(cooja_devs) > 0:
                return True
        except subprocess.CalledProcessError:
            log.info("There are no sensor nodes attached to this machine, and there are no cooja devices, cannot start!!!")
            return False
    else:
        try:
            wilab_nodes_output = subprocess.check_output(["ls /dev/rm090"], universal_newlines=True).strip()
        except FileNotFoundError:
            wilab_nodes_output = ""
        if "/dev/rm090" in wilab_nodes_output:
            return True
        else:
            for line in motelist_output.split("\n"):
                mote_description = line.split(",")[2]
                if "Zolertia RE-Mote" in mote_description:
                    return True
                elif "RM090" in mote_description:
                    return True
    return False


# skip all tests from this pytest module
# if no WiFi devices are present on host
pytestmark = pytest.mark.skipif(skip_if_no_contiki_devices(),
                                reason="No Contiki Device was found")


def get_device_phyid(iface):
    ''' get phy id for this interface '''
    fn = '/sys/class/net/{}/phy80211/name'.format(iface)
    if (os.path.isfile(fn)):
        fd = open(fn, 'r')
        dat = fd.read()
        fd.close()
        phyid = dat.strip()
        return phyid
    return None




@pytest.fixture(scope='module')
def my_contiki_module(request):
    # Create module
    class ContikiModule():
        def __init__(self):
            supported_interfaces = ['lowpan0']
            gc_attributes = []
            gc_functions = []
            ipv6_attributes = {ipv6_connector: './config/protocol_connectors/ipv6_ctrl_attributes.csv' ,rpl_connector: './config/protocol_connectors/rpl_ctrl_attributes.csv'}
            ipv6_functions = {}
            lpl_attributes = []
            lpl_functions = []
            taisc_attributes = []
            taisc_functions = []
            nullrdc_attributes = []
            nullrdc_functions = []
            self.gitar_engine = wishful_module_gitar.GitarEngine(SupportedInterfaces=supported_interfaces)
            self.generic_connector = wishful_module_generic.GenericConnector(SupportedInterfaces=supported_interfaces, ProtocolAttributes = gc_attributes, ProtocolFunctions=gc_functions)
            
    
    
    module.interface = wInterface
    module.wlan_interface = wInterface
    module.phy = get_device_phyid(wInterface)
    return module


def test_module_initialization(my_contiki_module):
    print("WiFi interface name: {}".format(my_wifi_module.interface))
    print("WiFi phy device name: {}".format(my_wifi_module.phy))
    assert my_wifi_module is not None


def test_set_channel(my_wifi_module):
    channel = my_wifi_module.get_channel()
    channel = (channel + 3) % 10
    my_wifi_module.set_channel(channel)
    rChannel = my_wifi_module.get_channel()
    assert channel == rChannel
