from . import flatten_cursor
import clang.cindex as cindex
import itertools

def extract_functions(cursor):
	"""Returns a list of tuples of the following format:
[(c1, f1), (c2,f2), ..., (cn, fn)]
Where c1...cn are the cursors which point to the function definitions; and
f1...fn are tuples of the following form:
(name, (type1, arg1), (type2, arg2), ... (typen, argn))
As usual, this is an iterator.
Note that the types returned are canonical, that is, they are what would result without typedefs.  This is most useful for automatic generation of code."""
	#get an iterator over all function definitions.
	function_cursors = itertools.ifilter(lambda c: c.kind == cindex.CursorKind.FUNCTION_DECL, flatten_cursor(cursor))
	for i in function_cursors:
		name = i.spelling
		arguments = filter(lambda x: x.kind == cindex.CursorKind.PARM_DECL, flatten_cursor(i))
		out = []
		out.append(name)
		for j in arguments:
			out.append((j.type.get_canonical().spelling, j.spelling))
		yield (i, tuple(out))
