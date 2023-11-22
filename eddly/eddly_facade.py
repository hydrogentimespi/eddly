import io
import logging


from .eddly_preproc  import Eddl_preproc
from .eddly_lex      import Eddl_lexer
from .eddly_parse    import Eddl_parser

class Eddly():

    loglevel = logging.NOTSET
    print_menu_stack = ''

    def __init__(self, loglevel = logging.INFO):
        """ creates an object for processing edd files into python structures """
        self.preproc = Eddl_preproc()
        self.loglevel = loglevel

    def read_ddl(self, ddl_file: str, textdict ='', preprocessed_output='pp_out.i'):
        """process main *.ddl file, preprocess, apply text dict, lex it and parse it."""
        lexer = Eddl_lexer()
        parser = Eddl_parser()
        preprocessed_ddl = ''   # TODO save as global object and print line on parsing error?

        #for tok in lexer.tokenize(preprocessed_ddl):
        #    print('%r: %r' % (tok.type, tok.value))

        self.log(logging.INFO, f'reading {ddl_file}...')
        with open(ddl_file, 'r', encoding="utf8") as f:
            main_ddl = f.read()

        self.preproc.parse(main_ddl)
        oh = io.StringIO()
        self.preproc.write(oh)
        preprocessed_ddl = oh.getvalue()

        if preprocessed_output:
            with open(preprocessed_output, 'w', encoding="utf8") as f:
                f.write(preprocessed_ddl)
            self.log(logging.INFO, f'preprocessor output written to {preprocessed_output}')

        if textdict:
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


    def get_menu_item_string(self, item):
        if item in self.menues:
            # item is a sub menu
            if 'LABEL' in self.menues[item]:
                return self.menues[item]['LABEL']
            else:
                # ...but has no string
                return item
        elif item[0] is '"':
            # item is string - strip ""
            return item[1:-1]
        else:
            if item in self.variables:
                # item is a variable
                if 'LABEL' in self.variables[item]:
                    return self.variables[item]['LABEL']
                else:
                    # ...but has no string
                    return item
            else:
                # item is e.g. method
                return item


    def print_menu_node(self, menu_node: dict):
        """
        print one menu entry including sub menues
        """
        max = len(menu_node['ITEMS'])-1
        for idx, item in enumerate(menu_node['ITEMS']):
            print(''.join(self.print_menu_stack), end='')
            if idx == max:
                # item is the last entry on this level
                print(f'{self.print_menu_this_last}{self.get_menu_item_string(item)}')
                if item in self.menues:
                    # menu item is a sub menu
                    self.print_menu_stack.append(self.print_menu_parent_last)
                    self.print_menu_node(self.menues[item])
                    self.print_menu_stack.pop()
            else:
                print(f'{self.print_menu_this_mid}{self.get_menu_item_string(item)}')
                if item in self.menues:
                    # menu item is a sub menu
                    self.print_menu_stack.append(self.print_menu_parent_mid)
                    self.print_menu_node(self.menues[item])
                    self.print_menu_stack.pop()

    def print_menu_tree(self, menu_entry_point: str):
        """
        print the menu tree resursively to console starting at menu_entry_point
        """
        self.print_menu_stack       = ['   ']         # start string of every printed menu line
        self.print_menu_this_mid    = '├─── '      
        self.print_menu_this_last   = '└─── '      
        self.print_menu_parent_mid  = '│    '
        self.print_menu_parent_last = '     '

        # print menu entry point name and line
        print(''.join(self.print_menu_stack), end='')
        print(self.get_menu_item_string(menu_entry_point))

        # print sub menues starting at entry point
        self.print_menu_node(self.menues[menu_entry_point])

