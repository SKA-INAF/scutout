# scutout
Tool to extract source cutouts from a collection of FITS astronomical images

## **Status**
This software is under development.

## **Credit**
This software is distributed with GPLv3 license. If you use scutout for your research, please add repository link or acknowledge authors in your papers.

## **Installation**  

To build and install the package:    

* Create a local install directory, e.g. ```$INSTALL_DIR```
* Add installation path to your ```PYTHONPATH``` environment variable:   
  ``` export PYTHONPATH=$PYTHONPATH:$INSTALL_DIR/lib/python2.7/site-packages ```
* Build and install package:   
  ``` python setup install --prefix=$INSTALL_DIR```   

All dependencies will be automatically downloaded and installed in ```$INSTALL_DIR```.   
     
To use package scripts:

* Add binary directory to your ```PATH``` environment variable:   
  ``` export PATH=$PATH:$INSTALL_DIR/bin ```    

## **Usage**  

To run source cutout tool:

* Prepare a configuration file (e.g. ```config.ini```) with desired options (e.g. workdir, data paths, cutout search options, etc). A sample config file is provided in the ```config``` directory.    
* Prepare an ascii file (e.g. ```sources.dat```) with source sky positions for cutout extraction. File shall be given with the following column format:
    - col1: Source right ascension (RA) in degrees    
    - col2: Source declination (Dec) in degrees    
    - col3: Source name identifier    

* Run cutout search:   
  ``` $INSTALL_DIR/bin/run_scutout.py --config=config.ini --filename=sources.dat```   
