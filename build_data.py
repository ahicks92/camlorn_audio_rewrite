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

yml_files = build_metadata.extract_from_headers.extract_from_headers(headers, target_directory = os.path.join(my_directory, 'extracted_data'), extra_args = ["-DAL_ALEXT_PROTOTYPES"])
with file(os.path.join(my_directory, 'extracted_data', 'functions.yml.raw'), 'w') as outfile:
	yaml.dump(data = yml_files['functions'], stream = outfile)
with file(os.path.join(my_directory, 'extracted_data', 'macros.yml.raw'), 'w') as outfile:
	yaml.dump(data = yml_files['macros'], stream = outfile, default_flow_style = False)

#Let's make the classes.  The raw yaml files from above are useful, but aren't structured enough.
#In OpenAL, the getters for an object begin with alGet and the setters begin with alSet.
#For example, sources are alGetSource and setters are alSource, with a type suffix.
#In terms of constants, the constants which act as properties are AL_SOURCE, AL_BUFFER, etc.
#At the moment, only process sources and buffers; other objects are more complex.
#Finally, note that we use strings here.  The actual value of a constant is almost never needed directly once it is mapped
#into the target programming language, and the above YML file record it.  This includes C.
macros = yml_files['macros']
functions = yml_files['functions']

#We make a dict and pull out what we can.
classes = collections.defaultdict(lambda: collections.defaultdict(list))

#Macros.
#Note that it is unfortunate but true that most source attributes are in fact special cases.
#this works well on EFX, however.
effects = set(['reverb', 'eax_reverb'])
for i in effects:
	macro_prefix = "AL_"+i.upper()
	for j in macros.iterkeys():
		if j.startswith(macro_prefix):
			classes[i]['properties'].append(j)

#Functions.  Fortunately, nothing here is a special case, or if it is it must be annotated.
for i in set(['source', 'buffer', 'effect']):
	getter_prefix = 'alGet' + i[0].upper() + i[1:]
	setter_prefix = 'al' + i[0].upper() + i[1:]
	for j in functions.iterkeys():
		if j.startswith(getter_prefix):
			classes[i]['getters'].append(j)
		elif j.startswith(setter_prefix):
			classes[i]['setters'].append(j)

#note that the efx getters and setters are actually for all classes, and that there is no effect class itself.
for i in effects:
	classes[i]['getters'] = list(classes['effect']['getters'])
	classes[i]['setters'] = list(classes['effect']['setters'])
#del classes['effect']

#remake the entire defaultdict into dicts. This is cleaner than the alternative by far.
#If not, the yaml is filled with a great number of tags that we absolutely don't want.
for i, j in classes.iteritems():
	classes[i] = dict(j)
classes = dict(classes)

with file('extracted_data/classes.yml.raw', 'w') as f:
	yaml.dump(data = classes, stream = f)
