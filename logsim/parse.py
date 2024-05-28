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
            if self.names.get_name_string(symbol.id) in self.scanner.keywords_list:
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
        EBNF: device = 'DEF', devicename, '=', devicetype, deviceproperty, ';' ;'''

        device_name = None
        device_kind = None
        device_property = None
        device_id = None
        
        symbol = self.scanner.get_symbol()
        # expected devicename 
        if symbol.type == self.scanner.NAME:
            device_id = symbol.id
            # device_name = self.names.get_name_string(symbol.id)
            if self.devices.get_device(device_id) != None:
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
        if self.names.get_name_string(symbol.id) in self.scanner.devices_list:
            device_kind_id = symbol.id#expect this to be a string like "AND"
        else:
            self.error('Error: Expected device type.')

        if self.names.get_name_string(device_kind_id) == 'AND':
            self.parse_and(device_id, self.devices.AND)
        elif self.names.get_name_string(device_kind_id) == 'OR':
            self.parse_or(device_id, self.devices.OR)
        elif self.names.get_name_string(device_kind_id) == 'NOR':
            self.parse_nor(device_id, self.devices.NOR)
        elif self.names.get_name_string(device_kind_id) == 'NAND':
            self.parse_nand(device_id, self.devices.NAND)
        elif self.names.get_name_string(device_kind_id) == 'XOR':
            self.parse_xor(device_id, self.devices.XOR)
        elif self.names.get_name_string(device_kind_id) == 'DTYPE':
            self.parse_dtype(device_id, self.devices.D_TYPE)
        elif self.names.get_name_string(device_kind_id) == 'CLOCK':
            self.parse_clock(device_id, self.devices.CLOCK)
        elif self.names.get_name_string(device_kind_id) == 'SWITCH':
            self.parse_switch(device_id, self.devices.SWITCH)
        else:
            self.error('Error: Unknown device type: ', device_kind)


        return True

    def parse_con(self):
        '''connection = 'CON', devicename, ['.', output], '->', devicename, '.',  input, ';'; '''
        output_device = None
        output_device_id = None
        input_device = None
        input_device_id = None
        output_port_id = None
        input_port_id = None

        symbol = self.scanner.get_symbol()
        output_device = self.devices.get_device(symbol.id)
        output_device_id = symbol.id

        # expected devicename 
        if symbol.type == self.scanner.NAME:
            if self.devices.get_device(symbol.id) != None:#check device is in the devices list
                #DTYPE is the only device that needs to be handled differently
                if output_device.device_kind == self.devices.D_TYPE:
                    #get output pin
                    symbol = self.scanner.get_symbol()
                    if symbol.type == self.scanner.DOT:
                        pass
                    else:
                        self.error('Error: Expected "."')
                    
                    symbol = self.scanner.get_symbol()
                    if self.names.get_name_string(symbol.id) in self.scanner.outputs_list:
                        output_port_id = symbol.id
                    else:
                        self.error('Error: Expected DTYPE output pin ')
                else:# all other devices have 1 output
                    output_port_id = None # TODO how are outputs labeled
                
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
                    input_device_id = symbol.id
                    if input_device != None:
                        #get input pin
                        symbol = self.scanner.get_symbol()
                        if symbol.type == self.scanner.DOT:
                            pass
                        else:
                            self.error('Error: Expected "."')
                        
                        symbol = self.scanner.get_symbol()
                        if symbol.id in input_device.inputs.keys():# TODO how do we do this???? I think this should work now
                            input_port_id = symbol.id
                        else:
                            self.error('Error: Expected input pin ')
                    else:
                        self.error('Error: Device not defined.')
                else:
                    self.error('Error: invalid device name: ...')

                self.network.make_connection(output_device_id, output_port_id, input_device_id, input_port_id)
            else:
                self.error('Error: Device not defined.')
        else:
            self.error('Error: invalid device name: ...')

        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')

        return True

    def parse_monitor(self):
        monitor_device_id = None
        monitor_port_id = None

        symbol = self.scanner.get_symbol()
        # expected devicename 
        if symbol.type == self.scanner.NAME:
            input_device = self.devices.get_device(symbol.id)
            monitor_device_id = symbol.id
            if input_device != None:
                pass
            else:
                self.error('Error: Device not defined.')
        else:
            self.error('Error: invalid device name: ...')

        #if the device is a DTYPE, we need to handle the output pin
        if input_device.device_kind == self.devices.D_TYPE:
            # expected '.'
            symbol = self.scanner.get_symbol()
            if symbol.type == self.scanner.DOT:
                pass
            else:
                self.error('Error: Expected "."')

            # expected output pin
            symbol = self.scanner.get_symbol()
            if self.names.get_name_string(symbol.id) in self.scanner.outputs_list:
                monitor_port_id = symbol.id
            else:
                self.error('Error: Expected pin number')

        self.monitors.make_monitor(monitor_device_id, monitor_port_id)
        
        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')
        

        return True


    #parse devices
    def parse_and(self, device_id, device_kind):

        symbol = self.scanner.get_symbol()

        if symbol.type == self.scanner.NUMBER:
            # number of gates
            no_of_inputs = int(symbol.id)
            if no_of_inputs >= 1 and no_of_inputs <= 16:
                self.devices.make_device(device_id, device_kind, no_of_inputs)
            else:
                self.error('Error: expected number of input pins 1-16')
        else:
            self.error('Error: expected number of input pins 1-16')
    
        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')
        return True

    def parse_or(self, device_id, device_kind):
        
        symbol = self.scanner.get_symbol()
        if symbol == self.scanner.NUMBER:
            no_of_inputs = int(symbol.id)
            if no_of_inputs >= 1 and no_of_inputs <= 16:
                self.devices.make_device(device_id, device_kind, no_of_inputs)
            else:
                self.error('Error: expected number of input pins 1-16')
        else:
            self.error('Error: expected number of input pins 1-16')

        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')
        return True

    def parse_nor(self, device_id, device_kind):

        symbol = self.scanner.get_symbol()
        if symbol == self.scanner.NUMBER:
            no_of_inputs = int(symbol.id)
            if no_of_inputs >= 1 and no_of_inputs <= 16:
                self.devices.make_device(device_id, device_kind, no_of_inputs)
            else:
                self.error('Error: expected number of input pins 1-16')
        else:
            self.error('Error: expected number of input pins 1-16')

        symbol.type = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')
        return True


    def parse_nand(self, device_id, device_kind):
        
        symbol = self.scanner.get_symbol()
        if symbol == self.scanner.NUMBER:
            no_of_inputs = int(symbol.id)
            if no_of_inputs >= 1 and no_of_inputs <= 16:
                self.devices.make_device(device_id, device_kind, no_of_inputs)
            else:
                self.error('Error: expected number of input pins 1-16')
        else:
            self.error('Error: expected number of input pins 1-16')

        symbol.type = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')
        
        return True


    def parse_xor(self, device_id, device_kind):

        self.devices.make_device(device_id, device_kind)

        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')
    
    def parse_dtype(self, device_id, device_kind):

        self.devices.make_device(device_id, device_kind)

        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')

    def parse_clock(self, device_id, device_kind):
        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.NUMBER:
            half_period = int(symbol.id)
            self.devices.make_device(device_id, device_kind, half_period)
        else:
            self.error('Error: expected half period of type INT')

        symbol = self.scanner.get_symbol()

        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')

    def parse_switch(self, device_id, device_kind):

        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.NUMBER:
            state = int(symbol.id)
            if state == 0 or state == 1:
                pass
            else:
                self.error('Error: expected state 0 or 1')

            self.devices.make_device(device_id, device_kind, state)
        else:
            self.error('Error: expected state 0 or 1')
        
        symbol = self.scanner.get_symbol()
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.error('Error: expected ";"')

    def error(self, message):
        print('Error on line :', self.scanner.current_line)
        print(message)
        symbol = self.scanner.get_symbol()
        while symbol.type != self.scanner.SEMICOLON and symbol.type != self.scanner.EOF:
            symbol = self.scanner.get_symbol()

   
        
