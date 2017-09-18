import pytest
from conftest import get_remote_hosts_dict, skip_if_not_enough_remote_nodes


__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2017, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


# skip all tests from this pytest module
# if there is no remote nodes with wifi cards
pytestmark = pytest.mark.skipif(skip_if_not_enough_remote_nodes("wifi", 1),
                                reason="Need at least 1 remote nodes with WiFi")


# skip test if there is less than two wifi nodes available
needTwoWifi = pytest.mark.skipif(skip_if_not_enough_remote_nodes("wifi", 2),
                                 reason="Need at least 2 remote nodes with WiFi")


@needTwoWifi
def test_sta_connects_ap():
    remoteHosts = get_remote_hosts_dict()
    print(remoteHosts)
    print("Create controller and 2 nodes: AP and STA. Make STA to connect to AP")
    pass
