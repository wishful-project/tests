import os
import time
import datetime
import gevent
import pytest
import wishful_controller
import wishful_upis as upis
from conftest import get_remote_hosts_dict, skip_if_not_enough_remote_nodes

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2017, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"

dir_path = os.path.dirname(os.path.realpath(__file__))
nodes = []

# skip all tests from this pytest module
# if there is less than two remote nodes
pytestmark = pytest.mark.skipif(skip_if_not_enough_remote_nodes("hosts", 2),
                                reason="Need at least 2 remote nodes")


@pytest.fixture(scope='module')
def my_wishful_controller(request):
    # Create controller
    controller = wishful_controller.Controller(dl="tcp://127.0.0.1:8990",
                                               ul="tcp://127.0.0.1:8989")
    # Configure controller
    controller.set_controller_info(name="WishfulController",
                                   info="WishfulControllerInfo")
    controller.add_module(moduleName="discovery",
                          pyModuleName="wishful_module_discovery_pyre",
                          className="PyreDiscoveryControllerModule",
                          kwargs={"iface": "lo",
                                  "groupName": "wishful_1234",
                                  "downlink": "tcp://127.0.0.1:8990",
                                  "uplink": "tcp://127.0.0.1:8989"
                                  }
                          )

    @controller.new_node_callback()
    def new_node(node):
        nodes.append(node)
        print("New node connected: {}".format(node.id))

    @controller.node_exit_callback()
    def node_exit(node, reason):
        if node in nodes:
            nodes.remove(node)
        print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))

    controller.start()
    print('\nWiSHFUL Server started')

    def teardown():
        controller.stop()
        print('\nWiSHFUL Server stopped')

    request.addfinalizer(teardown)
    return controller




def test_controller_initialization(my_wishful_controller):
    print("New WiSHFUL Controller: ", my_wishful_controller.info)
    assert my_wishful_controller.info == 'WishfulControllerInfo'


def test_node_discovery_one_node(my_wishful_controller, remote_agent_manager):
    '''
    Start first agent and let it connect to controller
    Wait 10 seconds to give Agent time to connect
    '''
    remote_hosts_dict = get_remote_hosts_dict()
    print(remote_hosts_dict)
    h0ip = None
    if "hosts" in remote_hosts_dict:
        h0ip = remote_hosts_dict["hosts"][0]["ip"]
    scriptPath = dir_path + "/wishful_simple_agent"
    configPath = dir_path + "/agent_config.yaml"
    remoteAgentHost = remote_agent_manager.create_remote_agent_proxy(h0ip)
    remoteAgentHost.upload_agent_script(scriptPath)
    remoteAgentHost.upload_agent_config(configPath)
    remoteAgentHost.start_remote_agent()

    i = 0
    while i < 10:
        gevent.sleep(1)
        i = i + 1
        if len(nodes) == 1:
            break
    assert len(nodes) == 1


def test_node_discovery_two_nodes(my_wishful_controller, remote_agent_manager):
    '''
    Start second agent and let it connect to controller
    Wait 10 seconds to give Agent time to connect
    '''
    remote_hosts_dict = get_remote_hosts_dict()
    h1ip = None
    if "hosts" in remote_hosts_dict:
        h1ip = remote_hosts_dict["hosts"][1]["ip"]
    scriptPath = dir_path + "/wishful_simple_agent"
    configPath = dir_path + "/agent_config.yaml"
    remoteAgentHost = remote_agent_manager.start_remote_agent(scriptPath,
                                                              configPath,
                                                              h1ip, 567895)
    i = 0
    while i < 10:
        gevent.sleep(1)
        i = i + 1
        if len(nodes) == 2:
            break
    assert len(nodes) == 2


def test_hello_mechanism(my_wishful_controller, remote_agent_manager):
    '''
    Stop one node and check if WiSHFUL controller notice that it is gone
    '''
    agent1 = remote_agent_manager.get_agent(1)
    try:
        agent1.stop()
    except Exception:
        print("exep")
    i = 0
    while i < 10:
        gevent.sleep(1)
        i = i + 1
        if len(nodes) == 1:
            break
    assert len(nodes) == 1


def test_blocking_call(my_wishful_controller):
    '''
    Test blocking call
    '''
    newChannel = my_wishful_controller.node(nodes[0]).radio.iface("wlan1").get_channel()
    newChannel = (newChannel + 1) % 10
    my_wishful_controller.node(nodes[0]).radio.iface("wlan1").set_channel(channel=newChannel)
    result = my_wishful_controller.node(nodes[0]).radio.iface("wlan1").get_channel()

    print("test_blocking_call  -- set channel: ", newChannel, " returned channel: ", result)
    assert newChannel == result


def test_non_blocking_call(my_wishful_controller):
    '''
    Test non blocking call with default callback
    '''
    global callbackExecuted
    global response
    callbackExecuted = False
    response = None
    newChannel = 1

    def default_callback(group, node, cmd, data):
        global callbackExecuted
        callbackExecuted = True
        global response
        response = data

    my_wishful_controller.default_callback = default_callback

    # set new channel with non-blocking call
    my_wishful_controller.blocking(False).node(nodes[0]).radio.iface("wlan1").set_channel(channel=newChannel)
    # wait for callback execution
    i = 0
    while i < 10:
        gevent.sleep(1)
        i = i + 1
        if callbackExecuted:
            break

    assert response == ['SET_CHANNEL_OK', newChannel, 0]

    # get channel with non-blocking call
    callbackExecuted = False
    response = None

    my_wishful_controller.blocking(False).node(nodes[0]).radio.iface("wlan1").get_channel()
    # wait for callback execution
    i = 0
    while i < 10:
        gevent.sleep(1)
        i = i + 1
        if callbackExecuted:
            break
    print("test_non_blocking_call  -- set channel: ", newChannel, " returned channel: ", response)
    assert response == newChannel

