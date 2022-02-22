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
import cv2 as cv
import enlighten

## ASTRO MODULES
from astropy.io import fits
from astropy.io import ascii 
from astropy.wcs import WCS
from astropy import units as u
from astropy.convolution import Gaussian2DKernel, convolve
import montage_wrapper as montage
import radio_beam

## GRAPHICS MODULES
#import matplotlib.pyplot as plt

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
		has_radius_col= 'RADIUS' in self.table.colnames

		manager = enlighten.get_manager()
		pbar = manager.counter(total=len(self.table), desc='Processing sources', unit='sources')

		for item in self.table:	
			ra= item['RA']
			dec= item['DEC']
			obj_name= item['OBJNAME']
			radius= -1
			if has_radius_col:
				radius= item['RADIUS']
	
			logger.info("Searching cutout for source %s (%f,%f) ..." % (obj_name,ra,dec))
			
			try:
				cs= CutoutHelper(self.config,ra,dec,obj_name,radius)
				status= cs.run()
				if status<0:
					errmsg= 'Failed to extract cutout for source ' + obj_name + ', skip to next...'
					logger.warn(errmsg)
					continue

			except Exception as e:
				#logger.error('Unknown error in source {0}. Trace: {1}'.format(obj_name, e.message))
				logger.error('Unknown error in source {0}. Trace: {1}'.format(obj_name, str(e)))
				continue

			pbar.update()

		return 0


