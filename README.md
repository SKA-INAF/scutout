# scutout
Tool to extract source cutouts from a collection of FITS astronomical images

## **Credit**
This software is distributed with GPLv3 license. If you use scutout for your research, please add repository link or acknowledge authors in your papers.

## **Installation**  

To install the package with pip from PyPi:      

``` pip install scutout ```     
      
To build and install the package from source:    

* Clone this repository or download the tar file of the desired release;    
* Create a local install directory, e.g. ```$INSTALL_DIR```;    
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

* Prepare a configuration file (e.g. ```config.ini```) with desired options (e.g. workdir, data paths, cutout search options, etc). A sample config file (.ini format) is provided in the ```config``` directory. Supported options are:        

  `[RUN]`
    - `workdir`: Work directory where to place cutout files. Default: current directory
    - `keep_tmpfiles`: To keep or remove tmp files produced per each source. Valid values: {yes|no}. Default: yes    
    
  `[CUTOUT_SEARCH]`
    - `survey`: List of surveys to be searched, separated by commas. For each searched survey you must provide the path to metadata (e.g. a .tbl table produced by Montage mImgtbl task). Valid values: {first, nvss, mgps, vgps, sgps, cornish, scorpio_atca_2_1, scorpio_askap15_b1, scorpio_askap36_b123, scorpio_askap36_b123_ch[1-5], meerkat_gps, meerkat_gps_ch[1-14], askap_racs, thor, irac_3_6, irac_4_5, irac_5_8, irac_8, mips_24, higal_70, higal_160, higal_250, higal_350, higal_500, wise_3_4, wise_4_6, wise_12, wise_22, atlasgal, atlasgal_planck, msx_8_3, msx_12_1, msx_14_7, msx_21_3}.    
    - `use_same_radius`: Use the source radius given in `source_radius` option instead of the radius provided in input file. Valid values: {yes|no}. Default: no
    - `source_radius`: Source radius in arcsec used by default if no radius is given in the input file. Default: 300"
    - `cutout_factor`: Used to compute cutout size as 2 x source_radius x cutout_factor. Default: 5
    - `multi_input_img_mode`: Method used to deal with multiple input image found in a given survey. Valid values: {best,mosaic,first}. Best takes the image in which the given source is better covered. Mosaic performs a mosaic of the available images found. This option is slower and was found to crash occasionally. First takes the first image available regardless of the source coverage. Default: best
    - `convert_to_jy_pixel`: To convert cutout image units in Jy/pixels. Valid values: {yes|no}. Default: yes
    - `subtract_bkg`: Subtract background from image (done before reprojection). Valid values: {yes|no}. Default: no
    - `regrid`: To regrid cutouts to same projection (aligned to North): Valid values: {yes|no}. Default: yes
    - `convolve`: To convolve cutouts to same resolution. Valid values: {yes|no}. Default: yes
    - `crop`: To crop cutouts around source position to have final images with same number of pixels. Valid values: {yes|no}. Default: yes
    - `crop_size`: Cropped image size in pixels. Default: 200
    
  `[BKG_SUBTRACTION]`    
    - `bkg_estimator`: Estimator used to compute the background. Valid values: {median|sigmaclip}. Default: sigmaclip
    - `bkg_inner_radius_factor`: Factor used to compute the background annulus inner radius R1= R_source x factor. Default: 1.1
    - `bkg_outer_radius_factor`: Factor used to compute the background annulus outer radius R2= R_source x factor. Default: 1.2
    - `bkg_max_nan_thr`: Max fraction of NAN pixels in background annulus above which bkg calculation fails. In this case the background is set to 0. Default: 0.1
    
  `[XXX_DATA]`
    - `metadata`: Path to Montage table (.tbl file produced with Montage mImgtbl task) containing survey FITS file list and metadata. Specify an option block per each survey XXX, where XXX can be: {FIRST, NVSS, MGPS, VGPS, SGPS, CORNISH, APEX_ATLASGAL, APEX_ATLASGAL_PLANCK, SCORPIO_ATCA_2_1_DATA, SCORPIO_ASKAP15_B1, SCORPIO_ASKAP36_B123, SCORPIO_ASKAP36_B123_CH[1-5], MEERKAT_GPS, MEERKAT_GPS_CH[1-14], ASKAP_RACS, THOR, WISE_3_4, WISE_4_6, WISE_12, WISE_22, SPITZER_IRAC3_6, SPITZER_IRAC4_5, SPITZER_IRAC5_8, SPITZER_IRAC8, SPITZER_MIPS24, HERSCHEL_HIGAL70, HERSCHEL_HIGAL160, HERSCHEL_HIGAL250, HERSCHEL_HIGAL350, HERSCHEL_HIGAL500, MSX_8_3, MSX_12_1, MSX_14_7, MSX_21_3}   
    
    
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

## **Testing** 

To run unit tests, enter into scutout directory and type:

``` python -m unittest -v tests.test_utils```

or, if coverage library is installed:

``` coverage run --source=scutout -m unittest -v tests.test_utils ```
