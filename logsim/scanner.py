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
        self.symbol_type_list = [self.SEMICOLON, self.EQUALS, self.DOT, self.ARROW, 
                                 self.KEYWORD, self.DEVICE, self.INPUT, self.OUTPUT, 
                                 self.NUMBER, self.NAME, self.EOF] = range(8)
        self.keywords_list = ['DEF', 'CON', 'MONITOR'],           
        self.devices_list = ['CLOCK', 'SWITCH', 'AND', 'NAND', 'OR', 'NOR', 'XOR', 'DTYPE']                     
        self.inputs_list = ['I', 'DATA', 'CLK', 'SET', 'RESET']
        self.outputs_list = ['Q', 'QBAR']
        # add the keywords into name table
        [self.DEF_ID, self.CONNECT_ID, self.MONITOR_ID] = self.names.lookup(self.keywords_list)
        [self.CLOCK_ID, self.SWITCH_ID, self.AND_ID, self.NAND_ID, self.OR_ID, self.NOR_ID, self.XOR_ID, self.DTYPE_ID] = self.names.lookup(self.devices_list)
        [self.I_ID, self.DATA_ID, self.CLK_ID, self.SET_ID, self.RESET_ID] = self.names.lookup(self.outputs_list)
        [self.Q_ID, self.QBAR_ID] = self.names.lookup(self.inputs_list)

        self.current_character = ''
        self.current_line = 0
        self.character_number = 0


    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces()
        symbol.line, symbol.position = self.find_character_position() # to modify

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
        """reads one further character into the document"""
        '''
        if self.read_as_string:
            try:
                self.current_character = self.input_file[self.character_count]
            except IndexError:
                self.current_character = ""
                return self.current_character
            self.character_count += 1
        else:
            self.current_character = self.input_file.read(1)
        '''
        self.current_character = self.file.read(1)
        self.character_number += 1

        if self.current_character == '\n':
            self.current_line += 1
            self.character_number = 0

        return self.current_character

    def get_name(self):
        """
        Return the next name string in input file and place the next non alphanumeric character in current_character.
        Return none if no name is found and an empty string in current_character if end of file is reached.
        """
    
        name = self.current_character
        while True:
            self.current_character = self.advance()
            if self.current_character.isalnum():
                name = name + self.current_character
            else:
                return [name, self.current_character]
        '''
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
        '''
    
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
                return [number, self.current_character]
        '''
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
        '''