###########################
##     CLASS DEFINITIONS
###########################
class CutoutHelper(object):
	""" Class to extract source cutout from RA/DEC position """

	def __init__(self,_config,_ra,_dec,_obj_name,_radius=-1):
		""" Return a cutout helper object """

		self.config= _config
		self.ra= _ra
		self.dec= _dec
		self.source_radius= _radius
		self.cutout_size= 2*_radius*self.config.cutout_factor
		if _radius<=0 or self.config.use_same_radius:	
			self.source_radius= self.config.source_radius
			self.cutout_size= 2*self.config.source_radius*self.config.cutout_factor
		
		self.bkg_inner_radius= self.source_radius*self.config.bkg_inner_radius_factor # in arcsec
		self.bkg_outer_radius= self.source_radius*self.config.bkg_outer_radius_factor # in arcsec

		self.source_radius/= 3600. # in degrees
		self.cutout_size/= 3600. # in degrees
		

		self.sname= _obj_name
		self.topdir= self.config.workdir + '/' + self.sname
		self.tmpdir= self.topdir + '/tmpfiles'
		self.surveys= self.config.surveys
		self.img_files= {}

	#==============================
	#     INITIALIZE
	#==============================
	def __initialize(self):
		""" Initialize search """

		# - Create source work directories
		logger.info('Creating source work directory ' + self.topdir + ' ...')
		Utils.mkdir(self.tmpdir)
		
		# - Enter tmp directory
		logger.info('Entering source work tmp directory ' + self.tmpdir + ' ...')
		os.chdir(self.tmpdir)

		return 0

	#==============================
	#     EXTRACT RAW CUTOUT
	#==============================
	def __extract_raw_cutout(self,survey):
		""" Find cutout for given survey """
		
		##  Create output directories
		# - Input data
		input_img_dir= self.tmpdir + '/inputs'
		Utils.mkdir(input_img_dir)
		
		# - Raw cutout data
		raw_cutout_dir= self.tmpdir + '/raw_cutouts'	
		Utils.mkdir(raw_cutout_dir) 

		# - Get survey data options		
		survey_opts= self.config.survey_options[survey]
		#print("Survey %s options" % survey)
		#print(survey_opts)
		metadata_tbl= survey_opts['metadata']
		#print("Survey %s metadata=%s" % (survey,metadata_tbl))
		
		# - Search in which survey file the source is located using Montage mCoverageCheck routine
		coverage_tbl= 'coverage_' + survey + '.tbl'
		coverage_tbl_fullpath= self.tmpdir + '/' + coverage_tbl
		logger.info('Making coverage table %s (r=%s arcsec) ...' % (coverage_tbl,str(self.source_radius*3600)))
		#logger.info('Making coverage table ' + coverage_tbl_fullpath + ' (r=' + str(self.source_radius) + ') ...')
		montage.mCoverageCheck(
			in_table=metadata_tbl,
			out_table=coverage_tbl_fullpath,
			mode='circle',
			ra=self.ra, dec=self.dec,
			radius=self.source_radius
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

		imgfile_fullpath= table[0]['fname']		

		if nimgs>1:
			logger.info("More than 1 image found covering source coordinates, using mode %s ..." % self.config.multi_input_img_mode)
			if self.config.multi_input_img_mode=='first':
				imgfile_fullpath= table[0]['fname']

			elif self.config.multi_input_img_mode=='best':
				try:
					res= montage.mBestImage(images_table=coverage_tbl_fullpath,ra=self.ra,dec=self.dec)
					imgfile_fullpath= res.file
				except:
					logger.warn("Caught exception from Montage mBestImage, fallback to first image ...")
					imgfile_fullpath= table[0]['fname']				

			elif self.config.multi_input_img_mode=='mosaic':
				mosaic_file= 'mosaic_' + survey + '.fits'
				mosaic_file_fullpath= os.path.join(input_img_dir,mosaic_file)
				status= Utils.makeMosaic(coverage_tbl_fullpath,output=mosaic_file_fullpath)	
				if status==0:
					imgfile_fullpath= mosaic_file_fullpath
				else:
					logger.warn("Failed to compute mosaic from images listed in file %s, taking best one out of them ..." % (coverage_tbl))
					try:
						res= montage.mBestImage(images_table=coverage_tbl_fullpath,ra=self.ra,dec=self.dec)
						imgfile_fullpath= res.file
					except:
						logger.warn("Caught exception from Montage mBestImage, fallback to first image ...")
						imgfile_fullpath= table[0]['fname']			
			else:
				logger.warn("Invalid/unknown multi input image option (%s), taking the first one..." % (self.config.multi_input_img_mode))
				imgfile_fullpath= table[0]['fname']
		
			
		#imgfile= table[0]['fname']
		#imgfile_fullpath= imgfile
		#imgfile_base= os.path.basename(imgfile_fullpath)
		imgfile_local= self.sname + '_' + survey + '.fits'
		imgfile_local_fullpath= self.tmpdir + '/' + imgfile_local
		
		# - Copy input file to tmp dir
		#shutil.copy(imgfile_fullpath,imgfile_local_fullpath)

		# - Extract the cutout using Montage
		logger.info("Extracting raw cutout around (%s,%s) with size %s (arcsec) ..." % (str(self.ra),str(self.dec),str(self.cutout_size*3600)))
		cutout_file= self.sname + '_' + survey + '_cut.fits'
		cutout_file_fullpath= self.tmpdir + '/' + cutout_file
		raw_cutout_file= ''
		raw_cutout_file_fullpath= ''
		montage.mSubimage(
			#in_image=imgfile_local_fullpath, 
			in_image=imgfile_fullpath, 
			out_image=cutout_file_fullpath, 
			ra=self.ra, dec=self.dec, xsize=self.cutout_size
		)
		self.img_files[survey]= cutout_file_fullpath
		
		# - Fix image axis or scale in case BZERO!=0 or BSCALE!=0
		logger.info("Fixing possible degenerate axis and non-null BSCALE factor in image %s ..." % (cutout_file))
		status= Utils.fixImgAxisAndUnits(cutout_file_fullpath,cutout_file_fullpath)
		if status<0:
			logger.error("Failed to adjust axis/scale of image " + cutout_file_fullpath + "!")
			return -1

		# - Convert to Jy/pixel units?
		#band= -1
		#pos= survey.find('_b')
		#if pos>0:
		#	band= int(survey[pos+2:])

		if self.config.convert_to_jypix_units:
			cutout_file_scaled= self.sname + '_' + survey + '_cut_jy.fits'
			cutout_file_scaled_fullpath= self.tmpdir + '/' + cutout_file_scaled
			raw_cutout_file= cutout_file
			raw_cutout_file_fullpath= cutout_file_fullpath

			logger.info('Converting image %s in Jy/pixel units ...' % (raw_cutout_file))
			Utils.convertImgToJyPixel(cutout_file_fullpath,cutout_file_scaled_fullpath,survey,table[0]['bunit'])
			self.img_files[survey]= cutout_file_scaled_fullpath
			
		
		## Organize files in directories or remove some of them
		# - Move coverage table to input subdir
		shutil.move(coverage_tbl_fullpath,os.path.join(input_img_dir,coverage_tbl))
		
		# -  Move raw cutout file to cutout subdir
		if raw_cutout_file:
			logger.debug("Moving file " + raw_cutout_file + ' to ' + raw_cutout_dir + ' ...')
			shutil.move(raw_cutout_file_fullpath,os.path.join(raw_cutout_dir,raw_cutout_file))

		# - Move final products in subdir
		shutil.move(self.img_files[survey],os.path.join(raw_cutout_dir,os.path.basename(self.img_files[survey])))
		self.img_files[survey]= os.path.join(raw_cutout_dir,os.path.basename(self.img_files[survey]))		

		#print("Cutout images to be processed after raw cutout step")
		#print(self.img_files)

		return 0

	#==============================
	#     SUBTRACT BKG
	#==============================
	def __subtract_bkg(self):
		""" Subtract bkg from raw cutout """

		# - Create output directory
		bkgsub_cutout_dir= self.tmpdir + '/bkgsub_cutouts'	
		Utils.mkdir(bkgsub_cutout_dir)

		#	- Loop over cutouts and compute bkg
		for survey, filename in self.img_files.items(): 
			filename_base= Utils.getBaseFileNoExt(filename)
			bkgsub_cutout= filename_base + '_bkgsub.fits'
			bkgsub_cutout_fullpath= self.tmpdir + '/' + bkgsub_cutout
			self.img_files[survey]= bkgsub_cutout_fullpath
	
			# - Compute bkg in annulus around source
			logger.info("Computing bkg for image %s (R1=%s, R2=%s) ..." % (filename_base,str(self.bkg_inner_radius),str(self.bkg_outer_radius)))			
			bkg= Utils.estimateBkgFromAnnulus(
				filename=filename,
				ra=self.ra,dec=self.dec,
				R1=self.bkg_inner_radius,R2=self.bkg_outer_radius,
				method=self.config.bkg_estimator,
				max_nan_thr=self.config.bkg_max_nan_thr
			)

			# - Read fits image
			data, header= Utils.read_fits(filename)
	
			# - Subtract bkg?
			good_bkg= (bkg>0 and np.isfinite(bkg))
			if good_bkg:
				logger.info("Subtracting bkg=%s from image %s ..." % (str(bkg),filename_base))			
				data_nobkg= data - bkg
			else:
				logger.warn("Computed bkg is not valid (negative/nan/inf), won't subtract bkg from image %s ..." % (filename_base))
				data_nobkg= data			

			# - Write fits
			logger.debug("Writing bkg-subtracted image to file %s ..." % (bkgsub_cutout))
			Utils.write_fits(data_nobkg,bkgsub_cutout_fullpath,header)

		# - Move final products in subdir
		for survey, path in self.img_files.items(): 
			shutil.move(self.img_files[survey],os.path.join(bkgsub_cutout_dir,os.path.basename(self.img_files[survey])))
			self.img_files[survey]= os.path.join(bkgsub_cutout_dir,os.path.basename(self.img_files[survey]))


		return 0

	#==============================
	#     REGRID CUTOUTS
	#==============================
	def __regrid_cutouts(self):
		""" Regrid cutouts to the same projection and pixel """

		##  Create output directories
		# - Raw cutout dir (should already exist if previous step was called)
		raw_cutout_dir= self.tmpdir + '/raw_cutouts'	
		Utils.mkdir(raw_cutout_dir)

		# - Regrid cutout dir
		reproj_cutout_dir= self.tmpdir + '/reproj_cutouts'	
		Utils.mkdir(reproj_cutout_dir)

		# - Get list of raw cutout images to be re-projected
		raw_cutouts= []
		reproj_cutouts= []
		dx_orig= []
		dy_orig= []

		for survey, path in self.img_files.items(): 
			reproj_cutout= Utils.getBaseFileNoExt(path) + '_reproj.fits'
			reproj_cutout_fullpath= self.tmpdir + '/' + reproj_cutout
			raw_cutouts.append(path)
			reproj_cutouts.append(reproj_cutout_fullpath)
			self.img_files[survey]= reproj_cutout_fullpath

		#print(raw_cutouts)
		#print(reproj_cutouts)

		# - Reproject cutouts using py Montage reproject high-level API
		try:
			montage.reproject(
				in_images=raw_cutouts, 
				out_images=reproj_cutouts, 
				header=None, 
				bitpix=None, 
				north_aligned=True,
				common=True	
			)
		except Exception as e:
			logger.error("Failed to reproject cutouts (err=%s)!" % str(e))
			return -1
			

		# - Scale image data to conserve flux, e.g. multiply data by (pix1/pix1_ori)*(pix2/pix2_ori)
		# - Copy back beam information (montage does not include in the re-projected image file)
		# - Overwrite previous image
		
		for index in range(len(raw_cutouts)):
			data, header= Utils.read_fits(raw_cutouts[index])
			dx= abs(header['CDELT1'])
			dy= abs(header['CDELT2'])
		
			data_reproj, header_reproj= Utils.read_fits(reproj_cutouts[index])
			dx_reproj= abs(header_reproj['CDELT1'])
			dy_reproj= abs(header_reproj['CDELT2'])

			flux_scale= (dx_reproj/dx)*(dy_reproj/dy)
			data_reproj_scaled= flux_scale*data_reproj
	
			logger.info("Scaling re-projected image %s to conserve flux (conv factor=%s) ..." % (raw_cutouts[index],str(flux_scale)))

			if Utils.hasBeamInfo(header) and not Utils.hasBeamInfo(header_reproj):
				header_reproj['BMAJ']= header['BMAJ']
				header_reproj['BMIN']= header['BMIN']
				header_reproj['BPA']= header['BPA'] if 'BPA' in header else 0.

			Utils.write_fits(data_reproj_scaled,reproj_cutouts[index],header_reproj)
			

		# - Move final products to subdir
		for survey, path in self.img_files.items(): 
			shutil.move(self.img_files[survey],os.path.join(reproj_cutout_dir,os.path.basename(self.img_files[survey])))
			self.img_files[survey]= os.path.join(reproj_cutout_dir,os.path.basename(self.img_files[survey]))
		
		#print("Cutout images to be processed after cutout reproj step")
		#print(self.img_files)

		return 0


	#=========================================
	#     CONVOLVE CUTOUTS TO SAME RESOLUTION
	#=========================================
	def __convolve_to_same_resolution(self):
		""" Convolve cutouts to same resolution """
		
		## Create output directory
		conv_cutout_dir= self.tmpdir + '/conv_cutouts'	
		Utils.mkdir(conv_cutout_dir)
		
		# - Get list of raw cutout images to be convolved
		raw_cutouts= []
		conv_cutouts= []
		beam_list= []
		pixsize_x= []
		pixsize_y= []
		data_list= []
		header_list= []

		for survey, path in self.img_files.items(): 
			raw_cutouts.append(path)
			conv_cutout= Utils.getBaseFileNoExt(path) + '_conv.fits'
			conv_cutout_fullpath= self.tmpdir + '/' + conv_cutout
			conv_cutouts.append(conv_cutout_fullpath)
			self.img_files[survey]= conv_cutout_fullpath
			
			# - Get image beam
			data, header= Utils.read_fits(path)
			wcs = WCS(header)
			data_list.append(data)
			header_list.append(header)

			hasBeamInfo= Utils.hasBeamInfo(header)
			xc= header['CRPIX1']
			yc= header['CRPIX2']	
			ra, dec = wcs.all_pix2world(xc,yc,0,ra_dec_order=True)
			dx= abs(header['CDELT1']) # in deg
			dy= abs(header['CDELT2']) # in deg
			pixsize_x.append(dx)
			pixsize_y.append(dy)

			if hasBeamInfo:
				bmaj= header['BMAJ'] # in deg
				bmin= header['BMIN'] # in deg
				pa= header['BPA'] if 'BPA' in header else 0 # in deg
				beam= radio_beam.Beam(bmaj*u.deg,bmin*u.deg,pa*u.deg)
			else:
				logger.warn("No BMAJ/BMIN keyword present in file " + path + ", trying to retrieve from survey name...")
				beamArea= Utils.getSurveyBeamArea(survey,ra,dec)
				bmaj= np.sqrt(beamArea*4.*np.log(2)/np.pi)
				if beamArea>0:
					beam= radio_beam.Beam(bmaj*u.deg,bmaj*u.deg)
				else:
					logger.error("No BMAJ keyword present in file " + path + ", cannot compute conversion factor!")
					return -1

			beam_list.append(beam)
		
		# - Compute common beam
		beams= radio_beam.Beams(beams=beam_list)
		common_beam= radio_beam.commonbeam.common_manybeams_mve(beams)
		common_beam_bmaj= common_beam.major.to(u.arcsec).value
		common_beam_bmin= common_beam.minor.to(u.arcsec).value
		common_beam_pa= common_beam.pa.to(u.deg).value
		

		# - Loop over image, find conv beam to be used to reach common beam and convolve image with this
		logger.info("Convolving images to common beam size (bmaj,bmin,pa)=(%s,%s,%s) ..." % (str(common_beam_bmaj),str(common_beam_bmin),str(common_beam_pa)))
		
		for index in range(len(raw_cutouts)):

			# - Find convolving beam 
			logger.debug("Finding convolving beam ...")
			try:
				bmaj, bmin, pa= radio_beam.utils.deconvolve(common_beam,beam_list[index])
			except Exception as e:	
				logger.error("Failed to deconvolve beam no. %d (err=%s)" % (index,str(e)))
				continue

			logger.debug("type(bmaj)")
			logger.debug(type(bmaj))
			logger.debug("type(bmin)")
			logger.debug(type(bmin))
			logger.debug("type(pa)")
			logger.debug(type(pa))

			try:
				#bmaj_deg= bmaj.to(u.deg).value
				#bmaj_arcsec= bmaj.to(u.arcsec).value
				bmaj_deg= bmaj.to_value(u.deg)
				bmaj_arcsec= bmaj.to_value(u.arcsec)
			except Exception as e:
				logger.warn("Failed to convert bmaj to no unit values (possibly not astropy Units type) (err=%s), assuming it is a scalar ..." % str(e))
				bmaj_deg= bmaj
				bmaj_arcsec= bmaj*3600
				
			try:
				#bmin_deg= bmin.to(u.deg).value
				#bmin_arcsec= bmin.to(u.arcsec).value
				bmin_deg= bmin.to_value(u.deg)
				bmin_arcsec= bmin.to_value(u.arcsec)
			except Exception as e:
				logger.warn("Failed to convert bmin to no unit values (possibly not astropy Units type) (err=%s), assuming it is a scalar ..." % str(e))
				bmin_deg= bmin
				bmin_arcsec= bmin*3600

			try:
				#pa_deg= pa.to(u.deg).value
				pa_deg= pa.to_value(u.deg)
			except Exception as e:
				logger.debug("Failed to convert pa to no unit values (possibly not astropy Units type) (err=%s), assuming it is a scalar ..." % str(e))
				pa_deg= pa
				

			logger.debug("Creating radio beam object ...")
			logger.debug("type(bmaj_deg)")
			logger.debug(type(bmaj_deg))

			try:
				conv_beam= radio_beam.Beam(bmaj_deg*u.deg,bmin_deg*u.deg,pa_deg*u.deg)
			except Exception as e:	
				logger.error("Failed to create conv beam from (bmaj,bmin,pa)=(%f,%f,%f) (err=%s)" % (bmaj_deg,bmin_deg,pa_deg,str(e)))
				continue			

			ny= data_list[index].shape[0]
			nx= data_list[index].shape[1]
			
			
			# - Create convolution kernel
			logger.info("Convolving image %s (size=%d,%d) with beam (bmaj,bmin,pa)=(%f,%f,%f) ..." % (raw_cutouts[index],nx,ny,bmaj_arcsec,bmin_arcsec,pa_deg))
			dx= pixsize_x[index]
			dy= pixsize_y[index]
			pixsize= max(dx,dy)
			conv_kernel= conv_beam.as_kernel(pixsize*u.deg)
			conv_kernel.normalize()
			kernel=conv_kernel.array

			# - Convolve image and write fits
			data_list[index][np.isnan(data_list[index])]=0.0
			data_conv=cv.filter2D(np.float64(data_list[index]),-1,kernel,borderType=cv.BORDER_CONSTANT)
			logger.info("Kernel size: %d x %d" % (kernel.shape[0],kernel.shape[1]))
			Utils.write_fits(data_conv,conv_cutouts[index],header_list[index])

		
		# - Move final products in subdir
		for survey, path in self.img_files.items(): 
			shutil.move(self.img_files[survey],os.path.join(conv_cutout_dir,os.path.basename(self.img_files[survey])))
			self.img_files[survey]= os.path.join(conv_cutout_dir,os.path.basename(self.img_files[survey]))

		#print("Cutout images to be processed after cutout convolve step")
		#print(self.img_files)


		return 0


	#==============================
	#     CROP CUTOUTS
	#==============================
	def __crop(self):
		""" Crop cutouts to the desired number of pixels """

		## Organize files in directories 
		crop_cutout_dir= self.tmpdir + '/cropped_cutouts'	
		Utils.mkdir(crop_cutout_dir)
		
		# - Computing source size. Crop method will internally check is cutout size is cutting part of the source
		source_size= self.source_radius # in deg

		for survey, filename in self.img_files.items(): 
			# - Set output filename
			cropped_cutout= Utils.getBaseFileNoExt(filename) + '_cropped.fits'
			cropped_cutout_fullpath= self.tmpdir + '/' + cropped_cutout
			#cropped_cutouts.append(cropped_cutout_fullpath)
			self.img_files[survey]= cropped_cutout_fullpath

			# - Crop image
			logger.info("Cropping cutout file " + filename + " to desired size ...")
			status= Utils.cropImage(
				filename=filename,
				ra=self.ra,dec=self.dec,
				crop_mode = self.config.crop_mode,
				crop_size = self.config.crop_size,
				outfile=cropped_cutout_fullpath,
				source_size=source_size,
				nanfill=True,
				nanfill_mode='imgmin',
				nanfill_val=0
			)

			# - Move conv cutout in subdir
			#filename_base= Utils.getBaseFile(filename)	
			#logger.info("Moving file " + filename_base + ' to ' + conv_cutout_dir + ' ...')
			#shutil.move(filename,os.path.join(conv_cutout_dir,filename_base))
	
			# - Exit if crop failed
			if status<0:
				logger.error("Failed to crop cutout file " + filename + " (hints: check is source is larger than crop size)")
				return -1

			# - Copy final product in subdir
			logger.debug("Moving file " + os.path.basename(self.img_files[survey]) + ' to ' + crop_cutout_dir + ' ...')
			shutil.move(self.img_files[survey],os.path.join(crop_cutout_dir,os.path.basename(self.img_files[survey])))
			self.img_files[survey]= os.path.join(crop_cutout_dir,os.path.basename(self.img_files[survey]))



		return 0
		
	#==============================
	#     RUN CUTOUT EXTRACTION
	#==============================
	def run(self):
		""" Run search for single source """
		
		#**********************
		#        INIT
		#**********************
		if self.__initialize()<0:
			logger.error("Failed to initialize source cutout search!")
			return -1
		
		#*************************************
		#   EXTRACT CUTOUT FROM SURVEY DATA
		#*************************************
		for survey in self.surveys:
			logger.info('Searching cutout for source ' + self.sname + ' for survey ' + survey + ' ...')
			status= self.__extract_raw_cutout(survey)
			if status<0:
				logger.error('Raw cutout extraction for source ' + self.sname + ' for survey ' + survey + ' failed!')
				return -1

		#*************************************
		#   SUBTRACT BACKGROUND
		#*************************************
		if self.config.subtract_bkg:
			logger.info('Subtracting bkg from raw cutouts ...')
			status= self.__subtract_bkg()
			if status<0:
				logger.error('Failed to subtract bkg from raw cutouts for source ' + self.sname + '!')
				return -1

		#*************************************
		#        REGRID CUTOUTS
		#*************************************
		if self.config.regrid:
			logger.info('Regridding raw cutouts ...')
			status= self.__regrid_cutouts()
			if status<0:
				logger.error('Failed to regrid raw cutouts for source ' + self.sname + '!')
				return -1

		#*************************************
		#       CONVOLVE CUTOUTS
		#*************************************
		if self.config.convolve:
			logger.info('Convolving raw cutouts to the same resolution ...')
			status= self.__convolve_to_same_resolution()
			if status<0:
				logger.error('Failed to convolve raw cutouts for source ' + self.sname + '!')
				return -1

		#*************************************
		#       CROP CUTOUTS
		#*************************************
		if self.config.crop_mode!='none':
			logger.info('Cropping cutouts in ' + self.config.crop_mode +  ' mode')
			status= self.__crop()
			if status<0:
				logger.error('Failed to crop cutouts for source ' + self.sname + '!')
				return -1
	
		#*************************************
		#     COPY FINAL FILES IN MAIN DIR
		#*************************************
		# - Copy final files in main directory
		logger.debug("Copying final image cutouts in main directory ...")
		for survey, filename in self.img_files.items():
			filename_base= Utils.getBaseFile(filename)
			filename_final= self.sname + '_' + survey + '.fits'
			filename_final_fullpath= self.topdir + '/' + filename_final
			shutil.copy(filename,filename_final_fullpath)

		# - Remove tmp file directory?
		if not self.config.keep_tmpfiles:
			logger.debug("Removing tmp file dir " + self.tmpdir + " ...")
			shutil.rmtree(self.tmpdir, ignore_errors=True)

		return 0

