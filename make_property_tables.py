from jinja2 import Environment, FileSystemLoader
import yaml
import os.path
searchpath = os.path.join(os.path.dirname(__file__), 'templates')
loader = FileSystemLoader(searchpath)
env = Environment(loader = loader)
template = env.get_template('property_table.html.t')

macros = yaml.load(stream = file('extracted_data/macros_raw.yml'))
old_macros = macros

#grab only the OpenAL macros.
macros = {k: v for k, v in macros.iteritems() if not k.startswith('ALC_') and '_MAX_' not in k and '_MIN_' not in k and '_DEFAULT_' not in k}

#Convert ranges to numbers, where possible.
for macro in macros.itervalues():
	if 'range' in macro and macro['range'] and len(macro['range']) == 2:
		macro['range'][0] = old_macros[macro['range'][0]]['value']
		macro['range'][1] = old_macros[macro['range'][1]]['value']

output = template.render(macros = macros)

with file('property_table.html', 'w') as f:
	f.write(output)
