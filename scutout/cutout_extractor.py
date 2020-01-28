#!/usr/bin/env python

##################################################
###          MODULE IMPORT
##################################################
## STANDARD MODULES
import os
import sys
import string
import logging
import numpy as np
import errno
import fnmatch
import shutil

## ASTRO MODULES
from astropy.io import fits
from astropy.io import ascii 
import montage_wrapper as montage

## GRAPHICS MODULES
import matplotlib.pyplot as plt

## MODULES
from scutout import logger
from scutout.utils import Utils

logger = logging.getLogger(__name__)


###########################
##     CLASS DEFINITIONS
###########################
class CutoutFinder(object):
	""" Class to extract source cutout from object list file """

	def __init__(self,_filename,_config):
		""" Return a cutout finder object """

		self.filename= _filename
		self.config= _config
		self.table= None
		self.table_size= 0
	
	#==============================
	#     READ INPUT FILE TABLE
	#==============================
	def __read_table(self):
		""" Read file table with object coordinates """	

		# - Read table
		self.table= Utils.read_ascii_table(self.filename,row_start=0,delimiter=' ')
		if not self.table:
			logger.error("Failed to read table!")
			return -1
		
		# - Check table has entries
		self.table_size= len(self.table)
		if self.table_size<=0:
			logger.error("Given input table with coordinates for cutout is empty (hint: check table path & format)!")
			return -1

		# - Print table info
		print(self.table)
		print(self.table.colnames)

		return 0

	#==============================
	#     RUN SEARCH
	#==============================
	def run_search(self):
		""" Run search """

		#**********************
		#     READ TABLE
		#**********************
		if self.__read_table()<0:
			logger.error("Failed to read input table, search failed!")
			return -1

		#**********************
		#     SEARCH CUTOUTS
		#**********************
		for item in self.table:	
			ra= item['RA']
			dec= item['DEC']
			obj_name= item['OBJNAME']
	
			logger.info("Searching cutout for source %s (%f,%f) ..." % (obj_name,ra,dec))

			cs= CutoutHelper(self.config,ra,dec,obj_name)
			status= cs.run()
			if status<0:
				errmsg= 'Failed to extract cutout for source ' + obj_name + ', skip to next...'
				logger.warn(errmsg)
				continue

		return 0


