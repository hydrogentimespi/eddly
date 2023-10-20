import io
import logging


from .eddly_preproc  import Eddl_preproc
from .eddly_lex      import Eddl_lexer
from .eddly_parse    import Eddl_parser

class Eddly():

    loglevel = logging.NOTSET

    def __init__(self, loglevel = logging.INFO):
        """ creates an object for processing edd files into python structures """
        self.preproc = Eddl_preproc()
        self.loglevel = loglevel

    def read_ddl(self, ddl_file: str, textdict: str, preprocessed_output='pp_out.i'):
        """process main *.ddl file, preprocess, apply text dict, lex it and parse it."""
        lexer = Eddl_lexer()
        parser = Eddl_parser()
        preprocessed_ddl = ''   # TODO save as global object and print line on parsing error?

        #for tok in lexer.tokenize(preprocessed_ddl):
        #    print('%r: %r' % (tok.type, tok.value))

        self.log(logging.INFO, f'reading {ddl_file}...')
        with open(ddl_file) as f:
            main_ddl = f.read()

        self.preproc.parse(main_ddl)
        oh = io.StringIO()
        self.preproc.write(oh)
        preprocessed_ddl = oh.getvalue()

        if preprocessed_output:
            with open(preprocessed_output, 'w') as f:
                f.write(preprocessed_ddl)
            self.log(logging.INFO, f'preprocessor output written to {preprocessed_output}')

        parser.read_text_dict(textdict)

        parser.parse(lexer.tokenize(preprocessed_ddl))

        # TODO do plausibility checking here not possible during parsing, e.g. do all variables referenced in commands exist?

        self.manufacturer       = parser.manufacturer
        self.dd_revision        = parser.dd_revision
        self.device_type        = parser.device_type
        self.device_revision    = parser.device_revision
        self.commands           = parser.commands
        self.variables          = parser.variables
        self.menues             = parser.menues


    # TODO get built-in logger to work with non standard levels like logging.DEBUG
    def log(self, level, msg: str):
        if level >= self.loglevel: print(f'eddly: {msg}')

    def get_variable_size(self, var: str) -> int:
        """size in bytes, based on 'SIZE' keyword"""
        assert var in self.variables, f'no such variable {var}.'

        if 'SIZE' in self.variables[var]:
            return self.variables[var]['SIZE']
        else:
            variable_sizes = {
                'DOUBLE':           8,
                'FLOAT':            4,
                'INTEGER':          1,
                'UNSIGNED_INTEGER': 1,
                'DATE':             3,
                'TIME':             4,
                'TIME_VALUE':       4,
                'BIT_ENUMERATED':   1,
                'ENUMERATED':       1,
                'INDEX':            1,
                'OCTET':            1
            }
            return variable_sizes[self.variables[var]['FORMAT']]

