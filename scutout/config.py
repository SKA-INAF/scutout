#!/usr/bin/env python

##################################################
###          MODULE IMPORT
##################################################
## STANDARD MODULES
import os
import sys
import string
import logging
import io

## CONFIG PARSER MODULES
from ConfigParser import SafeConfigParser
import ConfigParser

##############################
##     GLOBAL VARS
##############################
logger = logging.getLogger(__name__)

###########################
##     CLASS DEFINITIONS
###########################
class CaseConfigParser(SafeConfigParser):
	def optionxform(self, optionstr):
		return optionstr

class Config(object):
     
	""" Configuration options """

	def __init__(self):
		""" Return a Config object """

		# - Config options
		#self.data_options= {}
		self.__set_defaults()

		# - Config file parser		
		self.parser= ConfigParser.ConfigParser()
		#self.parser= CaseConfigParser(os.environ)
		self.config= None

	def optionxform(self, optionstr):
		return optionstr

	#==============================
	#     SET DEFAULT OPTIONS
	#==============================
	def __set_defaults(self):
		""" Set default options """
				
		# - Main options
		self.surveys= []
		self.workdir= os.getcwd()
		self.outer_cutout= 10 # arcmin
		self.inner_cutout= 1 # arcmin
		self.convertToJyPixelUnits= True

		# - FIRST survey options
		first_options= {
			#"search": False,
			"path": ""
		}

		# - MGPS survey options
		mgps_options= {
			#"search": False,
			"path": ""
		}

		# - SURVEY options
		self.survey_options= {
			"first" : first_options,
			"mgps" : mgps_options
		}

	#==============================
	#     PARSE CONFIG FILE
	#==============================
	def parse(self,filename):
		""" Read input INI config file and set options """

		# - Read config parser
		self.parser.read(filename)
		print(self.parser.sections())
		#self.__print_options()


		# - Check mandatory options
		# ... 

		# - Parse DATA section options
		if self.parser.has_option('DATA', 'surveys'):
			option_value= self.parser.get('DATA', 'surveys')	
			if option_value:
				self.surveys= option_value.split(",")
				print('surveys')
				print(self.surveys)
				print(type(self.surveys))

		# - Parse FIRST DATA section options
		if self.parser.has_option('FIRST_DATA', 'path'):
			option_value= self.parser.get('FIRST_DATA', 'path')	
			if option_value:
				self.survey_options['first']['path']= option_value
			
		# - Parse cutout option sections
		if self.parser.has_option('CUTOUT', 'outer_cutout'):
			option_value= self.parser.get('CUTOUT', 'outer_cutout')
			if option_value:
				self.outer_cutout= float(option_value)			
		
		if self.parser.has_option('CUTOUT', 'inner_cutout'):
			option_value= self.parser.get('CUTOUT', 'inner_cutout')
			if option_value:
				self.inner_cutout= float(option_value)	

		if self.parser.has_option('CUTOUT', 'convert_to_jy_pixel'):
			self.convertToJyPixelUnits= self.parser.getboolean('CUTOUT', 'convert_to_jy_pixel') 		

		return 0

	#==============================
	#     VALIDATE CONFIG
	#==============================
	def __validate(self):
		""" Validate config file """
		
		# - Check mandatory options

	def __print_options(self):
		""" """
	
		sections= self.parser.sections()
		for section in sections:
			print("section=%s" % section)
			options= self.parser.items(section)
			print(options)
			
			for option in options:
				print(option)
				print(type(option))
			#for key, value in options.iteritems():
			#for key, value in section.iteritems():
				#print("Option %s=%s" % (key,str(value)))
		

