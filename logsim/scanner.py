"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

    def get_name(self, input_file):
        """Return the next name string in input file and place the next non alphanumeric character in current_character."""
        """Return none if no name is found and an empty string in current_character if end of file is reached."""
    
        name = ""

        while True:
            char = input_file.read(1)
            if not char:
                if name:
                    return name
                else:
                    return None  # End of file reached
            if char.isalnum():  # Continuation of a name
                name += char
            else:
                if name:
                    self.current_character = char
                    break
                continue

        return name
    
    def get_number(self, input_file):
        """Seek the next number in input_file.
        Return the number (or None) and the next non-numeric character.
        """
        number = ""

        while True:
            char = input_file.read(1)
            if not char:
                if number:
                    return int(number)
                else:
                    return None  # End of file reached
            if char.isdigit():
                number += char
            else:
                if number:
                    self.current_character = char
                    break
                continue

        return int(number)
