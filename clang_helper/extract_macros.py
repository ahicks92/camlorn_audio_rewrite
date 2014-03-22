"""Utilities for extracting macros and preprocessor definitions from C files.  Depends on Clang's python bindings and Blist.
Note that cursors have children, which are also cursors.  They are not iterators, they are nodes in a tree.
Everything here uses iterators.  The general strategy is to have multiple passes over the same cursor to extract everything needed, and this entire file can be viewed as filters over raw cursors."""
import blist
import itertools
import clang.cindex as cindex
from . import flatten_cursor

def extract_preprocessor_cursors(cursor):
	"""Get all preprocessor definitions from a cursor."""
	for i in flatten_cursor(cursor):
		if i.kind.is_preprocessing():
			yield i

def extract_macros(c):
	"""Get all macros from a cursor."""
	return itertools.ifilter(lambda x: x.kind == cindex.CursorKind.MACRO_DEFINITION, extract_preprocessor_cursors(c))

def cursor_list_to_tokens(iterator):
	"""Conversts a list of interesting cursors to a tokenized representation.  Returns:
[(c1, t1), (c2, t2), ..., (cn, tn)]
Where c1...cn are the original cursors and t1...tn are lists of tokens.
Helpful note.  For simple C macros, the first token is the macro's name, and the remaining tokens (except for the last in some cases) are the tokenns that define it.  This holds true only for macros without parameters.
Note that for simple numeric constant macros, t[0] is the name and t[1] is the constant. Even throwing in a parentheses breaks this pattern, however.
For functions, the useful information can be extracted without hacks, and this function is the wrong method to do so."""
	for i in iterator:
		token_strings = [j.spelling for j in i.get_tokens()]
		yield (i, token_strings)

def extract_macro_constants(cursor):
	"""Returns a dict of macros to constants for all macros which are of the form:
#define foo number
This function is unable to handle more complex macros."""
	macro_definitions = extract_macros(cursor)
	macro_tokens= cursor_list_to_tokens(macro_definitions)
	#let's build a python dict of macros, and see what comes out.
	#because of reasons, this is actually unzip and python doesn't appear to give us one.
	macros = zip(*macro_tokens)[1]
	#let's go through it again, this time extracting all macros that are in some way a number.
	numeric_macros = blist.blist()
	for i in macros:
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
		yield (i[0], val)
