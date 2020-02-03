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
* Prepare an ascii file (e.g. ```sources.dat```) with source sky positions for cutout extraction. File shall be given with the following header and space-delimited columns:    
    
    ```# RA DEC RADIUS OBJNAME```    
    ```ra1 dec1 r1 sname1```    
    ```ra2 dec2 r2 sname2```    
    ```... ... ... ...```     
    ```... ... ... ...```    
         
    where:    
    - RA column (mandatory): Source right ascension in degrees   
    - DEC column (mandatory): Source declination in degrees    
    - RADIUS column (optional): Source radius in arcsec. If not given a default source radius (```source_radius``` option) will be used   
    - OBJNAME column (mandatory): Source name identifier, used as basis to create source cutout sub-directory    

* Run cutout search:   
  ``` $INSTALL_DIR/bin/run_scutout.py --config=config.ini --filename=sources.dat```   
