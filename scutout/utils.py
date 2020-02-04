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
import fnmatch
import shutil
import errno

## ASTRO MODULES
from astropy.io import fits
from astropy.io import ascii 
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
from astropy.stats import sigma_clipped_stats
from astropy import units as u
from astropy.coordinates import SkyCoord
from regions import CircleAnnulusSkyRegion, CircleAnnulusPixelRegion
import montage_wrapper as montage

## GRAPHICS MODULES
import matplotlib.pyplot as plt


logger = logging.getLogger(__name__)


###########################
##     CLASS DEFINITIONS
###########################
class Utils(object):
	""" Class collecting utility methods

			Attributes:
				None
	"""

	def __init__(self):
		""" Return a Utils object """
		
	@classmethod
	def getBaseFile(cls,filename):
		""" Get basefilename without extension """
		filename_base= os.path.basename(filename)
		return filename_base

	@classmethod
	def getBaseFileNoExt(cls,filename):
		""" Get basefilename without extension """
		filename_base= os.path.basename(filename)
		filename_base_noext= os.path.splitext(filename_base)[0]
		return filename_base_noext

	@classmethod
	def mkdir(cls,path):
		""" Create a directory """
		try:
			os.makedirs(path)
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				logger.error('Failed to create directory ' + path + '!')
				return -1
		return 0

	@classmethod
	def has_patterns_in_string(cls,s,patterns):
		""" Return true if patterns are found in string """
		if not patterns:		
			return False

		found= False
		for pattern in patterns:
			found= pattern in s
			if found:
				break

		return found

	@classmethod
	def find_file(cls,rootPath,searched_file):
		""" Find file recursively from root directory and return full path """
		matches = []
		for root, dirnames, filenames in os.walk(rootPath):
			for filename in fnmatch.filter(filenames, searched_file):
				matches.append(os.path.join(root, filename))

		return matches

	@classmethod
	def find_and_copy_file(cls,rootPath,searched_file,destDir):
		""" Find file recursively from root dir and move to destination dir """

		matched_files= Utils.find_file(rootPath,searched_file)
		if not matched_files:
			return -1

		for filename in matched_files:
			shutil.copy(filename, destDir)

		return 0

	@classmethod
	def write_ascii(cls,data,filename,header=''):
		""" Write data to ascii file """

		# - Skip if data is empty
		if data.size<=0:
			#cls._logger.warn("Empty data given, no file will be written!")
			logger.warn("Empty data given, no file will be written!")
			return

		# - Open file and write header
		fout = open(filename, 'wt')
		if header:
			fout.write(header)
			fout.write('\n')	
			fout.flush()	
		
		# - Write data to file
		nrows= data.shape[0]
		ncols= data.shape[1]
		for i in range(nrows):
			fields= '  '.join(map(str, data[i,:]))
			fout.write(fields)
			fout.write('\n')	
			fout.flush()	

		fout.close();

	@classmethod
	def read_ascii(cls,filename,skip_patterns=[]):
		""" Read an ascii file line by line """
	
		try:
			f = open(filename, 'r')
		except IOError:
			errmsg= 'Could not read file: ' + filename
			#cls._logger.error(errmsg)
			logger.error(errmsg)
			raise IOError(errmsg)

		fields= []
		for line in f:
			line = line.strip()
			line_fields = line.split()
			if not line_fields:
				continue

			# Skip pattern
			skipline= cls.has_patterns_in_string(line_fields[0],skip_patterns)
			if skipline:
				continue 		

			fields.append(line_fields)

		f.close()	

		return fields

	@classmethod
	def read_ascii_table(cls,filename,row_start=0,delimiter='|',format=''):
		""" Read an ascii table file line by line """

		try:
			if format:
				table= ascii.read(filename,format=format)
			else:
				table= ascii.read(filename,data_start=row_start, delimiter=delimiter)
		except Exception as ex:
			logger.error("Failed to read table!")
			return None			

		return table

	@classmethod
	def write_fits(cls,data,filename,header=None):
		""" Read data to FITS image """

		if header:
			hdu= fits.PrimaryHDU(data,header)
		else:
			hdu= fits.PrimaryHDU(data)

		hdul= fits.HDUList([hdu])
		hdul.writeto(filename,overwrite=True)

	@classmethod
	def read_fits(cls,filename):
		""" Read FITS image and return data """

		# - Open file
		try:
			hdu= fits.open(filename,memmap=False)
		except Exception as ex:
			errmsg= 'Cannot read image file: ' + filename
			#cls._logger.error(errmsg)
			logger.error(errmsg)
			raise IOError(errmsg)

		# - Read data
		data= hdu[0].data
		data_size= np.shape(data)
		nchan= len(data.shape)
		if nchan==4:
			output_data= data[0,0,:,:]
		elif nchan==2:
			output_data= data	
		else:
			errmsg= 'Invalid/unsupported number of channels found in file ' + filename + ' (nchan=' + str(nchan) + ')!'
			#cls._logger.error(errmsg)
			logger.error(errmsg)
			hdu.close()
			raise IOError(errmsg)

		# - Read metadata
		header= hdu[0].header

		# - Close file
		hdu.close()

		return output_data, header

	
	@classmethod
	def crop_img(cls,data,x0,y0,dx,dy):
		""" Extract sub image of size (dx,dy) around pixel (x0,y0) """

		#- Extract crop data
		xmin= int(x0-dx/2)
		xmax= int(x0+dx/2)
		ymin= int(y0-dy/2)
		ymax= int(y0+dy/2)		
		crop_data= data[ymin:ymax+1,xmin:xmax+1]
	
		#- Replace NAN with zeros and inf with large numbers
		np.nan_to_num(crop_data,False)

		return crop_data

	@classmethod
	def getBeamArea(cls,bmaj,bmin):
		""" Compute beam area """
		beamArea= np.pi * bmaj * bmin/(4.*np.log(2))
		return beamArea

	@classmethod
	def getNVSSSurveyBeamArea(cls):
		""" Returns NVSS survey beam area """ 
		bmaj= 45. # arcsec
		bmin= 45. # arcsec
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getWiseSurveyBeamArea(cls,band):
		""" Returns Wise survey beam area """ 
		if band=='wise_3_4':
			bmaj= 8.5 # arcsec
			bmin= 8.5 # arcsec
		elif band=='wise_4_6':
			bmaj= 8.5 # arcsec
			bmin= 8.5 # arcsec
		elif band=='wise_12':
			bmaj= 8.5 # arcsec
			bmin= 8.5 # arcsec
		elif band=='wise_22':
			bmaj= 17 # arcsec
			bmin= 17 # arcsec
		else:
			logger.error("Invalid/unknown band argument given (" + band + ")!")
			return 0
		
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getIRACSurveyBeamArea(cls,band):
		""" Returns IRAC survey beam area """ 
		if band=='irac_3_6':
			bmaj= 1.7 # arcsec
			bmin= 1.7 # arcsec
		elif band=='irac_4_5':
			bmaj= 1.7 # arcsec
			bmin= 1.7 # arcsec
		elif band=='irac_5_8':
			bmaj= 1.7 # arcsec
			bmin= 1.7 # arcsec
		elif band=='irac_8':
			bmaj= 1.9 # arcsec
			bmin= 1.9 # arcsec
		else:
			logger.error("Invalid/unknown band argument given (" + band + ")!")
			return 0
		
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getMIPSSurveyBeamArea(cls):
		""" Returns MIPS survey beam area """ 
		
		bmaj= 6 # arcsec
		bmin= 6 # arcsec
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getHiGalSurveyBeamArea(cls,band):
		""" Returns HiGal survey beam area """ 
		if band=='higal_70':
			bmaj= 8.512 # arcsec
			bmin= 8.512 # arcsec
		elif band=='higal_160':
			bmaj= 12.103 # arcsec
			bmin= 12.103 # arcsec
		elif band=='higal_250':
			bmaj= 18 # arcsec
			bmin= 18 # arcsec
		elif band=='higal_350':
			bmaj= 24 # arcsec
			bmin= 24 # arcsec
		elif band=='higal_500':
			bmaj= 34.5 # arcsec
			bmin= 34.5 # arcsec
		else:
			logger.error("Invalid/unknown band argument given (" + band + ")!")
			return 0
		
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getATLASGALSurveyBeamArea(cls):
		""" Returns ATLASGAL survey beam area """ 

		bmaj= 18.6 # arcsec (from http://www.apex-telescope.org/bolometer/laboca/technical/)
		bmin= 18.6 # arcsec (from http://www.apex-telescope.org/bolometer/laboca/technical/)
		#bmaj= 19.2 # arcsec (from ATLASGAL papers)
		#bmin= 19.2 # arcsec (from ATLASGAL papers)
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getATLASGALPlanckSurveyBeamArea(cls):
		""" Returns ATLASGAL+Planck survey beam area """ 

		bmaj= 21 # arcsec (from http://atlasgal.mpifr-bonn.mpg.de/cgi-bin/ATLASGAL_DATASETS.cgi)
		bmin= 21 # arcsec 
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getMSXSurveyBeamArea(cls):
		""" Returns MSX survey beam area """ 

		bmaj= 20 # arcsec
		bmin= 20 # arcsec
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getFIRSTSurveyBeamArea(cls,ra,dec):
		""" Returns FIRST survey beam area """ 
		
		if not ra or not dec:
			bmaj= 5.4
			bmin= 5.4

		if dec>4.55583333:
			bmaj= 5.4
			bmin= 5.4
		else:
			if dec<-2.50694444 and (ra<45 or ra>315):
				bmaj= 6.8
				bmin= 5.4
			else:
				bmaj= 6.4
				bmin= 5.4

		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getMGPSSurveyBeamArea(cls,dec):
		""" Returns MGPS survey beam area """ 
		
		if not dec or dec==0:
			bmaj= 43
		else:
			bmaj= 43./np.sin(np.deg2rad(dec)) # arcsec
		bmin= 43. # arcsec

		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getScorpioATCASurveyBeamArea(cls,band):
		""" Returns Scorpio ATCA survey beam area """ 
		
		if band=='scorpio_atca_2_1':
			bmaj= 9.8 # arcsec
			bmin= 5.8 # arcsec
		#elif band=='scorpio_atca_5_0':
		#	bmaj= 12.103 # arcsec
		#	bmin= 12.103 # arcsec
		
		else:
			logger.error("Invalid/unknown band argument given (" + band + ")!")
			return 0
		
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getScorpioASKAPB1SurveyBeamArea(cls):
		""" Returns Scorpio ASKAP 15 B1 survey beam area """ 
		bmaj= 24 # arcsec
		bmin= 21 # arcsec
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getScorpioASKAP36B123SurveyBeamArea(cls):
		""" Returns Scorpio ASKAP 36 B123 survey beam area """ 
		bmaj= 9.403 # arcsec
		bmin= 7.713 # arcsec
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getTHORSurveyBeamArea(cls):
		""" Returns THOR survey beam area """ 
		#Beam varying from 18.1 x 11.1 to 12.0 x 11.6
		bmaj= 12 # arcsec
		bmin= 12 # arcsec
		bmaj_deg= bmaj/3600.
		bmin_deg= bmin/3600.
		beamArea= Utils.getBeamArea(bmaj_deg,bmin_deg)
		return beamArea

	@classmethod
	def getSurveyBeamArea(cls,survey,ra=None,dec=None):
		""" Return beam area of given survey """
		
		beamArea= 0
		if survey=='nvss':
			beamArea= Utils.getNVSSSurveyBeamArea()
		elif survey=='first':
			beamArea= Utils.getFIRSTSurveyBeamArea(ra,dec)
		elif survey=='mgps':
			beamArea= Utils.getMGPSSurveyBeamArea(dec)
		elif survey=='wise_3_4':
			beamArea= Utils.getWiseSurveyBeamArea(survey)
		elif survey=='wise_5_6':
			beamArea= Utils.getWiseSurveyBeamArea(survey)
		elif survey=='wise_12':
			beamArea= Utils.getWiseSurveyBeamArea(survey)
		elif survey=='wise_22':
			beamArea= Utils.getWiseSurveyBeamArea(survey)
		elif survey=='irac_3_6':
			beamArea= Utils.getIRACSurveyBeamArea(survey)
		elif survey=='irac_4_5':
			beamArea= Utils.getIRACSurveyBeamArea(survey)
		elif survey=='irac_5_8':
			beamArea= Utils.getIRACSurveyBeamArea(survey)
		elif survey=='irac_8':
			beamArea= Utils.getIRACSurveyBeamArea(survey)
		elif survey=='mips_24':
			beamArea= Utils.getMIPSSurveyBeamArea()		
		elif survey=='higal_70':
			beamArea= Utils.getHiGalSurveyBeamArea(survey)
		elif survey=='higal_160':
			beamArea= Utils.getHiGalSurveyBeamArea(survey)
		elif survey=='higal_250':
			beamArea= Utils.getHiGalSurveyBeamArea(survey)
		elif survey=='higal_350':
			beamArea= Utils.getHiGalSurveyBeamArea(survey)
		elif survey=='higal_500':
			beamArea= Utils.getHiGalSurveyBeamArea(survey)
		elif survey=='atlasgal':
			beamArea= Utils.getATLASGALSurveyBeamArea()
		elif survey=='atlasgal_planck':
			beamArea= Utils.getATLASGALPlanckSurveyBeamArea()
		elif survey=='msx_8_3':
			beamArea= Utils.getMSXSurveyBeamArea()
		elif survey=='msx_12_1':
			beamArea= Utils.getMSXSurveyBeamArea()
		elif survey=='msx_14_7':
			beamArea= Utils.getMSXSurveyBeamArea()
		elif survey=='msx_21_3':
			beamArea= Utils.getMSXSurveyBeamArea()
		elif survey=='scorpio_atca_2_1':
			beamArea= Utils.getScorpioATCASurveyBeamArea(survey)
		elif survey=='scorpio_askap15_b1':
			beamArea= Utils.getScorpioASKAP15B1SurveyBeamArea()
		elif survey=='scorpio_askap36_b123':
			beamArea= Utils.getScorpioASKAP36B123SurveyBeamArea()
		elif survey=='thor':
			beamArea= Utils.getTHORSurveyBeamArea()
		else:
			logger.error("Unknown survey (" + survey + "), returning area=0!")
			beamArea= 0

		return beamArea

	@classmethod
	def getJyBeamToPixel(cls,beamArea,dx,dy):
		""" Compute conversion factor from Jy/beam to Jy/pixel """

		pixArea= np.abs(dx*dy)
		toJyPerPix = pixArea/beamArea

		return toJyPerPix

	@classmethod
	def getJyBeamToPixel2(cls,bmaj,bmin,dx,dy):
		""" Compute conversion factor from Jy/beam to Jy/pixel """
		beamArea= Utils.getBeamArea(bmaj,bmin)
		return Utils.getJyBeamToPixel(beamArea,dx,dy)

	@classmethod
	def hasBeamInfo(cls,header):
		""" Check if header has beam information """
		hasBmaj= ('BMAJ' in header)
		hasBmin= ('BMIN' in header)
		hasBeamInfo= (hasBmaj and hasBmin)
		if not hasBeamInfo:
			return False
		
		hasBeamVal= (header['BMAJ'] and header['BMIN'])
		if not hasBeamVal:
			return False

		return True


	@classmethod
	def fixImgAxisAndUnits(cls,filename,outfile):
		""" Fix image axis issues and convert units """

		# - Open input file
		try:
			hdu= fits.open(filename,memmap=False)
		except Exception as ex:
			logger.error('Cannot read image file: ' + filename)
			return -1

		# - Read data & header
		header= hdu[0].header
		data= hdu[0].data
		data_size= np.shape(data)
		nchan= len(data.shape)
		if nchan==4:
			output_data= data[0,0,:,:]
			output_header= header
			output_header['NAXIS']= 2

		elif nchan==2:
			output_data= data	
			output_header= header
			
		else:
			errmsg= 'Invalid/unsupported number of channels found in file ' + filename + ' (nchan=' + str(nchan) + ')!'
			hdu.close()
			logger.error(errmsg)
			return -1

		logger.info("Deleting NAXIS3/NAXIS4 from header...")
		if 'NAXIS3' in output_header:
			del output_header['NAXIS3']
		if 'NAXIS4' in output_header:
			del output_header['NAXIS4']
		
		if 'CTYPE3' in output_header:
			del output_header['CTYPE3']
		if 'CRVAL3' in output_header:
			del output_header['CRVAL3']
		if 'CDELT3' in output_header:
			del output_header['CDELT3']
		if 'CRPIX3' in output_header:
			del output_header['CRPIX3']
		if 'CROTA3' in output_header:
			del output_header['CROTA3']
		
		if 'CTYPE4' in output_header:
			del output_header['CTYPE4']
		if 'CRVAL4' in output_header:
			del output_header['CRVAL4']
		if 'CDELT4' in output_header:
			del output_header['CDELT4']
		if 'CRPIX4' in output_header:
			del output_header['CRPIX4']
		if 'CROTA4' in output_header:
			del output_header['CROTA4']

		# - Close input file
		hdu.close()

		# - Scale flux?
		bscale= 1
		bzero= 0
		if 'BZERO' in output_header:
			bzero= output_header['BZERO']
		if 'BSCALE' in output_header:
			bscale= output_header['BSCALE']

		if bzero!=0 or bscale!=1:
			logger.info("Scaling image " + filename + " flux by bscale=" + str(bscale) + ", bzero=" + str(bzero) + " ...")
			output_data_scaled= bzero + bscale*output_data
			output_data= output_data_scaled
			output_header['BSCALE']= 1
			output_header['BZERO']= 0
			
		
		# - Add missing BMAJ/BMIN to header?	
		# ...
	
		
		# - Convert data to float 32
		output_data= output_data.astype(np.float32)

		# - Write "fixed" fits
		Utils.write_fits(output_data,outfile,output_header)

		return 0

	@classmethod
	def convertImgToJyPixel(cls,filename,outfile,survey=''):
		""" Convert image units from original to Jy/pixel """

		# - Read fits image
		data, header= Utils.read_fits(filename)
		wcs = WCS(header)

		# - Check header keywords
		if not header['BUNIT']:
			logger.error("No BUNIT keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		if not header['CDELT1']:
			logger.error("No CDELT1 keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		if not header['CDELT2']:
			logger.error("No CDELT2 keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		if not header['CRPIX1']:
			logger.error("No CRPIX1 keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		if not header['CRPIX2']:
			logger.error("No CRPIX2 keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		
		units= header['BUNIT']
		dx= header['CDELT1'] # in deg
		dy= header['CDELT2'] # in deg
		xc= header['CRPIX1']
		yc= header['CRPIX2']	
		ra, dec = wcs.all_pix2world(xc,yc,0,ra_dec_order=True)
		
		#==================
		# - Convert data
		#==================
		convFactor= 1
		
		# - Jy/beam units (e.g. radio maps, apex)
		if units=='JY/BEAM' or units=='Jy/beam':
			
			hasBeamInfo= Utils.hasBeamInfo(header)
			if hasBeamInfo:
				bmaj= header['BMAJ'] # in deg
				bmin= header['BMIN'] # in deg
				convFactor= Utils.getJyBeamToPixel2(bmaj,bmin,dx,dy)
			else:
				logger.warn("No BMAJ/BMIN keyword present in file " + filename + ", trying to retrieve from survey name...")
				beamArea= Utils.getSurveyBeamArea(survey,ra,dec)
				if beamArea>0:
					convFactor= Utils.getJyBeamToPixel(beamArea,dx,dy)
				else:
					logger.error("No BMAJ keyword present in file " + filename + ", cannot compute conversion factor!")
					return -1
		
		# - DN UNITS (e.g WISE MAPS)
		elif units=='DN':
			if survey=='wise_3_4':
				convFactor= 1.9350E-06
			elif survey=='wise_4_6':
				convFactor= 2.7048E-06
			elif survey=='wise_12':
				convFactor= 1.8326e-06
			elif survey=='wise_22':
				convFactor= 5.2269E-05
			else:
				logger.error("Invalid or unknown survey (" + survey + ") given!")
				return -1

		# - MJy/sr units (e.g. HERSCHEL/SPITZER maps)
		elif units=='MJy/sr':
			convFactor= 1.e+6*dx*dy/(206265.*206265.)

		# - W/m^2-sr units (e.g. MSX maps)
		elif units=='W/m^2-sr':
			convFactor_fromJyToSr= dx*dy/(206265.*206265.)
			if survey=='msx_8_3':
				convFactor= 7.133e+12*convFactor_fromJyToSr
			elif survey=='msx_12_1':
				convFactor= 2.863e+13*convFactor_fromJyToSr
			elif survey=='msx_14_7':
				convFactor= 3.216e+13*convFactor_fromJyToSr
			elif survey=='msx_21_3':
				convFactor= 2.476e+13*convFactor_fromJyToSr
			else:
				logger.error("Invalid or unknown survey (" + survey + ") given!")
				return -1

		# - Jy/pixel units (e.g. simulated maps)
		elif units=='Jy/pixel' or units=='JY/PIXEL':
			convFactor= 1
		else:
			logger.error('Units ' + units + ' not recognized!')
			return -1	
						
		# - Scale data
		data_conv= data*convFactor
		header_conv= header	

		# - Edit header
		header_conv['BUNIT']= 'Jy/pixel'

		# - Write converted fits to file
		Utils.write_fits(data_conv,outfile,header_conv)

		return 0

	@classmethod
	def cropImage(cls,filename,ra,dec,crop_size,outfile,source_size=-1,nanfill=True,nanfill_mode='imgmin',nanfill_val=0):
		""" Crop image around (ra,dec) by crop_size """

		# - Read fits image
		data, header= Utils.read_fits(filename)
		wcs = WCS(header)
		dx= header['CDELT1'] # in deg
		dy= header['CDELT2'] # in deg
		pix_size= max(dx,dy) # in deg

		# - Check if crop size is cutting part of the source
		if source_size!=-1:
			source_size_pix= source_size/pix_size
			if source_size_pix>=crop_size:
				logger.warn("Requested crop size (%d) exceeding source size (size=%d arcsec, %d pix), won't write cropped fits file!" % (crop_size,source_size*3600,source_size_pix))
				return -1

		# - Find pixel coordinates corresponding to ra,dec
		x0, y0 = wcs.all_world2pix(ra,dec,0,ra_dec_order=True)

		# - Extract cutout. With option 'partial' when cutout size is larger than image size the cutout will be filled with nan (or specified value)
		cutout= Cutout2D(data, (x0,y0), (crop_size,crop_size), mode='partial',wcs=wcs)
		output_data= cutout.data

		# - Fill NAN?
		if nanfill:
			if nanfill_mode=='imgmin':
				img_min= np.nanmin(output_data)
				output_data[np.isnan(output_data)]= img_min	
			else:
				output_data[np.isnan(output_data)]= nanfill_val
			
		# - Write reshaped image fits
		Utils.write_fits(output_data,outfile)
		
		return 0

	@classmethod
	def estimateBkgFromAnnulus(cls,filename,ra,dec,R1,R2,method='sigmaclip',max_nan_thr=0.1):
		""" Estimate bkg from annulus around given sky position """

		# - Read fits image
		data, header= Utils.read_fits(filename)
		wcs = WCS(header)	

		# - Define sky annulus region
		center= SkyCoord(ra*u.deg,dec*u.deg,frame='fk5')
		annulus_sky = CircleAnnulusSkyRegion(	
			center=center,
			inner_radius=R1*u.arcsec,	
			outer_radius=R2*u.arcsec
		)

		# - Convert sky annulus to pixel annulus
		annulus_pix= annulus_sky.to_pixel(wcs)

		# - Get mask corresponding to annulus and array of pixel values in the mask
		mask= annulus_pix.to_mask()
		mask_data= mask.to_image(shape=data.shape)
		aperture_pixel_data= data[mask_data==1]
		
		# - Integrity check before computing stats
		npixels= aperture_pixel_data.size
		if npixels==0:
			logger.warn("Pixel mask is empty, returning zero!")
			return 0

		nan_counts= np.count_nonzero(np.isnan(aperture_pixel_data))
		nan_fract= float(nan_counts)/float(npixels) 
		if nan_fract>max_nan_thr:
			logger.warn("Fraction of nan pixels in mask (%s) exceeding max threshold (%s), returning zero!" % (str(nan_fract),str(max_nan_thr)))
			return 0
		
		# - Compute median or 3-sigma clipped value as bkg estimator
		bkg= 0
		nsigma= 3
		if method=='median':
			bkg= np.median(aperture_pixel_data)
		elif method=='sigmaclip':
			mean,median,rms= sigma_clipped_stats(aperture_pixel_data,sigma=nsigma)
			bkg= median
		else:
			logger.error("Invalid bkg estimation method (%s) given, returning zero!" % (method))
			return -1			

		return bkg

	@classmethod
	def makeMosaic(cls,input_tbl,combine="mean"):
		""" Create a mosaic from input images """

		# - Get current work directory
		dir_path = os.path.dirname(os.path.realpath(input_tbl))

		# - Computing optimal header
		logger.info("Computing optimal header ...")
		input_tbl_base= Utils.getBaseFileNoExt(input_tbl)
		header_filename= input_tbl_base + '.hdr'
		header_filename_fullpath= dir_path + '/' + header_filename
		montage.mMakeHdr(images_table=input_tbl, template_header=header_filename)
        
		# - Projecting raw frames
		logger.info("Projecting raw frames ...")
		stats_filename= input_tbl_base + '_stats.tbl'
		stats_filename_fullpath= dir_path + '/' + stats_filename
		exact= False
		montage.mProjExec(
			images_table=input_tbl, 
			template_header=header_filename, 
			proj_dir=dir_path, 
			stats_tbl=stats_filename_fullpath,
			exact=exact
		)



