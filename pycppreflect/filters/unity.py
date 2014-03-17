#!/usr/bin/env python
import os
import sys
import unittest
import string

from filterbase import *
from collections import defaultdict

sys.path.append("..")
from pycppreflect.sbind import *

class ImportAttribute(object):
	def __init__(self,plugin,sig):
		self.plugin = plugin
		self.signature = sig
		
	def __repr__(self):
		return str(self)
		
	def __str__(self):
		return "\t\t[DllImport(\""+self.plugin+"\")]\n"+\
			   "\t\tpublic static "+self.signature+";\n"

		
class ImportEditorAttribute(object):
	"""
	@format
		[UnmanagedFunctionPointer(CallingConvention.Cdecl)]
		private delegate void foo ();
		Delegate_<function_name> plugin_<function_name>;
	"""
	def __init__(self,plugin,name,sig):
		self.plugin = plugin
		self.signature = sig
		self.name = name
	
	def __repr__(self):
		return str(self)
		
	def __str__(self):
		return "\t\t[UnmanagedFunctionPointer(CallingConvention.Cdecl)]\n"+\
			   "\t\tprivate delegate "+self.signature+";\n"+\
			   "\t\tDelegate_"+self.name+" plugin_"+self.name+";\n"
	
class ImportDelegate(object):
	"""
	@format
			pAddressOfFunctionToCall = NativeMethods.GetProcAddress(plugin_dll.Value, "plugin_<function_name>");
			plugin_<function_name> = (Delegate_New)Marshal.GetDelegateForFunctionPointer(pAddressOfFunctionToCall,typeof(Delegate_<function_name>));
	"""
	def __init__(self,name):
		self.name = name
	
	def __repr__(self):
		return str(self)
		
	def __str__(self):
		return "\t\t\tpAddressOfFunctionToCall = NativeMethods.GetProcAddress(plugin_dll.Value, \"plugin_"+self.name+"\");\n"+\
			   "\t\t\tplugin_"+self.name+" = (Delegate_New)Marshal.GetDelegateForFunctionPointer(pAddressOfFunctionToCall,typeof(Delegate_"+self.name+"));\n"

class UnityPlatforms(object):
	""" Unity specific platform definitions [1]
	
	@links
		[1] - http://docs.unity3d.com/Documentation/Manual/PlatformDependentCompilation.html
	"""
	EDITOR 				= "UNITY_EDITOR" #	Define for calling Unity Editor scripts from your game code.
	STANDALONE_OSX		= "UNITY_STANDALONE_OSX" #Platform define for compiling/executing code specifically for Mac OS (This includes Universal, PPC and Intel architectures).
	DASHBOARD_WIDGET	= "UNITY_DASHBOARD_WIDGET" #Platform define when creating code for Mac OS dashboard widgets.
	WINDOWS				= "UNITY_STANDALONE_WIN" #Use this when you want to compile/execute code for Windows stand alone applications.
	LINUX				= "UNITY_STANDALONE_LINUX" #Use this when you want to compile/execute code for Linux stand alone applications.
	STANDALONE			= "UNITY_STANDALONE" #Use this to compile/execute code for any standalone platform (Mac, Windows or Linux).
	WEBPLAYER			= "UNITY_WEBPLAYER" #Platform define for web player content (this includes Windows and Mac Web player executables).
	WII					= "UNITY_WII" #Platform define for compiling/executing code for the Wii console.
	IPHONE				= "UNITY_IPHONE" #Platform define for compiling/executing code for the iPhone platform.
	ANDROID				= "UNITY_ANDROID" #Platform define for the Android platform.
	PS3					= "UNITY_PS3" #Platform define for running PlayStation 3 code.
	XBOX360				= "UNITY_XBOX360" #Platform define for executing Xbox 360 code.
	NACL				= "UNITY_NACL" #Platform define when compiling code for Google native client (this will be set additionally to UNITY_WEBPLAYER).
	FLASH				= "UNITY_FLASH" #	Platform define when compiling code for Adobe Flash.

	# pycppreflect custom
	UNDEFINED			= "UNDEFINED" #not part of the unity platform definition set, used as default placeholder
	
