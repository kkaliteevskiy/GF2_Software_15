import pytest
from names import Names
from scanner import Scanner, Symbol
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
'''
# check all errors are printed    
def test_parse_network_error1(new_names, devices, network, monitor):
    mock_file_content = 'DEF G1 = AND 2;\nDEF Q1=DTYPE\nCON Q1.Q -> AND.I1;#trial run\nCON'
    with patch("builtins.open", mock_open(read_data=mock_file_content)) as mock_file:
        scanner = Scanner("path/to/definition/file", new_names)
    parser = Parser(new_names, devices, network, monitor, scanner)
    assert parser.parse_network() == True
    assert parser.error_list == []
    assert parser.error_count == 0

    # Assert that the output is as expected
    message = "Error: Invalid character ' ' at line 0 position -1.\n# first comment\n^\nExpected keyword DEF, CON or MONITOR.\n"
'''
# in logsim, defined in the order: device, network, monitor, parse - for error code orders
def test_error1(new_names, devices, network, monitor):
    scanner = Scanner("test_files/test1", new_names)
    parser = Parser(new_names, devices, network, monitor, scanner)
    assert parser.parse_network() == True
    # errors: syntax(;), stop before CON
    assert parser.error_list == [parser.SYNTAX_ERROR]
    assert parser.error_count == 1


def test_error2(new_names, devices, network, monitor):
    scanner = Scanner("test_files/test2", new_names)
    parser = Parser(new_names, devices, network, monitor, scanner)
    assert parser.parse_network() == True
    # errors: syntax(command), syntax(command)
    assert parser.error_list == [parser.SYNTAX_ERROR, parser.SYNTAX_ERROR]
    assert parser.error_count == 2


def test_error3(new_names, devices, network, monitor):
    scanner = Scanner("test_files/test3", new_names)
    parser = Parser(new_names, devices, network, monitor, scanner)
    assert parser.parse_network() == True
    # errors: syntax(naming), INVALID_qualifier
    assert parser.error_list == [parser.SYNTAX_ERROR, devices.INVALID_QUALIFIER]
    assert parser.error_count == 2


def test_error4(new_names, devices, network, monitor):
    scanner = Scanner("test_files/test4", new_names)
    parser = Parser(new_names, devices, network, monitor, scanner)
    assert parser.parse_network() == True
    # errors: syntax(=), syntax(=), syntax(=)
    assert parser.error_list == [parser.SYNTAX_ERROR, parser.SYNTAX_ERROR, parser.SYNTAX_ERROR]
    assert parser.error_count == 3


def test_error5(new_names, devices, network, monitor):
    scanner = Scanner("test_files/test5", new_names)
    parser = Parser(new_names, devices, network, monitor, scanner)
    assert parser.parse_network() == True
    # errors: device_present, syntax(device), syntax(device)
    assert parser.error_list == [devices.DEVICE_PRESENT, parser.SYNTAX_ERROR, parser.SYNTAX_ERROR]
    assert parser.error_count == 3


def test_error6(new_names, devices, network, monitor):
    scanner = Scanner("test_files/test6", new_names)
    parser = Parser(new_names, devices, network, monitor, scanner)
    assert parser.parse_network() == True
    # errors: syntax(->), 
    assert parser.error_list == [network.PORT_ABSENT]
    assert parser.error_count == 1


# if inputs not connected, will raise error in terminal


def test_error(new_parser, capsys):
    # Call the function
    new_parser.error(err=0, msg="Alice", symbol=Symbol())
    assert new_parser.error_count == 1
    assert new_parser.error_list == [0]
    captured = capsys.readouterr()
    # Assert that the output is as expected
    message = "Error on line 1 at position -1 : Alice\nDEF G1 = AND 2 ;\n^\n"
    assert captured.out == message