import os
import pytest
import pyric             # pyric errors
import pyric.pyw as pyw  # iw functionality
import wishful_module_wifi

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2017, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


def skip_if_no_wifi_devices():
    wInterfaces = pyw.winterfaces()  # get all system wireless interfaces
    if len(wInterfaces) == 0:
        return True
    else:
        return False


# skip all tests from this pytest module
# if no WiFi devices are present on host
pytestmark = pytest.mark.skipif(skip_if_no_wifi_devices(),
                                reason="No WiFi Device was found")


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
def my_wifi_module(request):
    # Create module
    module = wishful_module_wifi.WifiModule()
    wInterfaces = pyw.winterfaces()
    wInterface = wInterfaces[0]
    module.interface = wInterface
    module.wlan_interface = wInterface
    module.phy = get_device_phyid(wInterface)
    return module


def test_module_initialization(my_wifi_module):
    print("WiFi interface name: {}".format(my_wifi_module.interface))
    print("WiFi phy device name: {}".format(my_wifi_module.phy))
    assert my_wifi_module is not None


def test_set_channel(my_wifi_module):
    channel = my_wifi_module.get_channel()
    channel = (channel + 3) % 10
    my_wifi_module.set_channel(channel)
    rChannel = my_wifi_module.get_channel()
    assert channel == rChannel
