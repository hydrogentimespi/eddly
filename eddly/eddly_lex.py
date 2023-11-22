import sys
from sly import Lexer

# TODO make this a member of Ddl_lexer without "sly.lex.LexerBuildError: currentinputfile does not match a name in tokens"
# TODO fall back to the file, initially fed into the preprocessor in case we see "#line 123" only
#currentinputfile = ''


class Eddl_lexer(Lexer):
    # define tokens
    tokens = {
        # common general tokens
        #LANGLE, RANGLE, replaced by LT and GT
        LBRACKET, RBRACKET,
        LCURLY, RCURLY,
        LPAREN, RPAREN,
        AMPERSAND, COMMA, DOT, SEMI, COLON,
        COMMENT, ID, STRING,
        F_NUM, H_NUM, I_NUM,
        ADD, DIV, MIN, MUL,
        FALSE, TRUE,
        IF, ELSE,
        EQUALS, NEQUALS, BOOLOR, BOOLAND, NOT, BITOR, BITXOR, GT, LT, GTE, LTE, EQ,

        # DDL GLOBAL tokens
		MANUFACTURER, DEVICE_TYPE, DEVICE_REVISION, DD_REVISION,
		IMPORT, STANDARD, TABLES,

        # DDL MENU tokens
		MENU, ITEMS,
		# TODO common tokens, e.g. LABEL,
        COLUMNBREAK, ROWBREAK,
		STYLE,

        # DDL METHOD tokens
        METHOD,

        # DDL COMMAND tokens
        COMMAND,
        NUMBER,
        OPERATION, READ, WRITE, COMMAND,
        REPLY, REQUEST, RESPONSE_CODES,
        INDEX, INFO,
        TRANSACTION,
        # RESPONSE CODES
        DATA_ENTRY_ERROR, DATA_ENTRY_WARNING, MISC_ERROR, MISC_WARNING, MODE_ERROR, PROCESS_ERROR, SUCCESS,

        # VARIABLE tokens
        ASCII,
        BIT_ENUMERATED,
        CLASS, CONSTANT_UNIT, CORRECTABLE, CORRECTION,
        DATE, DEFAULT_VALUE, DEVICE, DIAGNOSTIC, DISPLAY_FORMAT, EDIT_FORMAT, DYNAMIC,
        ENUMERATED,
        FLOAT,
        HANDLING, HARDWARE, HART, HELP, LIKE, REDEFINE,

        # VARIABLE>CLASS tokens
        ALARM, ANALOG_INPUT, ANALOG_OUTPUT, COMPUTATION, CONSTANT, CONTAINED, CORRECTION, DEVICE,
        DIAGNOSTIC, DIGITAL_INPUT, DIGITAL_OUTPUT, DISCRETE, DISCRETE_INPUT, DISCRETE_OUTPUT,
        DYNAMIC, FREQUENCY, FREQUENCY_INPUT, FREQUENCY_OUTPUT, HART, INPUT, IS_CONFIG, LOCAL,
        LOCAL_A, LOCAL_B, LOCAL_DISPLAY, MODE, OPERATE, OPTIONAL, OUTPUT, SERVICE, SPECIALIST,
        TEMPORARY, TUNE, PASSWORD, DOUBLE,

        WRITE_AS_ONE, EDIT_DISPLAY, COLLECTION, UNIT, ARRAY, GRID, AXIS, WAVEFORM, GRAPH, IMAGE,

        #INDEX, see COMMAND tokens
        INTEGER,
        LABEL, LOCAL,
        MAX_VALUE, MIN_VALUE, MISC,
        PACKED_ASCII, PRE_EDIT_ACTIONS, POST_EDIT_ACTIONS,

        #READ, see COMMAND tokens
        SERVICE,
        TIME_VALUE, TYPE,
        UNSIGNED_INTEGER,
        VALIDITY, VARIABLE
        #WRITE, see COMMAND tokens
    }

    # ignored charaters
    ignore = ' \t'

    # define common token regex
    ID        = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING    = r'\"[^\"]*\"([ \n]+\"[^\"]*\")*'

    F_NUM     = r'[+-]?(\d+)+\.(\d+)+([eE][+-]?\d+)?'        # '.5e7'  or '5.e7' not covered
    H_NUM     = r'0[xX][a-zA-Z0-9]+'
    I_NUM     = r'-?\d+'
    EQUALS    = '=='
    NEQUALS   = '!='
    BOOLOR    = '\|\|'
    BOOLAND   = '&&'
    NOT       = '!'
    #BITAND covered by AMPERSAND
    BITOR     = '\|'
    BITXOR    = '\^'
    GTE       = '>='
    LTE       = '<='
    GT        = '>'
    LT        = '<'
    # TODO shift operators '<<', '>>'

    ADD       = r'\+'
    DIV       = r'/'
    MIN       = r'-'
    MUL       = r'\*'
    EQ        = '='

    LBRACKET  = r'\['
    RBRACKET  = r'\]'
    LCURLY    = r'\{'
    RCURLY    = r'\}'
    LPAREN    = r'\('
    RPAREN    = r'\)'

    AMPERSAND = r'&'
    COMMA     = r','
    DOT       = r'\.'
    SEMI      = r';'
    COLON     = r':'


    # map token ID to DDL keyword token in alphabetical order - TODO: why ordered?
    ID['ASCII']               = ASCII
    ID['ARRAY']               = ARRAY
    ID['AXIS']                = AXIS
    ID['BIT_ENUMERATED']      = BIT_ENUMERATED
    ID['CLASS']               = CLASS
    ID['COLLECTION']          = COLLECTION
    ID['COLUMNBREAK']         = COLUMNBREAK
    ID['COMMAND']             = COMMAND
    ID['CONSTANT_UNIT']       = CONSTANT_UNIT
    ID['CORRECTABLE']         = CORRECTABLE
    ID['CORRECTION']          = CORRECTION
    ID['DATA_ENTRY_ERROR']    = DATA_ENTRY_ERROR
    ID['DATA_ENTRY_WARNING']  = DATA_ENTRY_WARNING
    ID['DATE']                = DATE
    ID['DOUBLE']              = DOUBLE
    ID['DEFAULT_VALUE']       = DEFAULT_VALUE
    ID['DEVICE']              = DEVICE
    ID['DIAGNOSTIC']          = DIAGNOSTIC
    ID['DISPLAY_FORMAT']      = DISPLAY_FORMAT
    ID['DYNAMIC']             = DYNAMIC
    ID['EDIT_DISPLAY']        = EDIT_DISPLAY
    ID['EDIT_FORMAT']         = EDIT_FORMAT
    ID['ELSE']                = ELSE
    ID['ENUMERATED']          = ENUMERATED
    ID['FALSE']               = FALSE
    ID['FLOAT']               = FLOAT
    ID['GRAPH']               = GRAPH
    ID['GRID']                = GRID
    ID['HANDLING']            = HANDLING
    ID['HARDWARE']            = HARDWARE
    ID['HART']                = HART
    ID['HELP']                = HELP
    ID['IF']                  = IF
    ID['INDEX']               = INDEX
    ID['INFO']                = INFO
    ID['INTEGER']             = INTEGER
    ID['IMAGE']               = IMAGE
    ID['ITEMS']               = ITEMS
    ID['LABEL']               = LABEL
    ID['LIKE']                = LIKE
    ID['LOCAL']               = LOCAL
    ID['MAX_VALUE']           = MAX_VALUE
    ID['MENU']                = MENU
    ID['METHOD']              = METHOD
    ID['MIN_VALUE']           = MIN_VALUE
    ID['MISC']                = MISC
    ID['MISC_ERROR']          = MISC_ERROR
    ID['MISC_WARNING']        = MISC_WARNING
    ID['MODE_ERROR']          = MODE_ERROR
    ID['NUMBER']              = NUMBER
    ID['OPERATION']           = OPERATION
    ID['PACKED_ASCII']        = PACKED_ASCII
    ID['PASSWORD']            = PASSWORD
    ID['POST_EDIT_ACTIONS']   = POST_EDIT_ACTIONS
    ID['PRE_EDIT_ACTIONS']    = PRE_EDIT_ACTIONS
    ID['PROCESS_ERROR']       = PROCESS_ERROR
    ID['READ']                = READ
    ID['REDEFINE']            = REDEFINE
    ID['REPLY']               = REPLY
    ID['REQUEST']             = REQUEST
    ID['RESPONSE_CODES']      = RESPONSE_CODES
    ID['ROWBREAK']            = ROWBREAK
    ID['SERVICE']             = SERVICE
    ID['STYLE']               = STYLE
    ID['SUCCESS']             = SUCCESS
    ID['TIME_VALUE']          = TIME_VALUE
    ID['TRANSACTION']         = TRANSACTION
    ID['TRUE']                = TRUE
    ID['TYPE']                = TYPE
    ID['UNSIGNED_INTEGER']    = UNSIGNED_INTEGER
    ID['UNIT']                = UNIT
    ID['VALIDITY']            = VALIDITY
    ID['VARIABLE']            = VARIABLE
    ID['WAVEFORM']            = WAVEFORM
    ID['WRITE']               = WRITE
    ID['WRITE_AS_ONE']        = WRITE_AS_ONE
    ID['MANUFACTURER']        = MANUFACTURER
    ID['DEVICE_TYPE']         = DEVICE_TYPE
    ID['DEVICE_REVISION']     = DEVICE_REVISION
    ID['DD_REVISION']         = DD_REVISION
    ID['IMPORT']              = IMPORT
    ID['STANDARD']            = STANDARD
    ID['_TABLES']             = TABLES          # sly does not like tokens beginning with '_'


    # line number tracking
    @_(r'#line .*')
    def handle_linedirective(self, t):
        # TODO improve this that the lexer and the parser are capable of printing the line number and line contents
        """
        try:
            (directive, line, file) = t.value.split()
            currentinputfile = file     # TODO: let also parser report current file, not only lineno
        except:
            (directive, line) = t.value.split() # keep file as set before
        #print(f'preprocessor directive {directive}, line {line}, file {file}')
        self.lineno = int(line)
        """
        pass

    # line number tracking
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # report illegal character error
    def error(self, t):
        #sys.stderr.write(f'lexing error: file:{currentinputfile}, line:{self.lineno}, Illegal character {t.value[0]}\n')
        sys.stderr.write(f'lexing error: line:{self.lineno}, Illegal character {t.value[0]}\n')
        sys.exit(1)

