from pcpp import Preprocessor
import sys

class Eddl_preproc(Preprocessor):

    def on_error(self, file, line, msg):
        sys.stderr.write(f'preprocessing error:file: {file}: line:{line}: {msg}')
        sys.exit(1)
