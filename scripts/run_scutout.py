#!/usr/bin/env python

from __future__ import print_function

##################################################
###          MODULE IMPORT
##################################################
## STANDARD MODULES
import os
import sys
import subprocess
import string
import time
import signal
from threading import Thread
import datetime
import numpy as np
import random
import math
import logging

## COMMAND-LINE ARG MODULES
import getopt
import argparse
import collections

## MODULES
from scutout import __version__, __date__
from scutout import logger
from scutout.config import Config
from scutout.cutout_extractor import CutoutFinder

#### GET SCRIPT ARGS ####
def str2bool(v):
	if v.lower() in ('yes', 'true', 't', 'y', '1'):
		return True
	elif v.lower() in ('no', 'false', 'f', 'n', '0'):
		return False
	else:
		raise argparse.ArgumentTypeError('Boolean value expected.')


###########################
##     ARGS
###########################
def get_args():
	"""This function parses and return arguments passed in"""
	parser = argparse.ArgumentParser(description="Parse args.")
	
	parser.add_argument('-filename','--filename', dest='filename', required=True, type=str, default='', help='List of source position to be searched for cutout (ascii format)') 
	parser.add_argument('-config','--config', dest='config', required=True, type=str, default='', help='Configuration file (INI format)') 
	parser.add_argument('-loglevel','--loglevel', dest='loglevel', required=False, type=str, default='INFO', help='Logging level (default=INFO)') 
	
	# ...
	# ...

	args = parser.parse_args()	

	return args


##############
##   MAIN   ##
##############
def main():
	"""Main function"""

	
	#===========================
	#==   PARSE ARGS
	#===========================
	logger.info("Get script args ...")
	try:
		args= get_args()
	except Exception as ex:
		logger.error("Failed to get and parse options (err=%s)",str(ex))
		return 1

	filename= args.filename
	config_filename= args.config
	log_level_str= args.loglevel.upper()

	log_level = getattr(logging, log_level_str, None)
	if not isinstance(log_level, int):
		logger.error('Invalid log level given: ' + log_level_str)
		return 1
	logger.setLevel(log_level)

	if not filename:
		logger.error("Input file name with coordinate list is empty!")
		return 1
	if not config_filename:
		logger.error("Configuration file name is empty!")
		return 1

	
	#===========================
	#==   PARSE CONFIG
	#===========================
	logger.info("Parse config file ...")

	config= Config()
	status= config.parse(config_filename)	
	if status<0:
		logger.error("Failed to parse and validate config file " + config_filename + "!")
		return 1

	
	#===========================
	#==   RUN CUTOUT SEARCH
	#===========================
	logger.info("Run cutout search ...")
	finder= CutoutFinder(filename,config)

	status= finder.run_search()
	if status<0:
		logger.error("Cutout finder run failed!")
		return -1


	return 0

###################
##   MAIN EXEC   ##
###################
if __name__ == "__main__":
	sys.exit(main())

