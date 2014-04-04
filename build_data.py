"""A script that builds all the information from the OpenAL headers."""
import build_metadata.extract_from_headers
import os.path
import yaml
import collections

headers =  set([
os.path.join('OpenAL-Soft', 'include', 'al', 'al.h'),
os.path.join('OpenAL-Soft', 'include', 'al', 'alc.h'),
os.path.join('OpenAL-Soft', 'include', 'al', 'efx.h')
])
my_directory = os.path.dirname(os.path.abspath(__file__))
for i in headers:
	headers.remove(i)
	headers.add(os.path.join(my_directory, i))

yml_files = build_metadata.extract_from_headers.extract_from_headers(headers, target_directory = os.path.join(my_directory, 'extracted_data'), macros = ["AL_ALEXT_PROTOTYPES"])
macros = yml_files['macros']
functions = yml_files['functions']

#For each macro, we now assign a class (if ppossible).

#pass 1: replace all macros with dicts with default values.
new_macros = dict()
for i, v in macros.iteritems():
	new_macros[i] = {'value': v, 'object' : '', 'range' : '', 'setter' : ''}
macros = new_macros

#pass 2: assignment of associated objects, where possible.
effects = set(['reverb', 'eaxreverb'])
for name, value in macros.iteritems():
	for classname in effects:
		prefix = 'AL_' + classname.upper() + '_'
		if name.startswith(prefix):
			value['object'] = classname

#pass 3: assignment of ranges where possible.
for k, v in macros.iteritems():
	min_macro = k.split('_')
	min_macro = min_macro[:2] + ['MIN'] + min_macro[2:]
	max_macro = k.split('_')
	max_macro = max_macro[:2] + ['MAX'] + max_macro[2:]
	min_macro = '_'.join(min_macro)
	max_macro = '_'.join(max_macro)
#	print min_macro, max_macro
	if min_macro in macros and max_macro in macros:
		v['range'] = [macros[min_macro]['value'], macros[max_macro]['value']]

with file(os.path.join(my_directory, 'extracted_data', 'functions_raw.yml'), 'w') as outfile:
	yaml.dump(data = functions, stream = outfile)
with file(os.path.join(my_directory, 'extracted_data', 'macros_raw.yml'), 'w') as outfile:
	yaml.dump(data = macros, stream = outfile)

