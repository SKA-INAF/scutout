#! /usr/bin/env python
"""
Setup for scutout
"""
import os
import sys
from setuptools import setup


def read(fname):
	"""Read a file"""
	return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
	""" Get the package version number """
	import scutout
	return scutout.__version__



PY_MAJOR_VERSION=sys.version_info.major
PY_MINOR_VERSION=sys.version_info.minor
print("PY VERSION: maj=%s, min=%s" % (PY_MAJOR_VERSION,PY_MINOR_VERSION))

reqs= []
reqs.append('numpy>=1.10')
reqs.append('astropy>=2.0, <3')
reqs.append('montage-wrapper')
reqs.append('radio-beam')
reqs.append('regions')

if PY_MAJOR_VERSION<=2:
	print("PYTHON 2 detected")
	reqs.append('future')
	reqs.append('scipy<=1.2.1')
	reqs.append('pyparsing>=2.0.1')
	#reqs.append('matplotlib<=2.2.4')
else:
	print("PYTHON 3 detected")
	reqs.append('scipy')
	reqs.append('pyparsing')
	#reqs.append('matplotlib')




data_dir = 'data'

setup(
	name="scutout",
	version=get_version(),
	author="Simone Riggi",
	author_email="simone.riggi@gmail.com",
	description="Tool to extract source cutouts from a collection of astronomical FITS images",
	license = "GPL3",
	url="https://github.com/SKA-INAF/scutout",
	long_description=read('README.md'),
	packages=['scutout'],
	install_requires=reqs,
	scripts=['scripts/run_scutout.py'],
	
)
