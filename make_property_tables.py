from jinja2 import Environment, FileSystemLoader
import yaml
import os.path
searchpath = os.path.join(os.path.dirname(__file__), 'templates')
loader = FileSystemLoader(searchpath)
env = Environment(loader = loader)
template = env.get_template('property_table.html.t')

macros = yaml.load(stream = file('extracted_data/macros_raw.yml'))

#grab only the OpenAL macros.
macros = {k: v for k, v in macros.iteritems() if not k.startswith('ALC_')}

output = template.render(macros)

with file('property_table.html', 'w') as f:
	f.write(output)
