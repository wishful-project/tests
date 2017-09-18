import pytest
from wishful_framework.classes import exceptions
import wishful_module_simple

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2017, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


@pytest.fixture(scope='module')
def my_simple_module(request):
    # Create module
    module = wishful_module_simple.SimpleModule2()
    return module


def test_module_initialization(my_simple_module):
    assert my_simple_module is not None


def test_channel(my_simple_module):
    channel = 10
    my_simple_module.set_channel(channel)
    rChannel = my_simple_module.get_channel()
    assert rChannel == channel


def test_tx_power(my_simple_module):
    print("Simple module created")
    txPower = 11
    my_simple_module.set_tx_power(txPower)
    rTxPower = my_simple_module.get_power()
    assert rTxPower == txPower


def test_exeption_handling(my_simple_module):
    try:
        my_simple_module.clean_per_flow_tx_power_table()
    except Exception as e:
        print("Exception type: ", type(e))
        assert type(e) == exceptions.UPIFunctionExecutionFailedException
