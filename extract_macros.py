import clang.cindex as cindex
import blist

def extract_preprocessor(children):
	"""Recursively iterate through a cursor, and print all preprocessor definitions."""
	retlist = blist.blist()
	for i in children:
		if i.kind.is_preprocessing():
			retlist.append(i)
		retlist += extract_preprocessor(i.get_children())
	return retlist

def extract_macros(c):
	return filter(lambda x: x.kind == cindex.CursorKind.MACRO_DEFINITION, extract_preprocessor(c.get_children()))

def cursor_list_to_tokens(l):
	retlist = blist.blist()
	for i in l:
		token_strings = [j.spelling for j in i.get_tokens()]
		retlist.append((i, token_strings))
	return retlist

index = cindex.Index.create()
tu = index.parse('openal-soft/include/al/al.h', options=cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
preprocessor_definitions = extract_preprocessor(tu.cursor.get_children())
preprocessor_definitions_with_tokens = cursor_list_to_tokens(preprocessor_definitions)

#let's build a python dict of OpenAL macros, and see what comes out.
#because of reasons, this is actually unzip and python doesn't appear to give us one.
tokens_for_macros = zip(*preprocessor_definitions_with_tokens)[1]
#filter out the OpenAL Ones, which all start withAL_.
open_al_macros = filter(lambda x: x[0].startswith('AL_'), tokens_for_macros)

#let's go through it again, this time extracting all macros that are in some way a number.
open_al_numeric_macros = blist.blist()
for i in open_al_macros:
	try:
		number_string = i[1]
		base = 10
		if i[1].startswith('0x'):
			number_string = i[1][2:]
			base = 16
		val = int(number_string, base)
	except ValueError:
		try:
			val = float(i[1])
		except ValueError:
			continue #this is an odd macro that we can't understand.
	open_al_numeric_macros.append((i[0], val))

numeric_macros_dict = dict(open_al_numeric_macros)
import json
out = file('open_al_macros.json', 'w')
json.dump(numeric_macros_dict, out)
