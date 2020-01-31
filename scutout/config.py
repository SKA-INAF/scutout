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
		self.__set_defaults()

		# - Config file parser		
		self.parser= ConfigParser.ConfigParser()
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
		
		# - Cutout search
		self.surveys= []
		self.source_radius= 300 # arcsec
		self.cutout_factor= 5 
		
		self.convert_to_jypix_units= True
		self.regrid= True
		self.convolve= True
		self.crop= True
		self.crop_size= 200 # in pixels

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

		# - SCORPIO ATCA survey options
		scorpio_atca_2_1_options= {
			"path": ""
		}

		# - SCORPIO ASKAP survey options
		scorpio_askap15_b1_options= {
			"path": ""
		}
		scorpio_askap36_b123_options= {
			"path": ""
		}
		
		# - THOR survey options
		thor_options= {
			"path": ""
		}

		# - Spitzer IRAC survey options
		spitzer_irac_3_6_options= {
			"path": ""
		}
		spitzer_irac_4_5_options= {
			"path": ""
		}
		spitzer_irac_5_8_options= {
			"path": ""
		}
		spitzer_irac_8_options= {
			"path": ""
		}

		# - Spitzer MIPS 24
		spitzer_mips_24_options= {
			"path": ""
		}

		# - Herschel HIGAL 
		herschel_higal_70_options= {
			"path": ""
		}
		herschel_higal_160_options= {
			"path": ""
		}
		herschel_higal_250_options= {
			"path": ""
		}
		herschel_higal_350_options= {
			"path": ""
		}
		herschel_higal_500_options= {
			"path": ""
		}
		
		# - WISE 
		wise_3_4_options= {
			"path": ""
		}
		wise_4_6_options= {
			"path": ""
		}
		wise_12_options= {
			"path": ""
		}
		wise_22_options= {
			"path": ""
		}

		# - APEX ATLAS GAL
		apex_atlasgal_options= {
			"path": ""
		}
		apex_atlasgal_planck_options= {
			"path": ""
		}

		# - MSX
		msx_8_3_options= {
			"path": ""
		}
		msx_12_1_options= {
			"path": ""
		}
		msx_14_7_options= {
			"path": ""
		}	
		msx_21_3_options= {
			"path": ""
		}		

		


		# - SURVEY options
		self.survey_options= {
			"first" : first_options,
			"nvss" : nvss_options,
			"mgps" : mgps_options,
			"scorpio_atca_2_1" : scorpio_atca_2_1_options,
			"scorpio_askap15_b1" : scorpio_askap15_b1_options,
			"scorpio_askap36_b123" : scorpio_askap36_b123_options,
			"thor" : thor_options,
			"irac_3_6" : spitzer_irac_3_6_options,
			"irac_4_5" : spitzer_irac_4_5_options,
			"irac_5_8" : spitzer_irac_5_8_options,
			"irac_8" : spitzer_irac_8_options,
			"mips_24" : spitzer_mips_24_options,
			"higal_70" : herschel_higal_70_options,
			"higal_160" : herschel_higal_160_options,
			"higal_250" : herschel_higal_250_options,
			"higal_350" : herschel_higal_350_options,
			"higal_500" : herschel_higal_500_options,
			"wise_3_4" : wise_3_4_options,
			"wise_4_6" : wise_4_6_options,
			"wise_12" : wise_12_options,
			"wise_22" : wise_22_options,
			"atlasgal" : apex_atlasgal_options,
			"atlasgal_planck" : apex_atlasgal_planck_options,
			"msx_8_3" : msx_8_3_options,
			"msx_12_1" : msx_12_1_options,
			"msx_14_7" : msx_14_7_options,
			"msx_21_3" : msx_21_3_options,
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
		#if self.parser.has_option('RUN', 'keep_inputs'):
		#	self.keep_inputs= self.parser.getboolean('RUN', 'keep_inputs')
		#if self.parser.has_option('RUN', 'keep_tmpcutouts'):
		#	self.keep_tmpcutouts= self.parser.getboolean('RUN', 'keep_tmpcutouts')
		
		# - Parse cutout option sections
		if self.parser.has_option('CUTOUT_SEARCH', 'surveys'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'surveys')	
			if option_value:
				self.surveys= option_value.split(",")
		
		if self.parser.has_option('CUTOUT_SEARCH', 'source_radius'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'source_radius')
			if option_value:
				self.source_radius= float(option_value)

		if self.parser.has_option('CUTOUT_SEARCH', 'cutout_factor'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'cutout_factor')
			if option_value:
				self.cutout_factor= int(option_value)	
		
		
		if self.parser.has_option('CUTOUT_SEARCH', 'convert_to_jy_pixel'):
			self.convert_to_jypix_units= self.parser.getboolean('CUTOUT_SEARCH', 'convert_to_jy_pixel') 		
		
		if self.parser.has_option('CUTOUT_SEARCH', 'regrid'):
			self.regrid= self.parser.getboolean('CUTOUT_SEARCH', 'regrid') 		

		if self.parser.has_option('CUTOUT_SEARCH', 'convolve'):
			self.convolve= self.parser.getboolean('CUTOUT_SEARCH', 'convolve') 
		
		if self.parser.has_option('CUTOUT_SEARCH', 'crop'):
			self.convolve= self.parser.getboolean('CUTOUT_SEARCH', 'crop')

		if self.parser.has_option('CUTOUT_SEARCH', 'crop_size'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'crop_size')
			if option_value:
				self.crop_size= int(option_value)

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

		# - Parse WISE section options
		if self.parser.has_option('WISE_3_4_DATA', 'path'):
			option_value= self.parser.get('WISE_3_4_DATA', 'path')	
			if option_value:
				self.survey_options['wise_3_4']['path']= option_value

		if self.parser.has_option('WISE_4_6_DATA', 'path'):
			option_value= self.parser.get('WISE_4_6_DATA', 'path')	
			if option_value:
				self.survey_options['wise_4_6']['path']= option_value

		if self.parser.has_option('WISE_12_DATA', 'path'):
			option_value= self.parser.get('WISE_12_DATA', 'path')	
			if option_value:
				self.survey_options['wise_12']['path']= option_value

		if self.parser.has_option('WISE_22_DATA', 'path'):
			option_value= self.parser.get('WISE_22_DATA', 'path')	
			if option_value:
				self.survey_options['wise_22']['path']= option_value

		# - Parse HERSCHEL section options
		if self.parser.has_option('HERSCHEL_HIGAL70_DATA', 'path'):
			option_value= self.parser.get('HERSCHEL_HIGAL70_DATA', 'path')	
			if option_value:
				self.survey_options['higal_70']['path']= option_value

		if self.parser.has_option('HERSCHEL_HIGAL160_DATA', 'path'):
			option_value= self.parser.get('HERSCHEL_HIGAL160_DATA', 'path')	
			if option_value:
				self.survey_options['higal_160']['path']= option_value

		if self.parser.has_option('HERSCHEL_HIGAL250_DATA', 'path'):
			option_value= self.parser.get('HERSCHEL_HIGAL250_DATA', 'path')	
			if option_value:
				self.survey_options['higal_250']['path']= option_value

		if self.parser.has_option('HERSCHEL_HIGAL350_DATA', 'path'):
			option_value= self.parser.get('HERSCHEL_HIGAL350_DATA', 'path')	
			if option_value:
				self.survey_options['higal_350']['path']= option_value

		if self.parser.has_option('HERSCHEL_HIGAL500_DATA', 'path'):
			option_value= self.parser.get('HERSCHEL_HIGAL500_DATA', 'path')	
			if option_value:
				self.survey_options['higal_500']['path']= option_value

		# - Parse Spitzer IRAC section options
		if self.parser.has_option('SPITZER_IRAC3_6_DATA', 'path'):
			option_value= self.parser.get('SPITZER_IRAC3_6_DATA', 'path')	
			if option_value:
				self.survey_options['irac_3_6']['path']= option_value
	
		if self.parser.has_option('SPITZER_IRAC4_5_DATA', 'path'):
			option_value= self.parser.get('SPITZER_IRAC4_5_DATA', 'path')	
			if option_value:
				self.survey_options['irac_4_5']['path']= option_value

		if self.parser.has_option('SPITZER_IRAC5_8_DATA', 'path'):
			option_value= self.parser.get('SPITZER_IRAC5_8_DATA', 'path')	
			if option_value:
				self.survey_options['irac_5_8']['path']= option_value

		if self.parser.has_option('SPITZER_IRAC8_DATA', 'path'):
			option_value= self.parser.get('SPITZER_IRAC8_DATA', 'path')	
			if option_value:
				self.survey_options['irac_8']['path']= option_value

		# - Parse Spitzer MIPS section options
		if self.parser.has_option('SPITZER_MIPS24_DATA', 'path'):
			option_value= self.parser.get('SPITZER_MIPS24_DATA', 'path')	
			if option_value:
				self.survey_options['mips_24']['path']= option_value
			
		# - Parse APEX data
		if self.parser.has_option('APEX_ATLASGAL_DATA', 'path'):
			option_value= self.parser.get('APEX_ATLASGAL_DATA', 'path')	
			if option_value:
				self.survey_options['atlasgal']['path']= option_value

		if self.parser.has_option('APEX_ATLASGAL_PLANCK_DATA', 'path'):
			option_value= self.parser.get('APEX_ATLASGAL_PLANCK_DATA', 'path')	
			if option_value:
				self.survey_options['atlasgal_planck']['path']= option_value

		# - Parse MSX
		if self.parser.has_option('MSX_8_3_DATA', 'path'):
			option_value= self.parser.get('MSX_8_3_DATA', 'path')	
			if option_value:
				self.survey_options['msx_8_3']['path']= option_value

		if self.parser.has_option('MSX_12_1_DATA', 'path'):
			option_value= self.parser.get('MSX_12_1_DATA', 'path')	
			if option_value:
				self.survey_options['msx_12_1']['path']= option_value

		if self.parser.has_option('MSX_14_7_DATA', 'path'):
			option_value= self.parser.get('MSX_14_7_DATA', 'path')	
			if option_value:
				self.survey_options['msx_14_7']['path']= option_value

		if self.parser.has_option('MSX_21_3_DATA', 'path'):
			option_value= self.parser.get('MSX_21_3_DATA', 'path')	
			if option_value:
				self.survey_options['msx_21_3']['path']= option_value

		# - Parse SCORPIO ATCA section options
		if self.parser.has_option('SCORPIO_ATCA_2_1_DATA', 'path'):
			option_value= self.parser.get('SCORPIO_ATCA_2_1_DATA', 'path')	
			if option_value:
				self.survey_options['scorpio_atca_2_1']['path']= option_value

		# - Parse SCORPIO ASKAP section options	
		if self.parser.has_option('SCORPIO_ASKAP15_b1_DATA', 'path'):
			option_value= self.parser.get('SCORPIO_ASKAP15_b1_DATA', 'path')	
			if option_value:
				self.survey_options['scorpio_askap15_b1']['path']= option_value

		if self.parser.has_option('SCORPIO_ASKAP36_b123_DATA', 'path'):
			option_value= self.parser.get('SCORPIO_ASKAP36_b123_DATA', 'path')	
			if option_value:
				self.survey_options['scorpio_askap36_b123']['path']= option_value

		# - Parse THOR survey
		if self.parser.has_option('THOR_DATA', 'path'):
			option_value= self.parser.get('THOR_DATA', 'path')	
			if option_value:
				self.survey_options['thor']['path']= option_value
	
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
		

