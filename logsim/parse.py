"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        symbol = self.scanner.get_symbol()

        #get the first symbol fo the expression
        while symbol.type != self.scanner.EOF:
            if symbol.type in self.scanner.keywords_list:
                if symbol.id == self.names.query('DEF'):
                    self.parse_def()
                elif symbol.id == self.names.query('CON'):
                    self.parse_con()
                elif symbol.id == self.names.query('MONITOR'):
                    self.parse_monitor()
                else:
                    self.error('Expected keyword DEF, CON or MONITOR. IF you see this message, you are in trouble.')
            else:
                self.error('Expected keyword DEF, CON or MONITOR.')

            symbol = self.scanner.get_symbol()

        return True
    
    def parse_def(self):
        '''Parse the DEF statement
        EBNF: device = ‘DEF’, devicename, '=', devicetype, deviceproperty, ';' ;'''

        device_name = None
        device_type = None
        device_property = None
        device_id = None
        
        symbol = self.scanner.get_symbol()
        # expected devicename 
        if symbol.type == self.scanner.NAME:
            device_id = symbol.id
            # device_name = self.names.get_name_string(symbol.id)
            if self.devices(device_id) == None:
                self.error('Error: Device already defined.')
            else:
                pass 
        else:
            self.error('Error: invalid device name: ...')
        
        # expected '='
        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.EQUALS:
            pass
        else:
            self.error('Error: Expected =')


        # expected devicetype
        symbol = self.scanner.get_symbol()
        if symbol.type in self.scanner.device_types:
            device_type = self.names.get_name_string(symbol.id)
        else:
            self.error('Error: Expected device type.')

        # expected deviceproperty: if deice takes a parameter expect the parameter, else expect ';'
        symbol = self.scanner.get_symbol()

        
        #match device to deviceproperty
        if device_type == 'AND':
            self.parse_and(symbol, device_type)
        elif device_type == 'OR':
            self.parse_or(symbol, device_type)
        elif device_type == 'NOR':
            self.parse_not(symbol, device_type)
        elif device_type == 'NAND':
            self.parse_nand(symbol, device_type)
        elif device_type == 'XOR':
            self.parse_nor(symbol, device_type)
        elif device_type == 'DTYPE':
            self.parse_xor(symbol, device_type)
        elif device_type == 'CLOCK':
            self.parse_xnor(symbol, device_type)
        elif device_type == 'SWITCH':
            self.parse_switch(symbol, device_type)
        else:
            self.error('Error: Unknown device type: ', device_type)


        return True

    def parse_con(self):
        '''connection = 'CON', devicename, ['.', output], '->', devicename, '.',  input, ';'; '''
        output_device = None
        output_pin = None
        input_device = None
        input_pin = None
        

        symbol = self.scanner.get_symbol()

        # expected devicename 
        if symbol.type == self.scanner.NAME:
            output_device = self.devices.get_device(symbol.id)
            if output_device != None:

                #DTYPE is the only device that needs to be handled differently
                if output_device.device_kind == 'DTYPE':

                    #get output pin
                    symbol = self.scanner.get_symbol()
                    if symbol.type == self.scanner.DOT:
                        pass
                    else:
                        self.error('Error: Expected "."')
                    
                    symbol = self.scanner.get_symbol()
                    if symbol.type == self.scanner.OUTPUT:
                        output_pin = symbol.id
                    else:
                        self.error('Error: Expected output pin ')

                # all other devices have 1 output
                
                #check arrow
                symbol = self.scanner.get_symbol()
                if symbol.type == self.scanner.ARROW:
                    pass
                else:
                    self.error('Error: Expected "->"')

                # get input device
                symbol = self.scanner.get_symbol()
                if symbol.type == self.scanner.NAME:
                    input_device = self.devices.get_device(symbol.id)
                    if input_device != None:
                        
                        #get input pin
                        symbol = self.scanner.get_symbol()
                        if symbol.type == self.scanner.DOT:
                            pass
                        else:
                            self.error('Error: Expected "."')
                        
                        symbol = self.scanner.get_symbol()
                        if symbol.type == self.scanner.INPUT:
                            input_pin = symbol.id
                        else:
                            self.error('Error: Expected input pin ')
                    else:
                        self.error('Error: Device not defined.')
                else:
                    self.error('Error: invalid device name: ...')

                # TODO : create connection/signal

                pass
            else:
                self.error('Error: Device not defined.')
        else:
            self.error('Error: invalid device name: ...')

        symbol = self.scanner.get_symbol()
        if symbol == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')


        # # check device type
        # if self.devices.query(output_device):
        #     device_type = self.devices.get_device_type(output_device)

        # # expected '.'
        # symbol = self.scanner.get_symbol()
        # if symbol.type == self.scanner.DOT:
        #     pass
        # else:
        #     self.error('Error: Expected "."')

        # # dtype has more than 1 output need to parse that. THIS CODE SHOULD PARSR THE GATE

        # # expected output pin 
        # symbol = self.scanner.get_symbol()
        # if symbol.type == self.scanner.OUTPUT: # check this
        #     output_pin = symbol.id #perhaps
        # else:
        #     self.error('Error: Expected pin number')
        
        # # expected '->'
        # symbol = self.scanner.get_symbol()
        # if symbol.type == self.scanner.ARROW:
        #     pass
        # else:
        #     self.error('Error: Expected "->"')
        
        # # expected devicename
        # if symbol.type == self.scanner.NAME:
        #     output_device = self.names.get_name_string(symbol.id)
        #     if self.devices.query(output_device):
        #         # TODO: define monitor
        #         pass
        #     else:
        #         self.error('Error: Device not defined.')
        # else:
        #     self.error('Error: nvalid device name: ...')

        # # expected '.'
        # symbol = self.scanner.get_symbol()
        # if symbol.type == self.scanner.DOT:
        #     pass
        # else:
        #     self.error('Error: Expected "."')

        # # expected input pin 
        # symbol = self.scanner.get_symbol()
        # if symbol.type == self.scanner.INPUT:
        #     output_pin = symbol.id
        # else:
        #     self.error('Error: Expected pin number')

        # symbol = self.scanner.get_symbol()
        # if symbol == self.scanner.SEMICOLON:
        #     pass
        # else:
        #     self.error('Error: expected ";"')
        
        # # TODO : define connection/s

        return True

    def parse_monitor(self):
        monitor_device = None
        monitor_pin = None

        symbol = self.scanner.get_symbol()
        # expected devicename 
        if symbol.type == self.scanner.NAME:
            input_device = self.names.get_name_string(symbol.id)
            if self.devices.query(input_device):
                # TODO: define monitor
                pass
            else:
                self.error('Error: Device not defined.')
        else:
            self.error('Error: nvalid device name: ...')

        # expected '.'
        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.DOT:
            pass
        else:
            self.error('Error: Expected "."')

        # expected output pin
        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.PINNUMBER:
            output_pin = symbol.id
        else:
            self.error('Error: Expected pin number')

        # TODO : define monitor

        return True


    #parse devices
    def parse_and(self, symbol, device_type):
        if symbol == self.scanner.DEVICEPROPERTY:

            # TODO: define gate

            symbol = self.scanner.get_symbol()
            if symbol == self.scanner.SEMICOLON:
                pass
            else:
                self.error('Error: expected ";"')
        else:
            self.error('Error: expected number of input pins 1-16')

    def parse_or(self, symbol, device_type):
        if symbol == self.scanner.DEVICEPROPERTY:
           
            # TODO: define gate

            symbol = self.scanner.get_symbol()
            if symbol == self.scanner.SEMICOLON:
                pass
            else:
                self.error('Error: expected ";"')
        else:
            self.error('Error: expected number of input pins 2-16')

    def parse_nor(self, symbol, device_type):
        if symbol == self.scanner.DEVICEPROPERTY:
            
            # TODO: define gate

            symbol = self.scanner.get_symbol()
            if symbol == self.scanner.SEMICOLON:
                pass
            else:
                self.error('Error: expected ";"')

        else:
            self.error('Error: expected number of input pins 2-16')


    def parse_nand(self, symbol, device_type):
        if symbol == self.scanner.DEVICEPROPERTY:
            
            # TODO: define gate

            symbol = self.scanner.get_symbol()
            if symbol == self.scanner.SEMICOLON:
                pass
            else:
                self.error('Error: expected ";"')
        else:
            self.error('Error: expected number of input pins 2-16')


    def parse_xor(self, symbol, device_type):
        if symbol == self.scanner.SEMICOLON:
            
            # TODO: define gate

            pass
        else:
            self.error('Error: expected ";"')
    
    def parse_dtype(self, symbol, device_type):
        if symbol == self.scanner.SEMICOLON:
            
            # TODO: define gate

            pass
        else:
            self.error('Error: expected ";"')

    def parse_clock(self, symbol, device_type):
        if symbol == self.scanner.SEMICOLON:
            
            # TODO: define gate
            pass
        else:
            self.error('Error: expected ";"')

    def error(self, message):
        print(message)
        symbol = self.scanner.get_symbol()
        while symbol.type != self.scanner.SEMICOLON and symbol.type != self.scanner.EOF:
            symbol = self.scanner.get_symbol()

    def parse_switch(self, symbol, device_type):
        if symbol == self.scanner.DEVICEPROPERTY:

            # TODO make switch
             
            symbol = self.scanner.get_symbol()
            if symbol == self.scanner.SEMICOLON:
                pass
            else:
                self.error('Error: expected ";"')
        else:
            self.error('Error: expected state 0 or 1')
        