class Unity(FilterBase):
	"""	Unity output filter
	
	@descrip
		Unity output filter takes as input a list of function declarations and returns
		text boilerplate for Unity to create the necessary import/export functions.
		
		This is meant to work in conjunction w/ a 
	"""
	def __init__(self):
		super(FilterBase, self).__init__()
		self.preprocessor_types = [UnityPlatforms.EDITOR,UnityPlatforms.ANDROID,UnityPlatforms.WINDOWS,UnityPlatforms.UNDEFINED]
		self.components_ = {}
		self.plugin = "unnamed_plugin"
		
		self._preprocessor_attrs = {
			UnityPlatforms.EDITOR:lambda x:ImportEditorAttribute(self.plugin,x.spelling,str(x)),
			UnityPlatforms.ANDROID:lambda x:ImportAttribute(self.plugin,str(x)),
			UnityPlatforms.WINDOWS:lambda x:ImportAttribute(self.plugin+".dll",str(x)),
			UnityPlatforms.LINUX:lambda x:ImportAttribute(self.plugin+".so",str(x)),
			UnityPlatforms.UNDEFINED:lambda x:ImportAttribute(self.plugin,str(x))
		}
		self._preprocessor_attrs = defaultdict(lambda x:ImportAttribute(self.plugin,str(x)), self._preprocessor_attrs)	#todo: fix, default lambda isn't working
		
		
		self._preprocessor_decls = {
			UnityPlatforms.EDITOR:lambda x:ImportDelegate(x.spelling),
			UnityPlatforms.ANDROID:lambda x:None,
			UnityPlatforms.WINDOWS:lambda x:None,
			UnityPlatforms.LINUX:lambda x:None,
			UnityPlatforms.UNDEFINED:lambda x:None
		}
		self._preprocessor_decls = defaultdict(lambda x: ImportDelegate(x.spelling), self._preprocessor_decls)	#todo: fix, default lambda isn't working
		
		
		
	#-----------------------------------
	@property
	def plugin(self):
		return self.components_['plugin']
		
	@plugin.setter
	def plugin(self,value):
		#strip extension for Unity
		self.components_['plugin'] = os.path.splitext(value)[0]
		
	def filter(self,objects):
		""" Filter function declarations to extract Unity CS script attributes and declarations
		for dll import.
		"""
		attrs = defaultdict(list)
		decls = defaultdict(list)
		
		#assuming objects are FunctionDecls
		for obj in objects:
			# grab import attributes
			tmp = self._process_function_attrs(obj)
			for k,v in tmp.items():
				attrs[k].append(v)
			
			# grab import delegates (ONLY used for UNITY_EDITOR currently)
			tmp = self._process_function_decls(obj)
			for k,v in tmp.items():
				if v:
					decls[k].append(v)
		self._dump(attrs,decls)
		self._dump_template(attrs,decls)
		
	def _attr_tag_from_key(self,key):
		"""	Get template attribute tag from key
		@todo
			- Replace with dict
		"""
		tag = ""
		if key == UnityPlatforms.EDITOR:
			tag='editor_import_attributes'
		elif key == UnityPlatforms.WINDOWS:
			tag = 'windows_import_attributes'
		elif key == UnityPlatforms.ANDROID:
			tag = 'android_import_attributes'
		elif key == UnityPlatforms.UNDEFINED:
			tag = 'undefined_import_attributes'
		else:
			tag = 'undefined_import_attributes'
		return tag
		
	def _decl_tag_from_key(self,key):
		"""	Get template declaration tag from key		
		@todo
			- Replace with dict
		"""
		tag = ""
		if key == UnityPlatforms.EDITOR:
			tag='editor_import_delegates'
		return tag	
		
	def _dump_template(self,attrs,decls):
		""" Dump Unity data to command line, formatted with a Unity CS script template.
		"""
		template_args = defaultdict(str)
		
		for key,values in attrs.items():
			tag = self._attr_tag_from_key(key)
			for value in values:
				template_args[tag] += str(value) + "\n"
				
		for key,values in decls.items():
			tag = self._decl_tag_from_key(key)
			print "key: "+key
			print "tag: "+tag
			for value in values:
				
				print tag+": "+str(value)
				template_args[tag] += str(value) + "\n"	
		
		template_args['plugin'] = "\"" + self.plugin + ".dll\"";
		
		filename = os.path.join(os.path.dirname(__file__), 'unity_template.cs')
		file = open(filename)
		source = string.Template(file.read())
		result = source.substitute(template_args)
		print result
		
	def _dump(self,attrs,decls):
		""" Dump Unity data to command line
		"""
		for key,values in decls.items():
			print key
			for value in values:
				print str(value)
			print ""
			
		for key,values in attrs.items():
			print key
			for value in values:
				print str(value)
			print ""
			
	def _process_function_attrs(self,obj):
		"""	Process function attributes for each preprocessor type
		"""
		ret = {}
		for ptype in self.preprocessor_types:
			ret[ptype] = self._preprocessor_attrs[ptype](obj)
		return ret
		
	def _process_function_decls(self,obj):
		"""	Process function declarations for each preprocessor type
		"""
		ret = {}
		for ptype in self.preprocessor_types:
			ret[ptype] = self._preprocessor_decls[ptype](obj)
		return ret	
		
class TestUnityFilter(unittest.TestCase):
	def setUp(self):
		self.functions = []
		
		ret = FunctionDecl()
		ret.displayname 		= 'foo1(char *, int)'
		ret.components_['result_type'] 		= 'int'
		self.functions.append(ret)
		
		ret = FunctionDecl()
		ret.displayname 		= 'foo2(double , int)'
		ret.components_['result_type'] 		= 'void*'
		self.functions.append(ret)
		
		ret = FunctionDecl()
		ret.displayname 		= 'foo3(float)'
		ret.components_['result_type'] 		= 'char**'
		self.functions.append(ret)
		
	def test_process(self):
		unity = Unity()
		unity.plugin = "testplugin.dll"
		unity.filter(self.functions)


if __name__ == '__main__':
    unittest.main()		