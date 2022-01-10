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
try:
	from ConfigParser import SafeConfigParser
	import ConfigParser
except:
	# in Python3 it was renamed from ConfigParser to configparser
	from configparser import SafeConfigParser
	import configparser

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
		try: # py2
			self.parser= ConfigParser.ConfigParser()
		except: # py3
			self.parser= configparser.ConfigParser()

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
		self.multi_input_img_mode= 'best'
		self.convert_to_jypix_units= True
		self.subtract_bkg= False
		self.regrid= True
		self.convolve= True
		self.crop_mode= 'none'
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

		# - VGPS survey options
		vgps_options= {
			"metadata": ""
		}

		# - SGPS survey options
		sgps_options= {
			"metadata": ""
		}

		# - VLASS survey options
		vlass_options= {
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
		scorpio_askap36_b123_ch1_options= {
			"metadata": ""
		}
		scorpio_askap36_b123_ch2_options= {
			"metadata": ""
		}
		scorpio_askap36_b123_ch3_options= {
			"metadata": ""
		}
		scorpio_askap36_b123_ch4_options= {
			"metadata": ""
		}
		scorpio_askap36_b123_ch5_options= {
			"metadata": ""
		}
		
		# - THOR survey options
		thor_options= {
			"metadata": ""
		}

		# - MEERKAT-GPS survey options
		meerkat_gps_options= {
			"metadata": ""
		}
		meerkat_gps_ch1_options= {
			"metadata": ""
		}
		meerkat_gps_ch2_options= {
			"metadata": ""
		}
		meerkat_gps_ch3_options= {
			"metadata": ""
		}
		meerkat_gps_ch4_options= {
			"metadata": ""
		}
		meerkat_gps_ch5_options= {
			"metadata": ""
		}
		meerkat_gps_ch6_options= {
			"metadata": ""
		}
		meerkat_gps_ch7_options= {
			"metadata": ""
		}
		meerkat_gps_ch8_options= {
			"metadata": ""
		}
		meerkat_gps_ch9_options= {
			"metadata": ""
		}
		meerkat_gps_ch10_options= {
			"metadata": ""
		}
		meerkat_gps_ch11_options= {
			"metadata": ""
		}
		meerkat_gps_ch12_options= {
			"metadata": ""
		}
		meerkat_gps_ch13_options= {
			"metadata": ""
		}
		meerkat_gps_ch14_options= {
			"metadata": ""
		}

		# - ASKAP RACS survey options
		askap_racs_options= {
			"metadata": ""
		}

		# - MAGPIS 21cm survey options
		magpis_21cm_options= {
			"metadata": ""
		}

		# - CORNISH 5 GHz survey options
		cornish_options= {
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

		# - CUSTOM survey (placeholder for new survey data added by users)
		custom_survey_options= {
			"metadata": ""
		}

	
		# - SURVEY options
		self.survey_options= {
			"first" : first_options,
			"nvss" : nvss_options,
			"mgps" : mgps_options,
			"vgps" : vgps_options,
			"sgps" : sgps_options,
			"vlass" : vlass_options,
			"scorpio_atca_2_1" : scorpio_atca_2_1_options,
			"scorpio_askap15_b1" : scorpio_askap15_b1_options,
			"scorpio_askap36_b123" : scorpio_askap36_b123_options,
			"scorpio_askap36_b123_ch1" : scorpio_askap36_b123_ch1_options,
			"scorpio_askap36_b123_ch2" : scorpio_askap36_b123_ch2_options,
			"scorpio_askap36_b123_ch3" : scorpio_askap36_b123_ch3_options,
			"scorpio_askap36_b123_ch4" : scorpio_askap36_b123_ch4_options,
			"scorpio_askap36_b123_ch5" : scorpio_askap36_b123_ch5_options,
			"thor" : thor_options,
			"meerkat_gps" : meerkat_gps_options,
			"meerkat_gps_ch1" : meerkat_gps_ch1_options,
			"meerkat_gps_ch2" : meerkat_gps_ch2_options,
			"meerkat_gps_ch3" : meerkat_gps_ch3_options,
			"meerkat_gps_ch4" : meerkat_gps_ch4_options,
			"meerkat_gps_ch5" : meerkat_gps_ch5_options,
			"meerkat_gps_ch6" : meerkat_gps_ch6_options,
			"meerkat_gps_ch7" : meerkat_gps_ch7_options,
			"meerkat_gps_ch8" : meerkat_gps_ch8_options,
			"meerkat_gps_ch9" : meerkat_gps_ch9_options,
			"meerkat_gps_ch10" : meerkat_gps_ch10_options,
			"meerkat_gps_ch11" : meerkat_gps_ch11_options,
			"meerkat_gps_ch12" : meerkat_gps_ch12_options,
			"meerkat_gps_ch13" : meerkat_gps_ch13_options,
			"meerkat_gps_ch14" : meerkat_gps_ch14_options,
			"askap_racs" : askap_racs_options,
			"magpis_21cm" : magpis_21cm_options,
			"cornish" : cornish_options,
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
			"custom_survey": custom_survey_options,
		}

	#==============================
	#     READ CONFIG FILE
	#==============================
	def __read(self, filename):
		""" Read input INI config file"""

		try:
			self.parser.read(filename)
		except Exception as e:
			logger.error("Exception occurred when reading config file %s (err=%s)!" % (filename, str(e)))
			return -1
		
		#print(self.parser.sections())
		#self.__print_options()

		return 0

	#==============================
	#     ADD CUSTOM SURVEY
	#==============================
	def __add_custom_survey(self, metadata_path):
		""" Add custom survey to config parser (to be called after read config) """
	
		# - Check if metadata field is empty
		if metadata_path=="":
			logger.error("Empty metadata path string given!")
			return -1	

		# - Add section if not already present
		section_name= "CUSTOM_SURVEY_DATA"
		if not self.parser.has_section(section_name):
			self.parser.add_section(section_name)

		# - Add metadata field to section
		self.parser.set(section_name, 'metadata', metadata)

		return 0

	#==============================
	#     PARSE CONFIG FILE
	#==============================
	def __set_options(self):
		""" Parse input INI config file after reading it """

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
				self.cutout_factor= float(option_value)	
		
		if self.parser.has_option('CUTOUT_SEARCH', 'multi_input_img_mode'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'multi_input_img_mode')	
			if option_value:
				self.multi_input_img_mode= option_value
		
		if self.parser.has_option('CUTOUT_SEARCH', 'convert_to_jy_pixel'):
			self.convert_to_jypix_units= self.parser.getboolean('CUTOUT_SEARCH', 'convert_to_jy_pixel') 		
		
		if self.parser.has_option('CUTOUT_SEARCH', 'subtract_bkg'):
			self.subtract_bkg= self.parser.getboolean('CUTOUT_SEARCH', 'subtract_bkg') 	

		if self.parser.has_option('CUTOUT_SEARCH', 'regrid'):
			self.regrid= self.parser.getboolean('CUTOUT_SEARCH', 'regrid') 		

		if self.parser.has_option('CUTOUT_SEARCH', 'convolve'):
			self.convolve= self.parser.getboolean('CUTOUT_SEARCH', 'convolve') 
		
		if self.parser.has_option('CUTOUT_SEARCH', 'crop_mode'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'crop_mode')
			if option_value:
				self.crop_mode = option_value

		if self.parser.has_option('CUTOUT_SEARCH', 'crop_size'):
			option_value= self.parser.get('CUTOUT_SEARCH', 'crop_size')
			if option_value:
				self.crop_size= float(option_value)

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

		# - Parse VGPS DATA section options
		if self.parser.has_option('VGPS_DATA', 'metadata'):
			option_value= self.parser.get('VGPS_DATA', 'metadata')	
			if option_value:
				self.survey_options['vgps']['metadata']= option_value

		# - Parse SGPS DATA section options
		if self.parser.has_option('SGPS_DATA', 'metadata'):
			option_value= self.parser.get('SGPS_DATA', 'metadata')	
			if option_value:
				self.survey_options['sgps']['metadata']= option_value

		# - Parse VLASS DATA section options
		if self.parser.has_option('VLASS_DATA', 'metadata'):
			option_value= self.parser.get('VLASS_DATA', 'metadata')	
			if option_value:
				self.survey_options['vlass']['metadata']= option_value

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
		if self.parser.has_option('SCORPIO_ASKAP15_B1_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP15_B1_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap15_b1']['metadata']= option_value

		if self.parser.has_option('SCORPIO_ASKAP36_B123_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP36_B123_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap36_b123']['metadata']= option_value

		if self.parser.has_option('SCORPIO_ASKAP36_B123_CH1_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP36_B123_CH1_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap36_b123_ch1']['metadata']= option_value

		if self.parser.has_option('SCORPIO_ASKAP36_B123_CH2_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP36_B123_CH2_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap36_b123_ch2']['metadata']= option_value

		if self.parser.has_option('SCORPIO_ASKAP36_B123_CH3_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP36_B123_CH3_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap36_b123_ch3']['metadata']= option_value

		if self.parser.has_option('SCORPIO_ASKAP36_B123_CH4_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP36_B123_CH4_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap36_b123_ch4']['metadata']= option_value

		if self.parser.has_option('SCORPIO_ASKAP36_B123_CH5_DATA', 'metadata'):
			option_value= self.parser.get('SCORPIO_ASKAP36_B123_CH5_DATA', 'metadata')	
			if option_value:
				self.survey_options['scorpio_askap36_b123_ch5']['metadata']= option_value

		# - Parse THOR survey
		if self.parser.has_option('THOR_DATA', 'metadata'):
			option_value= self.parser.get('THOR_DATA', 'metadata')	
			if option_value:
				self.survey_options['thor']['metadata']= option_value

		# - Parse MeerKAT-GPS section options	
		if self.parser.has_option('MEERKAT_GPS_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps']['metadata']= option_value
			
		if self.parser.has_option('MEERKAT_GPS_CH1_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH1_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch1']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH2_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH2_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch2']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH3_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH3_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch3']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH4_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH4_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch4']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH5_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH5_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch5']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH6_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH6_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch6']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH7_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH7_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch7']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH8_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH8_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch8']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH9_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH9_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch9']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH10_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH10_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch10']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH11_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH11_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch11']['metadata']= option_value
	
		if self.parser.has_option('MEERKAT_GPS_CH12_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH12_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch12']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH13_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH13_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch13']['metadata']= option_value

		if self.parser.has_option('MEERKAT_GPS_CH14_DATA', 'metadata'):
			option_value= self.parser.get('MEERKAT_GPS_CH14_DATA', 'metadata')	
			if option_value:
				self.survey_options['meerkat_gps_ch14']['metadata']= option_value

		# - Parse ASKAP RACS section options	
		if self.parser.has_option('ASKAP_RACS_DATA', 'metadata'):
			option_value= self.parser.get('ASKAP_RACS_DATA', 'metadata')	
			if option_value:
				self.survey_options['askap_racs']['metadata']= option_value		

		# - Parse MAGPIS 21cm section options	
		if self.parser.has_option('MAGPIS_21cm_DATA', 'metadata'):
			option_value= self.parser.get('MAGPIS_21cm_DATA', 'metadata')	
			if option_value:
				self.survey_options['magpis_21cm']['metadata']= option_value

		# - Parse CORNISH section options	
		if self.parser.has_option('CORNISH_DATA', 'metadata'):
			option_value= self.parser.get('CORNISH_DATA', 'metadata')	
			if option_value:
				self.survey_options['cornish']['metadata']= option_value

		# - Parse custom survey section options	
		if self.parser.has_option('CUSTOM_SURVEY_DATA', 'metadata'):
			option_value= self.parser.get('CUSTOM_SURVEY_DATA', 'metadata')	
			if option_value:
				self.survey_options['custom_survey']['metadata']= option_value
	

	def parse(self, filename, add_survey=False, metadata_path=""):
		""" Read input INI config file and set options """

		# ***************************
		# **    READ CONFIG FILE
		# ***************************
		# - Read config parser
		if self.__read(filename)<0:
			logger.error("Failed to read config file %s!" % (filename))
			return -1

		# ***************************
		# **    ADD CUSTOM SURVEY
		# ***************************
		if add_survey:
			if self.__add_custom_survey(metadata_path)<0:
				logger.error("Failed to add custom survey with metadata %s!" % (metadata_path))
				return -1

		# ***************************
		# **  PARSE AND SET OPTIONS
		# ***************************
		self.__set_options()

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
		#print(valid_surveys)
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
		

