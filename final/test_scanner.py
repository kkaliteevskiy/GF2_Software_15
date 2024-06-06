import pytest
from names import Names
from scanner import Scanner, Symbol
from unittest.mock import mock_open, patch


@pytest.fixture
def new_names():
    return Names()


@pytest.fixture
def new_symbol():
    return Symbol()


@pytest.fixture
def scanner(new_names):
    mock_file_content = 'DEF G1 = AND 2;\nDEF Q1=DTYPE\nCON Q1.Q\
          -> AND.I1;#trial run\nCON'
    with patch("builtins.open",
               mock_open(read_data=mock_file_content)) as mock_file:
        return Scanner("path/to/definition/file", new_names)


@pytest.fixture
def scanner_edge(new_names):
    mock_file_content = 'DEF      G1$  &ab== AND 2; This CON I '
    with patch(
        "builtins.open", mock_open(read_data=mock_file_content)
    ) as mock_file:
        return Scanner("path/to/definition/file", new_names)


@pytest.fixture
def scanner_file(new_names):
    return Scanner("example_1.txt", new_names)


def test_scanner_initial(scanner):
    assert scanner.names.query('DEF') == 0
    assert scanner.names.lookup(['CON', 'DEF', 'MONITOR']) == [1, 0, 2]
    assert scanner.names.lookup(['Q', 'QBAR']) == [16, 17]
    assert scanner.names.lookup(['G1', 'G2']) == [19, 20]
    assert scanner.names.get_name_string(14) == 'SET'


def test_scanner_raises_exception(new_names):
    with pytest.raises(FileNotFoundError):
        Scanner('abc.txt', new_names)


def test_get_symbol_1(scanner):
    symbol = scanner.get_symbol()  # DEF
    string = scanner.names.get_name_string(symbol.id)
    assert string == "DEF"
    assert symbol.type == scanner.KEYWORD
    assert symbol.line == 1
    assert symbol.position == 3

    symbol = scanner.get_symbol()  # G1
    def_string = scanner.names.get_name_string(symbol.id)
    assert def_string == "G1"
    assert symbol.type == 9
    assert symbol.type == scanner.NAME
    assert symbol.line == 1
    assert symbol.position == 6

    symbol = scanner.get_symbol()  # =
    assert symbol.id is None
    assert symbol.type == scanner.EQUALS

    symbol = scanner.get_symbol()  # AND
    symbol = scanner.get_symbol()  # 2
    symbol = scanner.get_symbol()  # ;
    symbol = scanner.get_symbol()  # DEF
    symbol = scanner.get_symbol()  # Q1
    symbol = scanner.get_symbol()  # =
    symbol = scanner.get_symbol()  # DTYPE
    assert symbol.id == 10
    assert symbol.type == scanner.DEVICE


def test_get_symbol_2(scanner_file):
    # check it skips comment line
    symbol = scanner_file.get_symbol()  # DEF
    string = scanner_file.names.get_name_string(symbol.id)
    assert string == "DEF"
    assert isinstance(symbol, Symbol)
    assert symbol.type == scanner_file.KEYWORD

    symbol = scanner_file.get_symbol()  # G1
    string = scanner_file.names.get_name_string(symbol.id)
    assert string == "G1"
    assert symbol.type == 9
    assert symbol.type == scanner_file.NAME


# 'DEF      G1$  &ab== AND 2; This CON I '
def test_get_symbol_3(scanner_edge):
    symbol = scanner_edge.get_symbol()  # DEF
    symbol = scanner_edge.get_symbol()  # G1
    def_string = scanner_edge.names.get_name_string(symbol.id)
    assert def_string == "G1"
    assert symbol.type == scanner_edge.NAME

    symbol = scanner_edge.get_symbol()  # $
    assert symbol.type is None
    assert symbol.id is None
    assert symbol.line == 1
    assert symbol.position == 12

    symbol = scanner_edge.get_symbol()  # &
    assert symbol.type is None
    assert symbol.id is None
    assert symbol.line == 1
    assert symbol.position == 15

    symbol = scanner_edge.get_symbol()  # ab
    assert symbol.line == 1
    assert symbol.position == 17

    symbol = scanner_edge.get_symbol()  # =
    assert symbol.line == 1
    assert symbol.position == 18

    symbol = scanner_edge.get_symbol()  # =
    assert symbol.line == 1
    assert symbol.position == 19

    symbol = scanner_edge.get_symbol()  # AND
    assert symbol.type == scanner_edge.DEVICE
    assert symbol.id == 5
    assert symbol.line == 1
    assert symbol.position == 23


def test_open_file(scanner):
    scanner.file.read(1) == 'D'
    assert scanner.current_character == ' '


def test_skip_spaces(scanner):
    # scanner.current_character initialised to ""
    scanner.advance()  # scanner.current_character = "D"
    scanner.advance()  # scanner.current_character = "E"
    scanner.advance()  # scanner.current_character = "F"
    scanner.advance()  # scanner.current_character = " "
    scanner.skip_spaces()
    assert scanner.current_character == 'G'


def test_skip_line_break(scanner):
    scanner.advance()  # scanner.current_character = "D"
    scanner.advance()  # scanner.current_character = "E"
    scanner.advance()  # scanner.current_character = "F"
    scanner.advance()  # scanner.current_character = " "
    scanner.advance()  # scanner.current_character = "G"
    scanner.advance()  # scanner.current_character = "1"
    scanner.advance()  # scanner.current_character = " "
    scanner.advance()  # scanner.current_character = "="
    scanner.advance()  # scanner.current_character = " "
    scanner.advance()  # scanner.current_character = "A"
    scanner.advance()  # scanner.current_character = "N"
    scanner.advance()  # scanner.current_character = "D"
    scanner.advance()  # scanner.current_character = " "
    scanner.advance()  # scanner.current_character = "2"
    scanner.advance()  # scanner.current_character = ";"
    scanner.advance()  # scanner.current_character = "\n"
    scanner.skip_spaces()
    assert scanner.current_character == 'D'


def test_advance(scanner):
    # scanner.current_character initialised to " "
    scanner.advance()  # scanner.current_character = "D"
    assert scanner.current_character == "D"


def test_get_name(scanner):
    scanner.current_character = "a"
    name = scanner.get_name()
    assert isinstance(name, str)
    assert name == "aDEF"


def test_get_number(scanner):
    scanner.current_character = "1"
    number = scanner.get_number()
    assert number == "1"
