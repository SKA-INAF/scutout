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
				
		# - Run options		
		self.workdir= os.getcwd()
		self.keep_tmpfiles= True
		self.keep_inputs= False
		self.keep_tmpcutouts= True

		# - Cutout search
		self.surveys= []
		self.outer_cutout= 10 # arcmin
		self.inner_cutout= 1 # arcmin
		self.convert_to_jypix_units= True
		self.regrid= True

		# - FIRST survey options
		first_options= {
			"path": ""
		}

		# - NVSS survey options
		nvss_options= {
			"path": ""
		}

		# - MGPS survey options
		mgps_options= {
			"path": ""
		}

		# - SURVEY options
		self.survey_options= {
			"first" : first_options,
			"nvss" : nvss_options,
			"mgps" : mgps_options
		}

	#==============================
	#     PARSE CONFIG FILE
	#==============================
	def parse(self,filename):
		""" Read input INI config file and set options """

		# ***************************
		# **    READ CONFIG FILE
		# ***************************
		# - Read config parser
		self.parser.read(filename)
		print(self.parser.sections())
		#self.__print_options()

		# ***************************
		# **    PARSE OPTIONS
		# ***************************
		# - Parse RUN section options
		if self.parser.has_option('RUN', 'workdir'):
			option_value= self.parser.get('RUN', 'workdir')	
			if option_value:
				self.workdir= option_value
		
		if self.parser.has_option('RUN', 'keep_tmpfiles'):
			self.keep_tmpfiles= self.parser.getboolean('RUN', 'keep_tmpfiles')		
		if self.parser.has_option('RUN', 'keep_inputs'):
			self.keep_inputs= self.parser.getboolean('RUN', 'keep_inputs')
		if self.parser.has_option('RUN', 'keep_tmpcutouts'):
			self.keep_tmpcutouts= self.parser.getboolean('RUN', 'keep_tmpcutouts')
		
		# - Parse cutout option sections
		if self.parser.has_option('CUTOUT_SEARCH', 'surveys'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'surveys')	
			if option_value:
				self.surveys= option_value.split(",")
				
		if self.parser.has_option('CUTOUT_SEARCH', 'outer_cutout'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'outer_cutout')
			if option_value:
				self.outer_cutout= float(option_value)			
		
		if self.parser.has_option('CUTOUT_SEARCH', 'inner_cutout'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'inner_cutout')
			if option_value:
				self.inner_cutout= float(option_value)	

		if self.parser.has_option('CUTOUT_SEARCH', 'convert_to_jy_pixel'):
			self.convert_to_jypix_units= self.parser.getboolean('CUTOUT_SEARCH', 'convert_to_jy_pixel') 		
		
		if self.parser.has_option('CUTOUT_SEARCH', 'regrid'):
			self.regrid= self.parser.getboolean('CUTOUT_SEARCH', 'regrid') 		

		# - Parse FIRST DATA section options
		if self.parser.has_option('FIRST_DATA', 'path'):
			option_value= self.parser.get('FIRST_DATA', 'path')	
			if option_value:
				self.survey_options['first']['path']= option_value

		# - Parse NVSS DATA section options
		if self.parser.has_option('NVSS_DATA', 'path'):
			option_value= self.parser.get('NVSS_DATA', 'path')	
			if option_value:
				self.survey_options['nvss']['path']= option_value

		# - Parse MGPS DATA section options
		if self.parser.has_option('MGPS_DATA', 'path'):
			option_value= self.parser.get('MGPS_DATA', 'path')	
			if option_value:
				self.survey_options['mgps']['path']= option_value
			
		# ***************************
		# **    VALIDATE CONFIG
		# ***************************
		if self.__validate()<0:
			logger.error("Invalid configuration options detected, please check!")
			return -1

		return 0

	#==============================
	#     VALIDATE CONFIG
	#==============================
	def __validate(self):
		""" Validate config file """
		
		# - Check mandatory options
		# ...
		# ...
		
		return 0

	#==============================
	#     PRINT OPTIONS
	#==============================
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
		

