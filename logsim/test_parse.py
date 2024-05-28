import pytest
from names import Names
from scanner import Scanner
from parse import Parser
from devices import Devices
from network import Network
from monitors import Monitors
from unittest.mock import mock_open, patch

@pytest.fixture
def new_names():
    return Names()

@pytest.fixture
def devices(new_names):
    return Devices(new_names)

@pytest.fixture
def network(new_names, devices):
    return Network(new_names, devices)

@pytest.fixture
def monitor(new_names, devices, network):
    return Monitors(new_names, devices, network)

@pytest.fixture
def scanner(new_names):
    return Scanner("logic_definition.txt", new_names)

@pytest.fixture
def new_parser(new_names, devices, network, monitor, scanner):
    return Parser(new_names, devices, network, monitor, scanner)

def test_parse_network():
    pass

def test_parse_network_raises_exception():
    pass

def test_parse_def():
    pass

def test_parse_def_raises_exception():
    pass

def test_parse_con():
    pass

def test_parse_con_raises_exception():
    pass

def test_parse_monitor():
    pass

def test_parse_monitor_raises_exception():
    pass

def test_parse_and():
    pass

def test_parse_and_raises_exception():
    pass

def test_parse_or():
    pass

def test_parse_or_raises_exception():
    pass

def test_parse_nor():
    pass

def test_parse_nor_raises_exception():
    pass

def test_parse_nand():
    pass

def test_parse_nand_raises_exception():
    pass

def test_parse_xor():
    pass

def test_parse_xor_raises_exception():
    pass

def test_parse_dtype():
    pass

def test_parse_dtype_raises_exception():
    pass

def test_parse_clock():
    pass

def test_parse_clock_raises_exception():
    pass

def test_parse_switch():
    pass

def test_parse_switch_raises_exception():
    pass

def test_error():
    pass