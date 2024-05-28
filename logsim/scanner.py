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
        self.path = path
        self.names = names
        self.symbol_type_list = [self.SEMICOLON, self.EQUALS, self.DOT, self.ARROW, 
                                 self.KEYWORD, self.DEVICE, self.INPUT, self.OUTPUT, 
                                 self.NUMBER, self.NAME, self.EOF] = range(11)
        self.keywords_list = ['DEF', 'CON', 'MONITOR']           
        self.devices_list = ['CLOCK', 'SWITCH', 'AND', 'NAND', 'OR', 'NOR', 'XOR', 'DTYPE']                     
        self.inputs_list = ['I', 'DATA', 'CLK', 'SET', 'CLEAR']
        self.outputs_list = ['Q', 'QBAR']
        # add the keywords into name table
        [self.DEF_ID, self.CONNECT_ID, self.MONITOR_ID] = self.names.lookup(self.keywords_list)
        [self.CLOCK_ID, self.SWITCH_ID, self.AND_ID, self.NAND_ID, self.OR_ID, self.NOR_ID, self.XOR_ID, self.DTYPE_ID] = self.names.lookup(self.devices_list)
        [self.I_ID, self.DATA_ID, self.CLK_ID, self.SET_ID, self.CLEAR_ID] = self.names.lookup(self.inputs_list)
        [self.Q_ID, self.QBAR_ID] = self.names.lookup(self.outputs_list)

        self.current_character = ' '
        self.current_line = 0
        self.character_number = -1


    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()

        if self.current_character.isalpha(): # NAME or KEYWORD or device or i/o
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            elif name_string in self.devices_list:
                symbol.type = self.DEVICE
            elif name_string in self.inputs_list:
                symbol.type = self.INPUT
            elif name_string in self.outputs_list:
                symbol.type = self.OUTPUT
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string]) # returns terminal IDs or add names to table, but why is this a list?

        elif self.current_character.isdigit(): # number
            symbol.id = self.get_number() # symbol ID is the number (don't need ID for number, not in name table)
            symbol.type = self.NUMBER
        
        elif self.current_character == '=':
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ';':
            symbol.type = self.SEMICOLON
            self.advance()
        
        elif self.current_character == '.':
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == '-':
            self.advance()
            if self.current_character == '>':
                symbol.type = self.ARROW
                self.advance()
            else:
                self.advance()
        
        elif self.current_character == '': # end of file
            symbol.type = self.EOF

        else:
            self.advance()
        
        symbol.line, symbol.position = self.current_line, self.character_number
        return symbol

    def open_file(self, path):
        """Open the specified file and return a file object."""
        try:
            return open(path, 'r')  # Return file object
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{path}' not found.")


    def print_error(self):
        """Print the current input line with a marker to show the error position."""
        new_file = open(self.path, 'r')
        lines = new_file.readlines()
        error_line = lines[self.current_line]
        print(self.current_line)
        print(error_line)
        print(' ' * (self.character_number - 1) + '^')
        print(f"Error: Invalid character '{self.current_character}' at line {self.current_line} position {self.character_number}.")  

    def skip_spaces(self):
        """Skip over spaces and line breaks until 
        current_character is not whitespace."""
        while True:
            if self.current_character.isspace():
                self.advance()
            # skip comment line
            elif self.current_character == '#':
                while self.current_character != '\n':
                    self.advance()
                self.advance()
            else:
                break


    def advance(self):
        """reads one further character into the document"""
        self.current_character = self.file.read(1)
        self.character_number += 1

        if self.current_character == '\n':
            self.current_line += 1
            self.character_number = 0
        #print(self.character_number)
        return self.current_character

    def get_name(self):
        """
        Return the next name string in input file and place the next non alphanumeric character in current_character.
        Return none if no name is found and an empty string in current_character if end of file is reached.
        """
    
        name = self.current_character
        while True:
            self.current_character = self.advance()
            if self.current_character.isalnum() or self.character_number == '_':
                name = name + self.current_character
            else:
                return name
            
    
    def get_number(self):
        """
        Seek the next number in input_file.
        Return the number (or None) and the next non-numeric character.
        """
        number = self.current_character
        while True:
            self.current_character = self.advance()
            if self.current_character.isdigit():
                number = number + self.current_character
            else:
                return number