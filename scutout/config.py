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
		self.use_same_radius= False
		self.source_radius= 300 # arcsec
		self.cutout_factor= 5 
		
		self.convert_to_jypix_units= True
		self.subtract_bkg= False
		self.regrid= True
		self.convolve= True
		self.crop= True
		self.crop_size= 200 # in pixels

		# - Background calculation
		self.bkg_estimator= 'sigmaclip'
		self.bkg_inner_radius_factor= 1.1
		self.bkg_outer_radius_factor= 1.2
		self.bkg_max_nan_thr= 0.1


		# - FIRST survey options
		first_options= {
			"metadata": ""
		}

		# - NVSS survey options
		nvss_options= {
			"metadata": ""
		}

		# - MGPS survey options
		mgps_options= {
			"metadata": ""
		}

		# - SCORPIO ATCA survey options
		scorpio_atca_2_1_options= {
			"metadata": ""
		}

		# - SCORPIO ASKAP survey options
		scorpio_askap15_b1_options= {
			"metadata": ""
		}
		scorpio_askap36_b123_options= {
			"metadata": ""
		}
		
		# - THOR survey options
		thor_options= {
			"metadata": ""
		}

		# - Spitzer IRAC survey options
		spitzer_irac_3_6_options= {
			"metadata": ""
		}
		spitzer_irac_4_5_options= {
			"metadata": ""
		}
		spitzer_irac_5_8_options= {
			"metadata": ""
		}
		spitzer_irac_8_options= {
			"metadata": ""
		}

		# - Spitzer MIPS 24
		spitzer_mips_24_options= {
			"metadata": ""
		}

		# - Herschel HIGAL 
		herschel_higal_70_options= {
			"metadata": ""
		}
		herschel_higal_160_options= {
			"metadata": ""
		}
		herschel_higal_250_options= {
			"metadata": ""
		}
		herschel_higal_350_options= {
			"metadata": ""
		}
		herschel_higal_500_options= {
			"metadata": ""
		}
		
		# - WISE 
		wise_3_4_options= {
			"metadata": ""
		}
		wise_4_6_options= {
			"metadata": ""
		}
		wise_12_options= {
			"metadata": ""
		}
		wise_22_options= {
			"metadata": ""
		}

		# - APEX ATLAS GAL
		apex_atlasgal_options= {
			"metadata": ""
		}
		apex_atlasgal_planck_options= {
			"metadata": ""
		}

		# - MSX
		msx_8_3_options= {
			"metadata": ""
		}
		msx_12_1_options= {
			"metadata": ""
		}
		msx_14_7_options= {
			"metadata": ""
		}	
		msx_21_3_options= {
			"metadata": ""
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
		
		if self.parser.has_option('CUTOUT_SEARCH', 'use_same_radius'):
			self.use_same_radius= self.parser.getboolean('CUTOUT_SEARCH', 'use_same_radius') 		
	
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
		
		if self.parser.has_option('CUTOUT_SEARCH', 'subtract_bkg'):
			self.subtract_bkg= self.parser.getboolean('CUTOUT_SEARCH', 'subtract_bkg') 	

		if self.parser.has_option('CUTOUT_SEARCH', 'regrid'):
			self.regrid= self.parser.getboolean('CUTOUT_SEARCH', 'regrid') 		

		if self.parser.has_option('CUTOUT_SEARCH', 'convolve'):
			self.convolve= self.parser.getboolean('CUTOUT_SEARCH', 'convolve') 
		
		if self.parser.has_option('CUTOUT_SEARCH', 'crop'):
			self.crop= self.parser.getboolean('CUTOUT_SEARCH', 'crop')

		if self.parser.has_option('CUTOUT_SEARCH', 'crop_size'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'crop_size')
			if option_value:
				self.crop_size= int(option_value)

		# - Parse background options
		if self.parser.has_option('BKG_SUBTRACTION', 'bkg_estimator'):
			option_value= self.parser.get('BKG_SUBTRACTION', 'bkg_estimator')	
			if option_value:
				self.bkg_estimator= option_value

		if self.parser.has_option('BKG_SUBTRACTION', 'bkg_inner_radius_factor'):
			option_value= self.parser.get('BKG_SUBTRACTION', 'bkg_inner_radius_factor')	
			if option_value:
				self.bkg_inner_radius_factor= float(option_value)

		if self.parser.has_option('BKG_SUBTRACTION', 'bkg_outer_radius_factor'):
			option_value= self.parser.get('BKG_SUBTRACTION', 'bkg_outer_radius_factor')	
			if option_value:
				self.bkg_outer_radius_factor= float(option_value)

		if self.parser.has_option('BKG_SUBTRACTION', 'bkg_max_nan_thr'):
			option_value= self.parser.get('BKG_SUBTRACTION', 'bkg_max_nan_thr')	
			if option_value:
				self.bkg_max_nan_thr= float(option_value)


		# - Parse FIRST DATA section options
		if self.parser.has_option('FIRST_DATA', 'metadata'):
			option_value= self.parser.get('FIRST_DATA', 'metadata')	
			if option_value:
				self.survey_options['first']['metadata']= option_value

		# - Parse NVSS DATA section options
		if self.parser.has_option('NVSS_DATA', 'metadata'):
			option_value= self.parser.get('NVSS_DATA', 'metadata')	
			if option_value:
				self.survey_options['nvss']['metadata']= option_value

		# - Parse MGPS DATA section options
		if self.parser.has_option('MGPS_DATA', 'metadata'):
			option_value= self.parser.get('MGPS_DATA', 'metadata')	
			if option_value:
				self.survey_options['mgps']['metadata']= option_value

		# - Parse WISE section options
		if self.parser.has_option('WISE_3_4_DATA', 'metadata'):
			option_value= self.parser.get('WISE_3_4_DATA', 'metadata')	
			if option_value:
				self.survey_options['wise_3_4']['metadata']= option_value

		if self.parser.has_option('WISE_4_6_DATA', 'metadata'):
			option_value= self.parser.get('WISE_4_6_DATA', 'metadata')	
			if option_value:
				self.survey_options['wise_4_6']['metadata']= option_value

		if self.parser.has_option('WISE_12_DATA', 'metadata'):
			option_value= self.parser.get('WISE_12_DATA', 'metadata')	
			if option_value:
				self.survey_options['wise_12']['metadata']= option_value

		if self.parser.has_option('WISE_22_DATA', 'metadata'):
			option_value= self.parser.get('WISE_22_DATA', 'metadata')	
			if option_value:
				self.survey_options['wise_22']['metadata']= option_value

		# - Parse HERSCHEL section options
		if self.parser.has_option('HERSCHEL_HIGAL70_DATA', 'metadata'):
			option_value= self.parser.get('HERSCHEL_HIGAL70_DATA', 'metadata')	
			if option_value:
				self.survey_options['higal_70']['metadata']= option_value

		if self.parser.has_option('HERSCHEL_HIGAL160_DATA', 'metadata'):
			option_value= self.parser.get('HERSCHEL_HIGAL160_DATA', 'metadata')	
			if option_value:
				self.survey_options['higal_160']['metadata']= option_value

		if self.parser.has_option('HERSCHEL_HIGAL250_DATA', 'metadata'):
			option_value= self.parser.get('HERSCHEL_HIGAL250_DATA', 'metadata')	
			if option_value:
				self.survey_options['higal_250']['metadata']= option_value

		if self.parser.has_option('HERSCHEL_HIGAL350_DATA', 'metadata'):
			option_value= self.parser.get('HERSCHEL_HIGAL350_DATA', 'metadata')	
			if option_value:
				self.survey_options['higal_350']['metadata']= option_value

		if self.parser.has_option('HERSCHEL_HIGAL500_DATA', 'metadata'):
			option_value= self.parser.get('HERSCHEL_HIGAL500_DATA', 'metadata')	
			if option_value:
				self.survey_options['higal_500']['metadata']= option_value

		# - Parse Spitzer IRAC section options
		if self.parser.has_option('SPITZER_IRAC3_6_DATA', 'metadata'):
			option_value= self.parser.get('SPITZER_IRAC3_6_DATA', 'metadata')	
			if option_value:
				self.survey_options['irac_3_6']['metadata']= option_value
	
		if self.parser.has_option('SPITZER_IRAC4_5_DATA', 'metadata'):
			option_value= self.parser.get('SPITZER_IRAC4_5_DATA', 'metadata')	
			if option_value:
				self.survey_options['irac_4_5']['metadata']= option_value

		if self.parser.has_option('SPITZER_IRAC5_8_DATA', 'metadata'):
			option_value= self.parser.get('SPITZER_IRAC5_8_DATA', 'metadata')	
			if option_value:
				self.survey_options['irac_5_8']['metadata']= option_value

		if self.parser.has_option('SPITZER_IRAC8_DATA', 'metadata'):
			option_value= self.parser.get('SPITZER_IRAC8_DATA', 'metadata')	
			if option_value:
				self.survey_options['irac_8']['metadata']= option_value

		# - Parse Spitzer MIPS section options
		if self.parser.has_option('SPITZER_MIPS24_DATA', 'metadata'):
			option_value= self.parser.get('SPITZER_MIPS24_DATA', 'metadata')	
			if option_value:
				self.survey_options['mips_24']['metadata']= option_value
			
		# - Parse APEX data
		if self.parser.has_option('APEX_ATLASGAL_DATA', 'metadata'):
			option_value= self.parser.get('APEX_ATLASGAL_DATA', 'metadata')	
			if option_value:
				self.survey_options['atlasgal']['metadata']= option_value

		if self.parser.has_option('APEX_ATLASGAL_PLANCK_DATA', 'metadata'):
			option_value= self.parser.get('APEX_ATLASGAL_PLANCK_DATA', 'metadata')	
			if option_value:
				self.survey_options['atlasgal_planck']['metadata']= option_value

		# - Parse MSX
		if self.parser.has_option('MSX_8_3_DATA', 'metadata'):
			option_value= self.parser.get('MSX_8_3_DATA', 'metadata')	
			if option_value:
				self.survey_options['msx_8_3']['metadata']= option_value

		if self.parser.has_option('MSX_12_1_DATA', 'metadata'):
			option_value= self.parser.get('MSX_12_1_DATA', 'metadata')	
			if option_value:
				self.survey_options['msx_12_1']['metadata']= option_value

		if self.parser.has_option('MSX_14_7_DATA', 'metadata'):
			option_value= self.parser.get('MSX_14_7_DATA', 'metadata')	
			if option_value:
				self.survey_options['msx_14_7']['metadata']= option_value

		if self.parser.has_option('MSX_21_3_DATA', 'metadata'):
			option_value= self.parser.get('MSX_21_3_DATA', 'metadata')	
			if option_value:
				self.survey_options['msx_21_3']['metadata']= option_value

		# - Parse SCORPIO ATCA section options
		if self.parser.has_option('SCORPIO_ATCA_2_1_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ATCA_2_1_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_atca_2_1']['metadata']= option_value

		# - Parse SCORPIO ASKAP section options	
		if self.parser.has_option('SCORPIO_ASKAP15_b1_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP15_b1_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap15_b1']['metadata']= option_value

		if self.parser.has_option('SCORPIO_ASKAP36_b123_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP36_b123_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap36_b123']['metadata']= option_value

		# - Parse THOR survey
		if self.parser.has_option('THOR_DATA', 'metadata'):
			option_value= self.parser.get('THOR_DATA', 'metadata')	
			if option_value:
				self.survey_options['thor']['metadata']= option_value
	
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
		
		# - Check survey options
		valid_surveys= list(self.survey_options.keys())
		logger.info("Checking that search surveys exist in supported survey list ...")
		print(valid_surveys)
		for survey in self.surveys:
			if not survey in valid_surveys:
				logger.error("Survey " + survey + " is unknown and/or not supported!")
				return -1

		# - Check survey metadata is not empty and existing file
		for survey in self.surveys:
			metadata= self.survey_options[survey]['metadata']
			if not metadata:
				logger.error("Metadata path for survey " + survey + " is empty string (please specify file in config)!")
				return -1
			if not os.path.isfile(metadata):
				logger.error("Metadata file " + metadata + " is not existing in filesystem!")
				return -1

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
		

