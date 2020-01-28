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
	def getJyBeamToPixelConvFactor(cls,bmaj,bmin,dx,dy):
		""" Compute conversion factor from Jy/beam to Jy/pixel """

		beamArea= np.pi * bmaj * bmin/(4.*np.log(2))
		pixArea= np.abs(dx*dy)
		toJyPerPix = pixArea/beamArea

		return toJyPerPix

	@classmethod
	def convertImgToJyPixel(cls,filename,outfile,band=-1):
		""" Convert image units from original to Jy/pixel """

		# - Read fits image
		data, header= Utils.read_fits(filename)

		# - Check header keywords
		if not header['BUNIT']:
			logger.error("No BUNIT keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		if not header['BMAJ']:
			logger.error("No BMAJ keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		if not header['BMIN']:
			logger.error("No BMIN keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		if not header['CDELT1']:
			logger.error("No CDELT1 keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		if not header['CDELT2']:
			logger.error("No CDELT2 keyword present in file " + filename + ", cannot compute conversion factor!")
			return -1
		units= header['BUNIT']
		bmaj= header['BMAJ']
		bmin= header['BMIN']
		dx= header['CDELT1']
		dy= header['CDELT2']

		#==================
		# - Convert data
		#==================
		convFactor= 1
		
		# - RADIO SURVEY MAPS
		if units=='JY/BEAM' or units=='Jy/beam':
			convFactor= Utils.getJyBeamToPixelConvFactor(bmaj,bmin,dx,dy)

		# - WISE MAPS
		elif units=='DN':
			if band==1:
				convFactor= 1.9350E-06
			elif band==2:
				convFactor= 2.7048E-06
			elif band==3:
				convFactor= 1.8326e-06
			elif band==4:
				convFactor= 5.2269E-05
			else:
				logger.error("Invalid or unknown band (" + str(band) + ") given!")
				return -1

		# - HERSCHEL/SPITZER MAPS
		elif units=='MJy/sr':
			convFactor= 1.e+6*dx*dy/(206265.*206265.)

		# - Jy/pixel (e.g. simulated maps)
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

