"""A script that builds all the information from the OpenAL headers."""
import build_metadata.extract_from_headers
import os.path
import yaml

headers =  set([
os.path.join('OpenAL-Soft', 'include', 'al', 'al.h'),
os.path.join('OpenAL-Soft', 'include', 'al', 'alc.h'),
os.path.join('OpenAL-Soft', 'include', 'al', 'efx.h')
])
my_directory = os.path.dirname(os.path.abspath(__file__))
for i in headers:
	headers.remove(i)
	headers.add(os.path.join(my_directory, i))

yml_files = build_metadata.extract_from_headers.extract_from_headers(headers, target_directory = os.path.join(my_directory, 'extracted_data'))
with file(os.path.join(my_directory, 'extracted_data', 'functions.yml'), 'w') as outfile:
	yaml.dump(data = yml_files['functions'], stream = outfile)
with file(os.path.join(my_directory, 'extracted_data', 'macros.yml'), 'w') as outfile:
	yaml.dump(data = yml_files['macros'], stream = outfile, default_flow_style = False)
