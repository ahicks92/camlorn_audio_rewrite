#!/usr/bin/env python

class FilterBase(object):
	def __init__(self):
		self.results = None
		
	def filter(self,objects):
		raise NotImplementedError( "filter not implemented in class" )
		