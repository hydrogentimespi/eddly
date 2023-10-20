from eddly import Eddly
import pprint

myedd = Eddly()

myedd.preproc.define('ENABLE_MENUES 1')
myedd.read_ddl('demo.ddl', 'strings.dc8', 'pp_out.i')

print(f'# Edd meta data: manufacturer {myedd.manufacturer}, device type {myedd.device_type}, dd revision {myedd.dd_revision}, device revision {myedd.device_revision}')
pp = pprint.PrettyPrinter(indent=4)
print('# commands')
pp.pprint(myedd.commands)
print('# variables')
pp.pprint(myedd.variables)
print('# menues')
pp.pprint(myedd.menues)

