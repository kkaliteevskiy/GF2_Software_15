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
        self.line = None
        self.position = None


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
        self.file = self.open_file(path)
        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS, self.DOT, self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(8)
        self.keywords_list = ['DEF', 'CON', 'MONITOR'] # add a END keyword?
        # to be defined or add into keywords list
        # self.devicetypes = 
        # self.inputs = 
        # self.outputs = 
        [self.DEF_ID, self.CONNECT_ID, self.MONITOR_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ''


    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()

        if self.current_character.isalpha(): # NAME or KEYWORD
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER
        
        elif self.current_character == '=':
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ',':
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ';':
            symbol.type = self.SEMICOLON
            self.advance()
        
        elif self.current_character == '.':
            symbol.type = self.DOT
            self.advance()
        
        elif self.current_character == '': # end of file
            symbol.type = self.EOF

        else:
            self.advance()

    def open_file(path):
        """Open the specified file and return a file object."""
        try:
            file = open(path, 'r')
            return file
        except FileNotFoundError:
            print(f"Error: File '{path}' not found.")
            return None
        
    def print_error(self, line, position):
        """Print the current input line with a marker to show the error position."""
        print(line)
        print(' ' * (position - 1) + '^')
        print(f"Error: Invalid character '{self.current_character}' at line {line} position {position}.")  

    def skip_spaces(self):
        """Skip over spaces and line breaks until current_character is not whitespace."""
        while self.current_character.isspace():
            self.advance()

    def advance(self):
        """Read the next character from the definition file and place it in current_character."""
        self.current_character = self.file.read(1)

    def get_name(self, input_file):
        """
        Return the next name string in input file and place the next non alphanumeric character in current_character.
        Return none if no name is found and an empty string in current_character if end of file is reached.
        """
    
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
        """
        Seek the next number in input_file.
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