###########################
##     CLASS DEFINITIONS
###########################
class CutoutHelper(object):
	""" Class to extract source cutout from RA/DEC position """

	def __init__(self,_config,_ra,_dec,_obj_name):
		""" Return a cutout helper object """

		self.config= _config
		self.ra= _ra
		self.dec= _dec
		self.outer_cutout= self.config.outer_cutout/60. # in degrees
		self.inner_cutout= self.config.inner_cutout/60. # in degrees
		self.sname= _obj_name
		self.topdir= self.config.workdir + '/' + self.sname
		self.tmpdir= self.topdir + '/tmpfiles'
		self.surveys= self.config.surveys
		self.img_files= {}

	def __initialize(self):
		""" Initialize search """

		# - Create source work directories
		logger.info('Creating source work directory ' + self.topdir + ' ...')
		Utils.mkdir(self.tmpdir)
		
		# - Enter tmp directory
		logger.info('Entering source work tmp directory ' + self.tmpdir + ' ...')
		os.chdir(self.tmpdir)

		return 0

	
	def __extract_raw_cutout(self,survey):
		""" Find cutout for given survey """
		
		# - Get survey data options
		survey_opts= self.config.survey_options[survey]
		data_dir= survey_opts['path']
		metadata_tbl= data_dir + '/metadata.tbl'
		print("metadata_tbl=%s" % metadata_tbl)
		
		# - Search in which survey file the source is located using Montage mCoverageCheck routine
		coverage_tbl= 'coverage_' + survey + '.tbl'
		coverage_tbl_fullpath= self.tmpdir + '/' + coverage_tbl
		logger.info('Making coverage table ' + coverage_tbl_fullpath + ' (r=' + str(self.outer_cutout) + ') ...')
		montage.mCoverageCheck(
			in_table=metadata_tbl,
			out_table=coverage_tbl_fullpath,
			mode='circle',
			ra=self.ra, dec=self.dec,
			radius=self.outer_cutout
		)

		# - Read coverage table to check if an image was found
		try:
			table= ascii.read(coverage_tbl_fullpath)
		except Exception as ex:
			logger.error('Failed to read coverage table!')
			return -1

		nimgs= len(table)
		if nimgs<=0:
			logger.info("No survey images found covering given source coordinates, go to next survey data...")
			return 0
		if nimgs>1:
			logger.warn("More than 1 image found covering source coordinates, taking the first one for the moment (FIX ME!!!)")

		imgfile= table[0]['fname']
		imgfile_fullpath= data_dir + '/' + imgfile
		imgfile_base= os.path.basename(imgfile)
		imgfile_local= self.sname + '_' + survey + '.fits'
		imgfile_local_fullpath= self.tmpdir + '/' + imgfile_local
		
		# - Copy input file to tmp dir
		shutil.copy(imgfile_fullpath,imgfile_local_fullpath)

		# - Extract the cutout using Montage
		cutout_file= self.sname + '_' + survey + '_cut.fits'
		cutout_file_fullpath= self.tmpdir + '/' + cutout_file
		raw_cutout_file= ''
		raw_cutout_file_fullpath= ''
		montage.mSubimage(
			in_image=imgfile_local_fullpath, 
			out_image=cutout_file_fullpath, 
			ra=self.ra, dec=self.dec, xsize=self.outer_cutout
		)
		self.img_files[survey]= cutout_file_fullpath
		
		# - Convert to Jy/pixel units?
		band= -1
		pos= survey.find('_b')
		if pos>0:
			band= int(survey[pos+2:])

		if self.config.convertToJyPixelUnits:
			logger.info('Convert image in Jy/pixel units ...')
			cutout_file_scaled= self.sname + '_' + survey + '_cut_jypix.fits'
			cutout_file_scaled_fullpath= self.tmpdir + '/' + cutout_file_scaled
			raw_cutout_file= cutout_file
			raw_cutout_file_fullpath= cutout_file_fullpath
			Utils.convertImgToJyPixel(cutout_file_fullpath,cutout_file_scaled_fullpath,band)
			self.img_files[survey]= cutout_file_scaled_fullpath
			
		print("cutout file")
		print(self.img_files)

		## Organize files in directories or remove some of them
		# - Input data
		input_img_dir= self.tmpdir + '/inputs'
		Utils.mkdir(input_img_dir)

		shutil.move(coverage_tbl_fullpath,os.path.join(input_img_dir,coverage_tbl))
		if self.config.keep_inputs:
			logger.info("Moving file " + imgfile_local_fullpath + ' to ' + input_img_dir + ' ...')
			shutil.move(imgfile_local_fullpath, os.path.join(input_img_dir,imgfile_local))
		else:
			try:
				logger.info("Removing tmp file " + imgfile_local_fullpath + ' ...')
				os.remove(imgfile_local_fullpath)
			except OSError:
				pass

		# -  Cutout file
		tmp_cutout_dir= self.tmpdir + '/raw_cutouts'	
		Utils.mkdir(tmp_cutout_dir)

		if raw_cutout_file:
			if self.config.keep_tmpcutouts:
				logger.info("Moving file " + raw_cutout_file + ' to ' + tmp_cutout_dir + ' ...')
				shutil.move(raw_cutout_file_fullpath,os.path.join(tmp_cutout_dir,raw_cutout_file))			
			else:
				try:
					logger.info("Removing raw cutout file " + raw_cutout_file + ' ...')
					os.remove(raw_cutout_file_fullpath)
				except OSError:
					pass

		return 0


	def run(self):
		""" Run search for single source """

		#**********************
		#     INIT
		#**********************
		if self.__initialize()<0:
			logger.error("Failed to initialize source cutout search!")
			return -1

		#*************************************
		#   EXTRACT CUTOUT FROM SURVEY DATA
		#*************************************
		for survey in self.surveys:
			logger.info('Searching cutout for source ' + self.sname + ' for survey ' + survey + ' ...')
			self.__extract_raw_cutout(survey)



		return 0

