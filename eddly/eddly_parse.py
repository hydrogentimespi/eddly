import sys
import re

from sly            import Parser
from .eddly_lex      import Eddl_lexer


class Eddl_parser(Parser):
    #debugfile = 'parser.out'

    tokens = Eddl_lexer.tokens
    start = 'ddl_node_list'

    edd = {}                                    # final dictionary holding entire edd
    text_dictionary = {}

    # TODO optimize to one temp dict,list as likely not used in parallel
    menues = {}
    menu_attribs_dict = {}                      # temp.  attributes within one menu
    menu_itemlist = []

    commands = {}
    command_attribs = {}                        # NUMBER, OPERATION, TRANSACTIONS,...
    command_transactions_dict = {}              # TRANSACTION 1,2,3...
    command_transaction_keywords_dict = {}      # REQUEST, REPLY
    command_transaction_items_list = []         # data items within REQUEST, REPLY
    command_response_codes_dict = {}            # 0, SUCCESS, [no_command_specific_errors];

    variables = {}
    variable_attribs_dict = {}                  # LABEL, CLASS, HANDLING,...
    variable_class_specifiers_list = []
    temp_dict = {}

    manufacturer    = None
    dd_revision     = None
    device_type     = None
    device_revision = None

    def error(self, t):
        # TODO  these tokens are not part of the grammar and reported unused
        #  just consume all tokens following the top level keyword until RCURLY is reached - ignore the whole block
        ignore_keywords = ['IMPORT', 'METHOD', 'UNIT', 'ARRAY', 'GRID', 'AXIS', 'WAVEFORM', 'GRAPH', 'EDIT_DISPLAY', 'WRITE_AS_ONE', 'COLLECTION', 'IF', 'ELSE', 'EDIT_DISPLAY', 'COLLECTION', 'IMAGE']
        if t.type in ignore_keywords:
            seencurly = 0
            curlylevel = 0
            while True:
                t = next(self.tokens, None)  # Get the next token
                if not t:
                    print("Error: end of input reached waiting for '}' - '%s'" % t)
                    sys.exit(2)
                if t.type == 'LCURLY':
                    seencurly = 1
                    curlylevel += 1
                if t.type == 'RCURLY':
                    curlylevel -= 1
                if seencurly and not curlylevel:
                    self.errok()
                    break
            t = next(self.tokens, None)  # Get the next token after RCURLY and continue parsing
            if not t:
                print("end of input reached after error recovery")
                self.errok()
                # TODO in this case, parsing cannot continue and error is thrown again.
                #  Workaround: ignored keywords must not appear last.
                #  VARIABLE dummyvar {LABEL "";}
            return t

        print("Error: parsing failed at '%s' of preprocessed input (see *.i file)" % t)
        sys.exit(2)

    def read_text_dict(self, dictfile):
        """ simple parsing of text dictionary files containing
            [22,0]  text_reference
                    "Measure range"
                    "|de|Messbereich"
        """
        f = open(dictfile)
        insidestring = 0
        self.text_dictionary = {}
        txt_string = ''
        for line in f:
            m = re.match(r'^\[\d+,\d+\] +([a-zA-Z0-9_]+)', line)
            if m:
                insidestring = 1
                ref = m.group(1)
            else:
                if insidestring == 1:
                    m = re.match(r'^ +\"(.*)\"', line)
                    if m:
                        txt_string += m.group(1)
                    else:
                        insidestring = 0
                        self.text_dictionary[ref] = txt_string
                        txt_string = ''



    #-- build ROOT NODE LIST -------------------------------------------------------
    @_('ddl_node',
       'ddl_node_list ddl_node')
    def ddl_node_list(self, p):
        pass

    #-- EDD global productions  -------------------------------------------------------
    @_('MANUFACTURER I_NUM COMMA',
       'MANUFACTURER H_NUM COMMA')
    def ddl_node(self, p):
        self.manufacturer = int(p[1], 0)

    @_('DEVICE_TYPE I_NUM COMMA',
       'DEVICE_TYPE H_NUM COMMA')
    def ddl_node(self, p):
        self.device_type = int(p[1], 0)

    @_('DEVICE_REVISION I_NUM COMMA DD_REVISION I_NUM')
    def ddl_node(self, p):
        self.device_revision = int(p.I_NUM0)
        self.dd_revision = int(p.I_NUM1)

    @_('menu')
    def ddl_node(self, p):
        pass

    @_('command')
    def ddl_node(self, p):
        pass

    @_('variable')
    def ddl_node(self, p):
        pass

    # -- MENU PRODUCTIONS -------------------------------------------------------
    @_('MENU ID LCURLY menu_attributes RCURLY')
    def menu(self, p):
        self.menues[p.ID] = self.menu_attribs_dict
        self.menu_attribs_dict = {}      # clear, for next menu item

    @_('menu_attrib',
       'menu_attributes menu_attrib')
    def menu_attributes(self, p):
        pass

    @_( 'LABEL somestring SEMI')
    def menu_attrib(self, p):
        self.menu_attribs_dict[p.LABEL] = p.somestring

    @_('STYLE ID SEMI')
    def menu_attrib(self, p):
        self.menu_attribs_dict[p.STYLE] = p.ID

    @_('STYLE MENU SEMI')
    def menu_attrib(self, p):
        self.menu_attribs_dict[p.STYLE] = p.MENU

    @_('menu_property_items')
    def menu_attrib(self, p):
        self.menu_attribs_dict['ITEMS'] = self.menu_itemlist
        self.menu_itemlist = []

    @_('ID')            # m_sub_menu1,
    def menu_item(self, p):
        return p.ID

    @_( 'ID LBRACKET I_NUM RBRACKET',                                       # variable_1[0]
        'ID LBRACKET I_NUM RBRACKET DOT ID',                                # variable_1[0].ANALOG_VALUE
        'ID LBRACKET I_NUM RBRACKET DOT ID DOT ID',                         # variable_1[0].DAQ.ANALOG_VALUE
        'ID LBRACKET H_NUM RBRACKET',                                       # variable_1[0x01]
        'ID LBRACKET H_NUM RBRACKET DOT ID',                                # variable_1[0x01].ANALOG_VALUE
        'ID LBRACKET H_NUM RBRACKET DOT ID DOT ID')                         # variable_1[0x01].DAQ.ANALOG_VALUE
    def menuitem_variable(self, p):
        return p[0]

    # TODO stuff in brackets into variable attributes
    @_( 'ID LPAREN ID RPAREN',                                              # variable_1 (DISPLAY_VALUE)
        'ID LPAREN ID COMMA ID RPAREN',                                     # variable_1 (DISPLAY_VALUE, READ_ONLY)
        'ID LPAREN ID COMMA ID COMMA ID RPAREN',                            # variable_1 (DISPLAY_VALUE, READ_ONLY, NO_LABEL)
        'menuitem_variable',
        'menuitem_variable LPAREN ID RPAREN',                               # variable_1[0x01] (DISPLAY_VALUE)
        'menuitem_variable LPAREN ID COMMA ID RPAREN',                      # variable_1[0x01] (DISPLAY_VALUE, READ_ONLY)
        'menuitem_variable LPAREN ID COMMA ID COMMA ID RPAREN'              # variable_1[0x01] (DISPLAY_VALUE, READ_ONLY, NO_LABEL)
        )
    def menu_item(self, p):
        return p[0]     # TODO bitfields, attributes ignored

    @_('STRING')        # "raw text menu entry
    def menu_item(self, p):
        return p.STRING

    @_('menu_item',
       'menu_items COMMA menu_item',
       'menu_items COMMA COLUMNBREAK COMMA menu_item',      # TODO will work only if not 1st or last entry
       'menu_items COMMA ROWBREAK COMMA menu_item',
       'menu_items COLUMNBREAK COMMA menu_item',
       'menu_items ROWBREAK COMMA menu_item',
       'menu_items COMMA COLUMNBREAK menu_item',
       'menu_items COMMA ROWBREAK menu_item',
       'menu_items menu_item')
    def menu_items(self, p):
        self.menu_itemlist.append(p.menu_item)

    @_('ITEMS LCURLY RCURLY',
       'ITEMS LCURLY menu_items RCURLY')
    def menu_property_items(self, p):
        pass

    # == BOOLEAN PRODUCTIONS ========================================================
    """
    # WARNING: 132 shift/reduce conflicts
    # We want to just strip the IF-ELSE surrounding and forward what is between LCURLY ... RCURLY. How?
    # TODO - IF-ELSE struct are parsed but then-clause is returned always
    # TODO - only for menues so far
    @_( 'IF bool_expression LCURLY menu_items RCURLY',
        'IF bool_expression LCURLY menu_items RCURLY ELSE LCURLY menu_items RCURLY')
    def menu_items(self, p):
        return p.menu_items0

    @_( 'bool_expression EQUALS    bool_expression',
        'bool_expression NEQUALS   bool_expression',
        'bool_expression BOOLOR    bool_expression',
        'bool_expression BOOLAND   bool_expression',
        'bool_expression AMPERSAND bool_expression',
        'bool_expression BITOR     bool_expression',
        'bool_expression BITXOR    bool_expression',
        'bool_expression GT        bool_expression',
        'bool_expression LT        bool_expression',
        'bool_expression GTE       bool_expression',
        'bool_expression LTE       bool_expression',
        'NOT bool_expression')           # TODO shift operators '<<', '>>'
    def bool_expression(self, p):
        pass

    @_( 'LPAREN bool_expression RPAREN')
    def bool_expression(self, p):
        pass

    @_('ID', 'I_NUM', 'H_NUM', 'TRUE', 'FALSE')
    def bool_expression(self, p):
        pass
    """


    # == COMMAND PRODUCTIONS ========================================================
    @_('COMMAND ID LCURLY command_attributes RCURLY')
    def command(self, p):
        assert not p.ID in self.commands, f'command {p.ID} already defined'
        self.command_attribs['TRANSACTIONS'] = self.command_transactions_dict
        self.command_transactions_dict = {}
        self.commands[p.ID] = self.command_attribs
        self.command_attribs = {}
        # TODO plausibility checking? WRITE cmd has >0 request items, READ cmd >0 reply items ...

    @_('command_attrib',
       'command_attributes command_attrib',             # semi after TRANSACTION {} is optional
       'command_attributes SEMI command_attrib')
    def command_attributes(self, p):
        pass

    @_('NUMBER I_NUM')
    def command_attrib(self, p):
        self.command_attribs[p.NUMBER] = int(p.I_NUM)

    @_('OPERATION WRITE',
       'OPERATION READ',
       'OPERATION COMMAND')
    def command_attrib(self, p):
        self.command_attribs[p.OPERATION] = p[1]

    # == COMMAND TRANSACTION PRODUCTIONS ========================================================
    @_( 'TRANSACTION LCURLY command_transaction_keywords RCURLY',
        'TRANSACTION I_NUM LCURLY command_transaction_keywords RCURLY')
    def command_attrib(self, p):
        try:
            transaction_num = int(p.I_NUM)
        except:
            transaction_num = 0
        assert not transaction_num in self.command_transactions_dict, f'TRANSACTION {transaction_num} already defined'
        self.command_transactions_dict[transaction_num] = self.command_transaction_keywords_dict
        self.command_transaction_keywords_dict = {}

    @_('command_transaction_keyword',
       'command_transaction_keywords command_transaction_keyword')
    def command_transaction_keywords(self, p):
        pass

    # REPLY before REQUEST is allowed, RESPONSE_CODES inside TRANSACTIONS are optional
    @_( 'REQUEST LCURLY RCURLY',
        'REPLY LCURLY RCURLY',
        'REQUEST LCURLY command_transaction_items RCURLY',
        'REPLY LCURLY command_transaction_items RCURLY')
    def command_transaction_keyword(self, p):
        assert not p[0] in self.command_transaction_keywords_dict, f'TRANSACTION {p[0]} already defined'
        # list below REPLY contains tuples (variable, mask), list below REQUEST contains just variables
        itemslist = []
        if p[0] == 'REQUEST':
            for var,mask in self.command_transaction_items_list:
                itemslist.append(var)
        else:
            itemslist = self.command_transaction_items_list
        self.command_transaction_keywords_dict[p[0]] = itemslist
        self.command_transaction_items_list = []

    @_('command_transaction_item',
       'command_transaction_items COMMA command_transaction_item')
    def command_transaction_items(self, p):
        self.command_transaction_items_list.append(p.command_transaction_item)

    @_( 'command_transaction_int_or_var',
        'command_transaction_int_or_var command_transaction_item_mask',
        'command_transaction_int_or_var                               command_transaction_info_or_index',
        'command_transaction_int_or_var command_transaction_item_mask command_transaction_info_or_index')
    def command_transaction_item(self, p):
        try:
            mask = int(p.command_transaction_item_mask,0)
        except:
            mask = int('0xFFFF',0)
        return p.command_transaction_int_or_var, mask

    @_( 'ID')
    def command_transaction_int_or_var(self, p):
        return p.ID

    @_( 'ID LBRACKET I_NUM RBRACKET DOT ID',                     # array[0].ELEMENT
        'ID LBRACKET ID RBRACKET DOT ID' )                       # deviceVariables[device_variable_code_1].DIGITAL_UNITS,
    def command_transaction_int_or_var(self, p):
        return f'{p.ID0}({p[2]}].{p.ID1}'

    @_( 'ID LBRACKET I_NUM RBRACKET DOT ID DOT ID',              # dynamic_variables[0].DEVICE_VARIABLE.DAMPING_VALUE
        'ID LBRACKET ID RBRACKET DOT ID DOT ID')                 # dynamic_variables[device_variable_code_1].DEVICE_VARIABLE.DAMPING_VALUE
    def command_transaction_int_or_var(self, p):
        return f'{p.ID0}({p[2]}].{p.ID1}.{p.ID2}'

    @_( 'I_NUM')
    def command_transaction_int_or_var(self, p):
        return int(p.I_NUM)

    @_( 'H_NUM')
    def command_transaction_int_or_var(self, p):
        return int(p[0],16)

    @_('LT H_NUM GT')
    def command_transaction_item_mask(self, p):
        return p.H_NUM

    @_( 'LPAREN INFO RPAREN',
        'LPAREN INDEX RPAREN',
        'LPAREN INFO COMMA INDEX RPAREN',
        'LPAREN INDEX COMMA INFO RPAREN')
    def command_transaction_info_or_index(self, p):
        pass                # TODO ignore INFO, INDEX

    # == COMMAND RESPONSE CODES PRODUCTIONS ========================================================
    @_('RESPONSE_CODES LCURLY command_response_code_items RCURLY')
    def command_attrib(self, p):
        self.command_attribs['RESPONSE_CODES'] = self.command_response_codes_dict
        self.command_response_codes_dict = {}

    @_('command_response_code_item',
       'command_response_code_items command_response_code_item')
    def command_response_code_items(self, p):
        pass

    @_( 'I_NUM COMMA command_response_code_type COMMA somestring SEMI')
    def command_response_code_item(self, p):
        assert not p.I_NUM in self.command_response_codes_dict, f'response code {p.I_NUM} already defined'
        self.command_response_codes_dict[int(p.I_NUM)] = [p.command_response_code_type, p.somestring]

    @_( 'DATA_ENTRY_ERROR',
        'DATA_ENTRY_WARNING',
        'MISC_ERROR',
        'MISC_WARNING',
        'MODE_ERROR',
        'PROCESS_ERROR',
        'SUCCESS')
    def command_response_code_type(self, p):
        return p[0]

    # == VARIABLE PRODUCTIONS ========================================================
    @_('VARIABLE ID LCURLY variable_attribs RCURLY')
    def variable(self, p):
        assert not p.ID in self.variables, f'variable {p.ID} already defined'
        self.variables[p.ID] = self.variable_attribs_dict
        self.variable_attribs_dict = {}

    @_('variable_attrib',
       'variable_attribs variable_attrib')
    def variable_attribs(self, p):
        pass

    @_( 'LABEL somestring SEMI', 'REDEFINE LABEL somestring SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.LABEL] = p.somestring

    @_( 'STRING')
    def somestring(self, p):
        string = re.sub(r'\|.*', '', p.STRING)
        string = string.replace('\"','')
        return string

    @_( 'LBRACKET ID RBRACKET')
    def somestring(self, p):
        assert p.ID in self.text_dictionary, f' dictionary string {p.ID} not found'
        string = re.sub(r'\|.*', '', self.text_dictionary[p.ID])
        #print(f'[0,0] {p.ID} "{self.text_dictionary[p.ID]}"')       # print only the used texts to console
        return string

    @_( 'HELP somestring SEMI', 'REDEFINE HELP somestring SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.HELP] = p.somestring

    @_('CLASS class_specifiers SEMI', 'REDEFINE CLASS class_specifiers SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.CLASS] = self.variable_class_specifiers_list
        self.variable_class_specifiers_list = []

    @_('class_specifier',
       'class_specifiers AMPERSAND class_specifier')
    def class_specifiers(self, p):
        self.variable_class_specifiers_list.append(p.class_specifier)

    @_( 'ALARM', 'ANALOG_INPUT', 'ANALOG_OUTPUT', 'COMPUTATION', 'CONSTANT', 'CONTAINED', 'CORRECTION', 'DEVICE',
        'DIAGNOSTIC', 'DIGITAL_INPUT', 'DIGITAL_OUTPUT', 'DISCRETE', 'DISCRETE_INPUT', 'DISCRETE_OUTPUT',
        'DYNAMIC', 'FREQUENCY', 'FREQUENCY_INPUT', 'FREQUENCY_OUTPUT', 'HART', 'INPUT', 'IS_CONFIG', 'LOCAL',
        'LOCAL_A', 'LOCAL_B', 'LOCAL_DISPLAY', 'MODE', 'OPERATE', 'OPTIONAL', 'OUTPUT', 'SERVICE', 'SPECIALIST',
        'TEMPORARY', 'TUNE')
    def class_specifier(self, p):
        return p[0]

    @_('HANDLING handling_specifiers SEMI', 'REDEFINE HANDLING handling_specifiers SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.HANDLING] = p.handling_specifiers

    @_('READ', 'WRITE', 'READ AMPERSAND WRITE')
    def handling_specifiers(self, p):
        if self.production.len == 3:
            return ['READ', 'WRITE']
        else:
            return p[0]

    @_('DEFAULT_VALUE I_NUM SEMI', 'DEFAULT_VALUE H_NUM SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.DEFAULT_VALUE] = int(p[1], 0)

    @_('DEFAULT_VALUE F_NUM SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.DEFAULT_VALUE] = p.F_NUM

    @_('DEFAULT_VALUE STRING SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.DEFAULT_VALUE] = p.STRING

    @_('REDEFINE DEFAULT_VALUE I_NUM SEMI', 'REDEFINE DEFAULT_VALUE H_NUM SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.DEFAULT_VALUE] = int(p[2], 0)

    @_('CONSTANT_UNIT somestring SEMI')
    def variable_attrib(self, p):
        self.variable_attribs_dict[p.CONSTANT_UNIT] = p.somestring

    # == VARIABLE TYPE PRODUCTIONS ========================================================
    @_( '         TYPE type_format                                                       SEMI',
        '         TYPE type_format LPAREN I_NUM RPAREN                                   SEMI',
        '         TYPE type_format                        LCURLY type_attributes RCURLY',
        '         TYPE type_format LPAREN I_NUM RPAREN    LCURLY type_attributes RCURLY',
        'REDEFINE TYPE type_format                                                       SEMI',
        'REDEFINE TYPE type_format LPAREN I_NUM RPAREN                                   SEMI',
        'REDEFINE TYPE type_format                        LCURLY type_attributes RCURLY',
        'REDEFINE TYPE type_format LPAREN I_NUM RPAREN    LCURLY type_attributes RCURLY')
    def variable_attrib(self, p):
        self.variable_attribs_dict['FORMAT'] = p.type_format
        try:
            self.variable_attribs_dict['SIZE'] = int(p.I_NUM)
        except:
            pass

    @_( 'ASCII',
        'DATE',
        'DOUBLE',
        'FLOAT',
        'INTEGER',
        'UNSIGNED_INTEGER',
        'TIME_VALUE',
        'INDEX',
        'PACKED_ASCII',
        'PASSWORD')
    def type_format(self, p):
        return p[0]

    @_( 'type_attribute',
        'type_attributes type_attribute')
    def type_attributes(self, p):
        pass

    @_( 'MIN_VALUE I_NUM SEMI',
        'MAX_VALUE I_NUM SEMI')
    def type_attribute(self, p):
        self.variable_attribs_dict[p[0]] = int(p.I_NUM)

    # TODO this hack resolves MIN_VALUE IF { ... } MAX_VALUE. Remove as soon as IF handling is fixed
    @_( 'MIN_VALUE', 'MAX_VALUE')
    def type_attribute(self, p):
        pass

    @_( 'MIN_VALUE F_NUM SEMI',
        'MAX_VALUE F_NUM SEMI')
    def type_attribute(self, p):
        self.variable_attribs_dict[p[0]] = float(p.F_NUM)

    @_( 'DISPLAY_FORMAT somestring SEMI',
        'EDIT_FORMAT somestring SEMI')
    def type_attribute(self, p):
        self.variable_attribs_dict[p[0]] = p.somestring

    @_('         TYPE ENUMERATED                         LCURLY type_enum_values RCURLY',
       '         TYPE ENUMERATED LPAREN I_NUM RPAREN     LCURLY type_enum_values RCURLY',
       'REDEFINE TYPE ENUMERATED                         LCURLY type_enum_values RCURLY',
       'REDEFINE TYPE ENUMERATED LPAREN I_NUM RPAREN     LCURLY type_enum_values RCURLY')
    def variable_attrib(self, p):
        self.variable_attribs_dict['FORMAT'] = p.ENUMERATED
        try:
            self.variable_attribs_dict['SIZE'] = int(p.I_NUM)
        except:
            pass
        self.variable_attribs_dict['ENUMS'] = self.temp_dict
        self.temp_dict = {}

    @_('         TYPE BIT_ENUMERATED                         LCURLY type_enum_values RCURLY',
       '         TYPE BIT_ENUMERATED LPAREN I_NUM RPAREN     LCURLY type_enum_values RCURLY',
       'REDEFINE TYPE BIT_ENUMERATED                         LCURLY type_enum_values RCURLY',
       'REDEFINE TYPE BIT_ENUMERATED LPAREN I_NUM RPAREN     LCURLY type_enum_values RCURLY')
    def variable_attrib(self, p):
        self.variable_attribs_dict['FORMAT'] = p.BIT_ENUMERATED
        try:
            self.variable_attribs_dict['SIZE'] = int(p.I_NUM)
        except:
            pass
        self.variable_attribs_dict['ENUMS'] = self.temp_dict
        self.temp_dict = {}

    @_( 'type_enum_value',
        'type_enum_values type_enum_value',
        'type_enum_values COMMA type_enum_value')
    def type_enum_values(self, p):
        pass

    @_( 'LCURLY I_NUM COMMA somestring RCURLY',
        'LCURLY H_NUM COMMA somestring RCURLY')
    def type_enum_value(self, p):
        myint = int(p[1], 0)
        self.temp_dict[int(myint)] = p.somestring

    @_( 'LCURLY I_NUM COMMA somestring COMMA somestring RCURLY',
        'LCURLY H_NUM COMMA somestring COMMA somestring RCURLY')
    def type_enum_value(self, p):
        myint = int(p[1], 0)
        self.temp_dict[int(myint)] = p.somestring0

    @_('TYPE INDEX ID SEMI')
    def variable_attrib(self, p):
        pass    #TODO index ignored

    # == LIKE VARIABLE TYPE PRODUCTIONS ========================================================
    # TODO simple light-weight redefine strategy
    #   attribs of the like variable are collected in variable_attribs in the same way as for a new variable.
    #   Only redefine (not add, delete) supported.
    #   Redefine only on the first level below variable supported (LABEL, HELP,..) not e.g. inside enums.
    #   missing 'REDEFINE' on a LIKE variable not detected
    @_('ID LIKE VARIABLE ID LCURLY variable_attribs RCURLY')
    def variable(self, p):
        assert not p.ID0 in self.variables, f'variable {p.ID0} already defined'
        # TODO throwing error fails when IMPORTed variables are missing
        #assert p.ID1 in self.variables, f'to be redefined variable {p.ID1} not previously defined'
        if p.ID1 in self.variables:
            self.variables[p.ID0] = self.variables[p.ID1].copy()
        else:
            self.variables[p.ID0] = {}
        for key in self.variable_attribs_dict:
            self.variables[p.ID0][key] = self.variable_attribs_dict[key]
        self.variable_attribs_dict = {}

