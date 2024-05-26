
import pytest
from names import Names
from scanner import Scanner, Symbol
from unittest.mock import mock_open, patch


@pytest.fixture
def scanner():
    names = Names()
    mock_file_content = 'DEF G1 = AND 2;\nDEF Q1=DTYPE\nCON Q1.Q -> AND.I1'
    with patch("builtins.open", mock_open(read_data=mock_file_content)) as mock_file:
        return Scanner("path/to/definition/file", names)

def test_get_symbol(scanner):
    # Assuming that the first symbol in your mock file content is 'DEF'
    symbol = scanner.get_symbol()
    print(f"Symbol id: {symbol.id}, Symbol type: {symbol.type}")
    def_string = scanner.names.get_name_string(symbol.id)
    assert def_string == "DEF"
    assert isinstance(symbol, Symbol)
    #assert symbol.type == scanner.KEYWORD
    

def test_open_file(scanner):
    file = scanner.open_file("path/to/definition/file")
    assert scanner.current_character == ""

def test_skip_spaces(scanner):
    # scanner.current_character initialised to ""
    scanner.advance() # scanner.current_character = "D"
    scanner.advance() # scanner.current_character = "E"
    scanner.advance() # scanner.current_character = "F"
    scanner.advance() # scanner.current_character = " "
    scanner.skip_spaces()
    assert scanner.current_character == 'G'

def test_skip_line_break(scanner):
    scanner.advance() # scanner.current_character = "D"
    scanner.advance() # scanner.current_character = "E"
    scanner.advance() # scanner.current_character = "F"
    scanner.advance() # scanner.current_character = " "
    scanner.advance() # scanner.current_character = "G"
    scanner.advance() # scanner.current_character = "1"
    scanner.advance() # scanner.current_character = " "
    scanner.advance() # scanner.current_character = "="
    scanner.advance() # scanner.current_character = " "
    scanner.advance() # scanner.current_character = "A"
    scanner.advance() # scanner.current_character = "N"
    scanner.advance() # scanner.current_character = "D"
    scanner.advance() # scanner.current_character = " "
    scanner.advance() # scanner.current_character = "2"
    scanner.advance() # scanner.current_character = ";"
    scanner.advance() # scanner.current_character = "\n"
    scanner.skip_spaces()
    assert scanner.current_character == 'D'

def test_advance(scanner):
    #scanner.current_character initialised to ""
    scanner.advance() # scanner.current_character = "D"
    assert scanner.current_character == "D"

def test_get_name(scanner):
    scanner.current_character = "a"
    name = scanner.get_name()
    assert isinstance(name, str)

def test_get_number(scanner):
    scanner.current_character = "1"
    number = scanner.get_number()
    assert number == "1"