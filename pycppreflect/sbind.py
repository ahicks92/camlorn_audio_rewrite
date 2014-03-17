#!/usr/bin/env python

r"""
Python CPlusPlus Reflection: Simple Bind
========================================

A simplified binder of clang's AST output for use in automating
code generation via preprocessor reflection of existing c++ code.

Basically I wanted a stripped down set of scripts to handle
c++ parsing using clang's python bindings.  

@Note
	You MUST INCLUDE libclang.dll (libclang.so) in your path [2]
	
@Original Intent
	I hate writing boilerplate, who doesn't?  At one time or another I have
	had Unity 3D projects that required massive linking to existing C++ libraries.

	So for every:
	extern "C" __declspec void foo(int bar){}

	I had to write:
	#if UNITY_STANDALONE_WIN
		[DllImport("unityplugin.dll")] //[1] Windows will not auto-append '.dll' to library name.  
		public static void foo(int bar);
	#else
		[DllImport("unityplugin")]
		public static void foo(int bar);


	No fun :-(   	

@links
	[1] - http://www.mono-project.com/Interop_with_Native_Libraries#Library_Names
	[2] - http://eli.thegreenplace.net/2011/07/03/parsing-c-in-python-with-clang/  (See 'Setting Up')
	
@TODO:
	- Need a recursive method to handle nested pointers (void** results in a function type of pointer*)
	- Move helper code and parser to separate files
	- Add more cursor handlers or adopt a more reflective approach to parsing cursor.
	  Keep in mind, the goal is simply to make it easier to find function declarations, not 
	  rewrite all the clang bindings.
"""

import os
import sys
import clang.cindex

from pprint import pprint

class ParamDecl(object):
	def __init__(self):
		self.components_ = {}
		
	@staticmethod
	def flatten(cursor):
		""" Factory method to create paramter declaration
		"""
		if cursor.kind != clang.cindex.CursorKind.PARM_DECL:
			return None

		#pprint(Helpers.get_function_info(cursor))
		ret = ParamDecl()
		ret.location = cursor.location
		ret.displayname = cursor.displayname
		ret.param_type = cursor.type.get_canonical()

		return ret

		
	#-----------------------------------
	@property
	def is_pointer(self):
		""" return whether or not parameter is a pointer
		"""
		return self.components_['is_pointer']
		
	@is_pointer.setter
	def is_pointer(self,value):
		""" set whether or not parameter is a pointer
		"""
		self.components_['is_pointer'] = value
		
		
	#-----------------------------------
	@property
	def location(self):
		""" get location of parameter in source
		"""
		return self.components_['location']
		
	@location.setter
	def location(self,value):
		""" set parameter's location in source
		"""
		self.components_['location'] = value
		
	
	#-----------------------------------
	@property
	def displayname(self):
		""" get display name
		
		example: void foo(int c) -> c
		"""
		return self.components_['displayname']
		
	@displayname.setter
	def displayname(self,value):
		""" set display name
		"""
		self.components_['displayname'] = value
		
		
	#-----------------------------------
	@property
	def param_type(self):
		""" get parameter type
		"""
		return self.components_['param_type']
		
	@param_type.setter
	def param_type(self,value):
		"""	set parameter type
		
		@type value: clang.cindex.Type 
		@param value: Type for this parameter (assumed to be valid)
		"""
		if value.kind == clang.cindex.TypeKind.POINTER:
			self.is_pointer = True
			self.components_['param_type'] = value.get_pointee().kind.name.lower()
		else:
			self.is_pointer = False
			self.components_['param_type'] = value.kind.name.lower()
		
		
	def __repr__(self):
		return str(self)
		
	def __str__(self):
		if self.is_pointer:
			return self.components_['param_type'] + "* " + self.components_['displayname']
		else:
			return self.components_['param_type'] + " " + self.components_['displayname']
			
	def dump(self):
		print "\n<Parameter: "+ str(self) + ">"
		pprint(self.components_)	
		
