def flatten_cursor(cursor):
	"""Turns a cursor into a iterator of cursors which contains itself and all of its children, recursively."""
	yield cursor
	for i in cursor.get_children():
		for j in flatten_cursor(i):
			yield j