def test_non_blocking_call_with_callback(my_wishful_controller):
    '''
    Test non blocking call with default callback
    '''
    global callbackExecuted
    global response
    callbackExecuted = False
    response = None
    newChannel = 10

    def set_channel_callback(group, node, data):
        global callbackExecuted
        callbackExecuted = True
        global response
        response = data

    def get_channel_callback(group, node, data):
        global callbackExecuted
        callbackExecuted = True
        global response
        response = data

    # set new channel with non-blocking call
    my_wishful_controller.callback(set_channel_callback).node(nodes[0]).radio.iface("wlan1").set_channel(channel=newChannel)
    # wait for callback execution
    i = 0
    while i < 10:
        gevent.sleep(1)
        i = i + 1
        if callbackExecuted:
            break

    assert response == ['SET_CHANNEL_OK', newChannel, 0]

    # get channel with non-blocking call
    callbackExecuted = False
    response = None

    my_wishful_controller.callback(get_channel_callback).node(nodes[0]).radio.iface("wlan1").get_channel()
    # wait for callback execution
    i = 0
    while i < 10:
        gevent.sleep(1)
        i = i + 1
        if callbackExecuted:
            break

    print("test_non_blocking_call_with_callback  -- set channel: ", newChannel, " returned channel: ", response)
    assert response == newChannel

def test_delayed_call(my_wishful_controller):
    '''
    Test non blocking call with default callback
    '''
    global callbackExecuted
    global response
    callbackExecuted = False
    response = None
    newChannel = 6

    def set_channel_callback(group, node, data):
        global callbackExecuted
        callbackExecuted = True
        global response
        response = data

    def get_channel_callback(group, node, data):
        global callbackExecuted
        callbackExecuted = True
        global response
        response = data

    # set new channel with delayed non-blocking call
    scheduleWithDelay = 4
    my_wishful_controller.delay(scheduleWithDelay).callback(set_channel_callback).node(nodes[0]).radio.iface("wlan1").set_channel(channel=newChannel)
    # wait for callback execution
    i = 0
    startTime = time.time()
    while i < 1000:
        gevent.sleep(0.01)
        i = i + 1
        if callbackExecuted:
            break
    endTime = time.time()
    delay = endTime-startTime
    assert response == ['SET_CHANNEL_OK', newChannel, 0]
    assert delay >= scheduleWithDelay and delay <= scheduleWithDelay+0.1

    # get channel with delayed non-blocking call
    callbackExecuted = False
    response = None
    scheduleWithDelay = 2
    my_wishful_controller.delay(scheduleWithDelay).callback(get_channel_callback).node(nodes[0]).radio.iface("wlan1").get_channel()
    # wait for callback execution
    i = 0
    startTime = time.time()
    while i < 1000:
        gevent.sleep(0.01)
        i = i + 1
        if callbackExecuted:
            break
    endTime = time.time()
    delay = endTime - startTime
    print("test_delayed_call -- schedule delay: {}, executed with delay: {}".format(scheduleWithDelay, delay))
    assert response == newChannel
    assert delay >= scheduleWithDelay and delay <= scheduleWithDelay+0.1


def test_scheduled_call(my_wishful_controller):
    '''
    Test non blocking call with default callback
    '''
    global callbackExecuted
    global response
    callbackExecuted = False
    response = None
    newChannel = 2

    def set_channel_callback(group, node, data):
        global callbackExecuted
        callbackExecuted = True
        global response
        response = data

    def get_channel_callback(group, node, data):
        global callbackExecuted
        callbackExecuted = True
        global response
        response = data

    # set new channel with delayed non-blocking call
    scheduleWithDelay = 4
    exec_time = datetime.datetime.now() + datetime.timedelta(seconds=scheduleWithDelay)
    my_wishful_controller.exec_time(exec_time).callback(set_channel_callback).node(nodes[0]).radio.iface("wlan1").set_channel(channel=newChannel)
    # wait for callback execution
    i = 0
    startTime = time.time()
    while i < 1000:
        gevent.sleep(0.01)
        i = i + 1
        if callbackExecuted:
            break
    endTime = time.time()
    delay = endTime-startTime
    assert response == ['SET_CHANNEL_OK', newChannel, 0]
    assert delay >= scheduleWithDelay and delay <= scheduleWithDelay+0.1

    # get channel with delayed non-blocking call
    callbackExecuted = False
    response = None
    scheduleWithDelay = 3
    exec_time = datetime.datetime.now() + datetime.timedelta(seconds=scheduleWithDelay)
    my_wishful_controller.exec_time(exec_time).callback(get_channel_callback).node(nodes[0]).radio.iface("wlan1").get_channel()
    # wait for callback execution
    i = 0
    startTime = time.time()
    while i < 1000:
        gevent.sleep(0.01)
        i = i + 1
        if callbackExecuted:
            break
    endTime = time.time()
    delay = endTime - startTime
    print("test_scheduled_call -- schedule delay: {}, executed with delay: {}".format(scheduleWithDelay, delay))
    assert response == newChannel
    assert delay >= scheduleWithDelay and delay <= scheduleWithDelay+0.1