class FunctionDecl(object):
	def __init__(self):
		self.components_ = {}
		self.is_result_pointer = False
		
	@staticmethod
	def flatten(cursor):
		""" Factory method to create function declaration
		"""
		if cursor.kind != clang.cindex.CursorKind.FUNCTION_DECL:
			return None
			
		
		ret = FunctionDecl()
		ret.location 			= str(cursor.location)
		ret.spelling 			= str(cursor.spelling)
		ret.displayname 		= str(cursor.displayname)
		ret.usr 				= str(cursor.get_usr())
		ret.kind 				= str(cursor.kind)

		ret.params 				= cursor.get_argument_list()
		ret.result_type 		= cursor.result_type.get_canonical()		
		return ret
		
	#-----------------------------------
	@property
	def location(self):
		""" get file location of function
		"""
		return self.components_['location']
		
	@location.setter
	def location(self,value):
		""" set file location of function
		"""
		self.components_['location'] = value

	
	#-----------------------------------	
	@property
	def kind(self):
		""" get clang.cindex CursorType
		"""
		return self.components_['kind']
		
	@kind.setter
	def kind(self,value):
		""" set clang.cindex CursorType
		"""
		self.components_['kind'] = value
	
	
	#-----------------------------------
	@property
	def usr(self):
		""" get Unified Symbol Resultion (USR)
		
		Note: see clang/cindex.py Cursor.get_usr for a full description of USR
		"""
		return self.components_['usr']
		
	@usr.setter
	def usr(self,value):
		""" set USR
		"""
		self.components_['usr'] = value
	
	
	#-----------------------------------
	@property
	def spelling(self):
		""" get spelling (simple name)
		
		example: void foo(int c) -> foo
		"""
		return self.components_['spelling']
		
	@spelling.setter
	def spelling(self,value):
		""" set spelling (simple name)
		"""
		self.components_['spelling'] = value		
		
	
	#-----------------------------------
	@property
	def displayname(self):
		"""	get display name
		
		example: void foo(int c) -> foo (int c)
		"""
		return self.components_['displayname']
		
	@displayname.setter
	def displayname(self,value):
		"""	set display name
		"""
		self.components_['displayname'] = value			
		
	
	#-----------------------------------
	@property
	def params(self):
		"""	parameters for this function
		"""	
		return self.components_['params']
		
	@params.setter
	def params(self,value):
		"""	set parameters for this function
		
		@type value: 'list' of cland.cindex.Cursor 
		@param value: List of clang cursors representing function arguments
		"""
		if 'params' not in self.components_:
			self.components_['params'] = []
		for arg in value:
			tmp = ParamDecl.flatten(arg)
			if tmp != None:
				self.components_['params'].append(tmp)	
		
		
	#-----------------------------------
	@property
	def is_result_pointer(self):
		""" get if result (return value) is a pointer
		"""
		return self.components_['is_result_pointer']
		
	@is_result_pointer.setter
	def is_result_pointer(self,value):
		""" set if result (return value) is a pointer
		"""	
		self.components_['is_result_pointer'] = value
		
		
	#-----------------------------------
	@property
	def result_type(self):
		"""	result (or return) type of this function
		
		Only returns the type name so float* and float both would return 'float'
		Check 'is_result_pointer' to determine whether the return type is a pointer.
		
		@TODO: Make result type its own class
		"""
		return self.components_['result_type']
		
	@result_type.setter
	def result_type(self,value):
		"""	set result (or return) type of this function
		"""
		if value.kind == clang.cindex.TypeKind.POINTER:
			self.is_result_pointer = True
			self.components_['result_type'] = value.get_pointee().kind.name.lower()	
		else:
			self.is_result_pointer = False
			self.components_['result_type'] = value.kind.name.lower()			
	
	
	def __repr__(self):
		return str(self)
		
	def __str__(self):
		if self.is_result_pointer:
			return self.result_type + "* " + self.displayname
		else:
			return self.result_type + " " + self.displayname
	
	def dump(self):
		print "\n<Function: "+ str(self) + ">"
		pprint(self.components_)	
		
class ExternDecl(object):
	def __init__(self):
		pass
		
	@staticmethod	
	def flatten(cursor):
		if cursor.kind != clang.cindex.CursorKind.LINKAGE_SPEC:
			return None
		
		ret = []
		for child in cursor.get_children():
			tmp = FunctionDecl.flatten(child)
			if tmp != None:
				ret.append(tmp)

		return ret

class Parser(object):
	def __init__(self):
		self.components_ = {}
		self.is_relative = True
		self.is_recursive = True
		self.clang_args = ['-x', 'c++','-cc1']
		self.cursor_handles = "" #cursor_handlers setter temporarily disabled
		self.functions = []
	
	#-------------------------------------
	@property
	def cursor_handles(self):
		""" Get cursor query types
		"""
		return self.components_['cursor_handles']
		
	@cursor_handles.setter
	def cursor_handles(self,value):
		self.components_['cursor_handles'] = {
			clang.cindex.CursorKind.LINKAGE_SPEC:ExternDecl
			}
		
		
	#-------------------------------------
	@property
	def is_relative(self):
		""" Get whether to use relative pathing.  If true, only
		source located in subdirectorties will be fully parsed
		
		@example: if input file is /foo/bar/test.h, only files
		under /foo/bar will be parsed.  (Includes /foo/bar/baz 
		if is_recursive is also true)
		"""
		return self.components_['is_relative']
		
	@is_relative.setter
	def is_relative(self,value):
		self.components_['is_relative'] = value

		
	#-------------------------------------
	@property
	def is_recursive(self):
		""" Get whether to use relative pathing.  If true, only
		source located in subdirectorties will be fully parsed
		
		@example: if input file is /foo/bar/test.h, only files
		under /foo/bar will be parsed.  (Includes /foo/bar/baz 
		if is_recursive is also true)
		"""
		return self.components_['is_recursive']
		
	@is_recursive.setter
	def is_recursive(self,value):
		self.components_['is_recursive'] = value
	
	#-------------------------------------
	@property
	def clang_args(self):
		""" Get clang translation unit parsing arguments
		
		@defaults: ['-x', 'c++','-cc1']
		"""
		return self.components_['clang_args']
		
	@clang_args.setter
	def clang_args(self,value):
		""" Set clang translation unit parsing arguments
		"""
		self.components_['clang_args'] = value
		
		
	#---------------------------------
	def parse(self,initialFilePath):
		self.initialFilePath_ = initialFilePath
		self.rootPath_ = os.path.realpath(os.path.dirname(initialFilePath))
		
		self.clangIndex_ = clang.cindex.Index.create()
		self.translationUnit_ = self.clangIndex_.parse(self.initialFilePath_, self.clang_args)
		
		print "clang args: ",self.clang_args
		
		
		if not self.translationUnit_:
			print "Unable to load input"
			return
		
		self._parse_cursor(self.translationUnit_.cursor)
		
	
	def _valid_path(self,cursorPath):
		""" Return whether cursor path is valid or not
		
		@validity: Validity is determined by the pathing flags
		"""
		if(cursorPath == self.rootPath_):
			return True
			
		if self.is_relative:
			if cursorPath.find(self.rootPath_)==-1:
				return False
	
		#if here, path is not working directory so just check if recurse is true.
		return self.is_recursive

	def _parse_cursor(self,cursor):
		"""	Parse Clang cursor 
		"""
		cursorPath = os.path.realpath(os.path.dirname(str(cursor.location.file)))
		
		if self._valid_path(cursorPath):
			#Note: Initially, self.cursors are ALWAYS clang.cindex.CursorKind.LINKAGE_SPEC
			#Todo: Write additional cursor handles or come up with dummies
			if cursor.kind in self.cursor_handles:
				fns = self.cursor_handles[cursor.kind].flatten(cursor)
				self.functions += fns
				
				for f in fns:
					f.dump()

		# Recurse for children of this cursor
		for c in cursor.get_children():
			self._parse_cursor(c)	
		
#todo: move helpers to separate file
class Helpers(object):

	@staticmethod
	def get_info(node, depth=0):
		return { 'kind' : node.kind,
				 'usr' : node.get_usr(),
				 'spelling' : node.spelling,
				 'location' : node.location,
				 'extent.start' : node.extent.start,
				 'extent.end' : node.extent.end,
				 'is_definition' : node.is_definition(),
				 'definition':node.get_definition(),
				 'spelling':node.spelling,
				 'displayname':node.displayname}
				 
	@staticmethod
	def get_function_info(node, depth=0):
		return { 'kind' : node.kind,
				 'usr' : node.get_usr(),
				 'spelling' : node.spelling,
				 'spelling':node.spelling,
				 'displayname':node.displayname,
				 'args':node.get_argument_list(),
				 'result_type':str(node.result_type.kind)
			 }
			 	
	@staticmethod
	def output_cursor_and_children(cursor):
		Helpers.get_info(cursor)

		# Recurse for children of this cursor
		has_children = False;
		for c in cursor.get_children():
			if not has_children:
				has_children = True
			Helpers.output_cursor_and_children(c)
