import unittest
import logging
import builtins
import copy
import sys
import numpy as np
from astropy.io import fits
from astropy import units as u
from unittest.mock import patch
from .context import utils


class UtilsTest(unittest.TestCase):
    """Tests for 'utils' package methods"""

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(filename='tests/exec.log',
                            filemode='a', level=logging.WARNING)

    def setUp(self):
        self.utils = utils.Utils

    def _createDummyFITS(self, ndim=2, radec=(0, 0), delt=0.00166667, size=512, bkg_mean=0, bkg_std=0.5, bunit='K'):
        """ Creates dummy FITS file for testing purposes
        Args:
        - ndim:         number of dimensions
        - radec:        tuple of RA, DEC in degrees (default=(0,0))
        - delt:         RA, DEC increment in degrees (default=6'')
        - size:         image size in pixels (default=512)
        - bkg_mean:     background mean in brightness units (default=0)
        """

        data = bkg_mean + bkg_std * np.random.randn(size, size)
        hdu = fits.PrimaryHDU(data)

        # add world properties
        hdu.header['CTYPE1'] = 'RA---TAN'
        hdu.header['CTYPE2'] = 'DEC--TAN'
        hdu.header['CRVAL1'] = radec[0]
        hdu.header['CRVAL2'] = radec[1]
        hdu.header['CDELT1'] = delt     # default 6''/px
        hdu.header['CDELT2'] = -delt    # default 6''/px
        hdu.header['CRPIX1'] = size/2
        hdu.header['CRPIX2'] = size/2
        hdu.header['EQUINOX'] = 2000.00

        # add degenerate axes if needed
        if (ndim > 2):
            for idx in range(3, ndim+1):
                hdu.data = np.expand_dims(hdu.data, axis=0)  # append axis
                hdu.header['CTYPE' + str(idx)] = 'EXTRA'
                hdu.header['CRVAL' + str(idx)] = '0'
                hdu.header['CDELT' + str(idx)] = delt
                hdu.header['CRPIX' + str(idx)] = 0
                hdu.header['CROTA' + str(idx)] = 0

        # add some additional default stuff
        hdu.header['BUNIT'] = bunit
        hdu.header['TELESCOP'] = 'TEST-TEL'
        hdu.header['INSTRUME'] = 'TEST-INS'
        hdu.header['DATE_OBS'] = '2001-01-01'
        hdu.header['OBJECT'] = 'TEST-SOU'
        return hdu

    # Basic methods
    def test_getBaseFile(self):
        self.assertEqual(self.utils.getBaseFile('test.txt'), 'test.txt')
        self.assertEqual(self.utils.getBaseFile(
            '/usr/local/test.txt'), 'test.txt')
        self.assertEqual(self.utils.getBaseFile('test'), 'test')

    def test_getBaseFileNoExt(self):
        self.assertEqual(self.utils.getBaseFileNoExt('test.txt'), 'test')
        self.assertEqual(self.utils.getBaseFileNoExt(
            '/usr/local/test.txt'), 'test')
        self.assertEqual(self.utils.getBaseFileNoExt('test'), 'test')

    def test_has_pattern_in_string(self):
        self.assertTrue(self.utils.has_patterns_in_string('test_string', '_'))
        # self.assertFalse(self.utils.has_patterns_in_string('test_string','test_string'))
        self.assertFalse(self.utils.has_patterns_in_string('test_string', '?'))

    def test_crop_img_Basic(self):
        hdu = self._createDummyFITS()

        x_max = hdu.shape[0]
        y_max = hdu.shape[1]

        crop = self.utils.crop_img(hdu.data, x_max/2, y_max/2, 10, 10)
        self.assertEqual(crop.shape, (11, 11))

        crop = self.utils.crop_img(hdu.data, x_max/2, y_max/2, 17, 25)
        self.assertEqual(crop.shape, (26, 18))

    def test_crop_img_OutOfBounds(self):
        hdu = self._createDummyFITS()

        x_max = hdu.shape[0]
        y_max = hdu.shape[1]

        crop = self.utils.crop_img(hdu.data, 0, 0, 10, 10)
        self.assertEqual(crop.shape, (0, 0))
        self.assertEqual(crop.shape, (0, 0))

    # Test survey beams

    def test_getBeamArea(self):
        deg_conv = 1/3600
        self.assertEqual(self.utils.getBeamArea(
            1*deg_conv, 1*deg_conv), 8.742978668648137e-08)
        self.assertEqual(self.utils.getBeamArea(0, 1*deg_conv), 0)
        self.assertEqual(self.utils.getBeamArea(0, 0), 0)

    def test_getNVSSSurveyBeamArea(self):
        self.assertEqual(self.utils.getNVSSSurveyBeamArea(),
                         0.00017704531804012478)

    def test_getFIRSTSurveyBeamArea(self):
        self.assertEqual(self.utils.getFIRSTSurveyBeamArea(
            ra=0, dec=0), 3.021573427884796e-06)
        self.assertEqual(self.utils.getFIRSTSurveyBeamArea(
            ra=0, dec=5), 2.5494525797777964e-06)
        self.assertEqual(self.utils.getFIRSTSurveyBeamArea(
            ra=20, dec=-5), 3.2104217671275954e-06)
        self.assertEqual(self.utils.getFIRSTSurveyBeamArea(
            ra=320, dec=-5), 3.2104217671275954e-06)

    def test_getMGPSSurveyBeamArea(self):
        self.assertEqual(self.utils.getMGPSSurveyBeamArea(
            dec=0), 0.00016165767558330406)
        self.assertEqual(self.utils.getMGPSSurveyBeamArea(
            dec=10), 0.0009309494505227407)

    def test_getSGPSSurveyBeamArea(self):
        self.assertEqual(self.utils.getSGPSSurveyBeamArea(),
                         0.0008742978668648136)

    def test_getVGPSSurveyBeamArea(self):
        self.assertEqual(self.utils.getVGPSSurveyBeamArea(),
                         0.00017704531804012478)

    def test_getWiseSurveyBeamArea(self):
        self.assertEqual(self.utils.getWiseSurveyBeamArea(
            band='wise_3_4'),  6.316802088098279e-06)
        self.assertEqual(self.utils.getWiseSurveyBeamArea(
            band='wise_4_6'),  6.316802088098279e-06)
        self.assertEqual(self.utils.getWiseSurveyBeamArea(
            band='wise_12'),  6.316802088098279e-06)
        self.assertEqual(self.utils.getWiseSurveyBeamArea(
            band='wise_22'),  2.5267208352393116e-05)
        self.assertEqual(self.utils.getWiseSurveyBeamArea(band='no_band'),  0)
        self.assertEqual(self.utils.getWiseSurveyBeamArea(band=''),  0)

    def test_getIRACSurveyBeamArea(self):
        self.assertEqual(self.utils.getIRACSurveyBeamArea(
            band='irac_3_6'), 2.526720835239311e-07)
        self.assertEqual(self.utils.getIRACSurveyBeamArea(
            band='irac_4_5'), 2.526720835239311e-07)
        self.assertEqual(self.utils.getIRACSurveyBeamArea(
            band='irac_5_8'), 2.526720835239311e-07)
        self.assertEqual(self.utils.getIRACSurveyBeamArea(
            band='irac_8'), 3.156215299381976e-07)
        self.assertEqual(self.utils.getIRACSurveyBeamArea(band='no_band'),  0)
        self.assertEqual(self.utils.getIRACSurveyBeamArea(band=''),  0)

    def test_getMIPSSurveyBeamArea(self):
        self.assertEqual(self.utils.getMIPSSurveyBeamArea(),
                         3.147472320713329e-06)

    def test_getHiGalSurveyBeamArea(self):
        self.assertEqual(self.utils.getHiGalSurveyBeamArea(
            band='higal_70'), 6.334650354471603e-06)
        self.assertEqual(self.utils.getHiGalSurveyBeamArea(
            band='higal_160'), 1.2806943258149252e-05)
        self.assertEqual(self.utils.getHiGalSurveyBeamArea(
            band='higal_250'), 2.8327250886419965e-05)
        self.assertEqual(self.utils.getHiGalSurveyBeamArea(
            band='higal_350'), 5.0359557131413266e-05)
        self.assertEqual(self.utils.getHiGalSurveyBeamArea(
            band='higal_500'), 0.00010406330360358443)
        self.assertEqual(self.utils.getIRACSurveyBeamArea(band='no_band'),  0)
        self.assertEqual(self.utils.getHiGalSurveyBeamArea(band=''),  0)

    def test_getATLASGALSurveyBeamArea(self):
        self.assertEqual(self.utils.getATLASGALSurveyBeamArea(),
                         3.0247209002055094e-05)

    def test_getATLASGALPlanckSurveyBeamArea(self):
        self.assertEqual(
            self.utils.getATLASGALPlanckSurveyBeamArea(), 3.8556535928738286e-05)

    def test_getMSXSurveyBeamArea(self):
        self.assertEqual(self.utils.getMSXSurveyBeamArea(),
                         3.497191467459255e-05)

    def test_getScorpioATCASurveyBeamArea(self):
        self.assertEqual(self.utils.getScorpioATCASurveyBeamArea(
            band='scorpio_atca_2_1'), 4.969509075259601e-06)
        self.assertEqual(self.utils.getScorpioATCASurveyBeamArea(
            band='scorpio_atca_5_0'), 0)  # Not implemented

    def test_getScorpioASKAP15B1SurveyBeamArea(self):
        self.assertEqual(
            self.utils.getScorpioASKAP15B1SurveyBeamArea(), 4.4064612489986616e-05)

    def test_getScorpioASKAP36B123SurveyBeamArea(self):
        self.assertEqual(
            self.utils.getScorpioASKAP36B123SurveyBeamArea(), 6.340874918134747e-06)

    def test_getTHORSurveyBeamArea(self):
        self.assertEqual(self.utils.getTHORSurveyBeamArea(),
                         1.2589889282853316e-05)

    def test_getSurveyBeamArea(self):
        self.assertEqual(self.utils.getSurveyBeamArea(
            'nvss'), 0.00017704531804012478)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'first', 0, 0), 3.021573427884796e-06)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'mgps', 0), 0.00016165767558330406)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'sgps'), 0.0008742978668648136)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'vgps'), 0.00017704531804012478)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'wise_3_4'), 6.316802088098279e-06)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'wise_4_6'), 6.316802088098279e-06)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'wise_12'), 6.316802088098279e-06)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'wise_22'), 2.5267208352393116e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'irac_3_6'), 2.526720835239311e-07)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'irac_4_5'), 2.526720835239311e-07)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'irac_5_8'), 2.526720835239311e-07)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'irac_8'), 3.156215299381976e-07)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'mips_24'), 3.147472320713329e-06)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'higal_70'), 6.334650354471603e-06)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'higal_160'), 1.2806943258149252e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'higal_250'), 2.8327250886419965e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'higal_350'), 5.0359557131413266e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'higal_500'), 0.00010406330360358443)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'atlasgal'),  3.0247209002055094e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'atlasgal_planck'), 3.8556535928738286e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'msx_8_3'), 3.497191467459255e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'msx_12_1'), 3.497191467459255e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'msx_14_7'), 3.497191467459255e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'msx_21_3'), 3.497191467459255e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'scorpio_atca_2_1'), 4.969509075259601e-06)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'scorpio_askap15_b1'), 4.4064612489986616e-05)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'scorpio_askap36_b123'), 6.340874918134747e-06)
        self.assertEqual(self.utils.getSurveyBeamArea(
            'thor'), 1.2589889282853316e-05)

    # Helpers

    def test_getJyBeamToPixel(self):
        self.assertEqual(self.utils.getJyBeamToPixel(
            beamArea=1e-8, dx=1e-9, dy=1e-9), 1e-10)
        # negative dx/dy
        self.assertEqual(self.utils.getJyBeamToPixel(
            beamArea=1e-8, dx=-1e-9, dy=1e-9), 1e-10)
        self.assertEqual(self.utils.getJyBeamToPixel(beamArea=0.011330900354567986,
                                                     dx=0.1, dy=0.1), 0.8825424006106064)         # pxl size equal to bmaj, bmin
        self.assertEqual(self.utils.getJyBeamToPixel2(
            bmaj=0.1, bmin=0.1, dx=0.1, dy=0.1), 0.8825424006106064)                    # test overload

    def test_hasBeamInfo_NoBeam(self):
        hdu = self._createDummyFITS()
        self.assertFalse(self.utils.hasBeamInfo(hdu.header))

    def test_hasBeamInfo_EmptyBeam(self):
        hdu = self._createDummyFITS()
        hdu.header['BMAJ'] = ''
        hdu.header['BMIN'] = ''
        self.assertFalse(self.utils.hasBeamInfo(hdu.header))

    def test_hasBeamInfo_BaseCase(self):
        hdu = self._createDummyFITS()
        hdu.header['BMAJ'] = 1
        hdu.header['BMIN'] = 1
        self.assertTrue(self.utils.hasBeamInfo(hdu.header))

    @patch('utils.Utils.write_fits')
    @patch('utils.fits.open')
    def test_fixImgAxisAndUnits_Input2DFits(self, mock_read, mock_write):
        hdu = self._createDummyFITS(ndim=2)         # dummy 2D fits
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = fits.HDUList([hdu])
        self.assertEqual(self.utils.fixImgAxisAndUnits(infile, outfile), 0)
        assert mock_read.called
        assert mock_write.called
        fixed_hdu = mock_write.call_args[0]
        fixed_hdu_data = fixed_hdu[0]
        fixed_hdu_name = fixed_hdu[1]
        fixed_hdu_head = fixed_hdu[2]

        self.assertEqual(fixed_hdu_data.ndim, 2)        # check dimensions
        self.assertEqual(fixed_hdu_name, outfile)       # check file name
        self.assertEqual(fixed_hdu_head['NAXIS'], 2)    # check header
        self.assertFalse('NAXIS3' in fixed_hdu_head)
        self.assertFalse('CRVAL3' in fixed_hdu_head)
        self.assertFalse('CRPIX3' in fixed_hdu_head)
        self.assertFalse('CDELT3' in fixed_hdu_head)
        self.assertFalse('CROTA3' in fixed_hdu_head)

    @patch('utils.Utils.write_fits')
    @patch('utils.fits.open')
    def test_fixImgAxisAndUnits_Input3DFits(self, mock_read, mock_write):
        hdu = self._createDummyFITS(ndim=3)         # dummy 3D fits
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = fits.HDUList([hdu])

        # invalid number of channels
        self.assertEqual(self.utils.fixImgAxisAndUnits(infile, outfile), -1)
        assert mock_read.called
        assert not mock_write.called

    @patch('utils.Utils.write_fits')
    @patch('utils.fits.open')
    def test_fixImgAxisAndUnits_Input4DFits(self, mock_read, mock_write):
        hdu = self._createDummyFITS(size=512, ndim=4)         # dummy 4D fits
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = fits.HDUList([hdu])

        self.assertEqual(self.utils.fixImgAxisAndUnits(infile, outfile), 0)
        assert mock_read.called
        assert mock_write.called
        fixed_hdu = mock_write.call_args[0]
        fixed_hdu_data = fixed_hdu[0]
        fixed_hdu_name = fixed_hdu[1]
        fixed_hdu_head = fixed_hdu[2]

        self.assertEqual(fixed_hdu_data.ndim, 2)        # check dimensions
        self.assertEqual(fixed_hdu_data.shape, (512, 512))
        self.assertEqual(fixed_hdu_name, outfile)       # check file name
        self.assertEqual(fixed_hdu_head['NAXIS'], 2)    # check header
        self.assertFalse('NAXIS3' in fixed_hdu_head)
        self.assertFalse('CRVAL3' in fixed_hdu_head)
        self.assertFalse('CRPIX3' in fixed_hdu_head)
        self.assertFalse('CDELT3' in fixed_hdu_head)
        self.assertFalse('CROTA3' in fixed_hdu_head)
        self.assertFalse('NAXIS4' in fixed_hdu_head)
        self.assertFalse('CRVAL4' in fixed_hdu_head)
        self.assertFalse('CRPIX4' in fixed_hdu_head)
        self.assertFalse('CDELT4' in fixed_hdu_head)
        self.assertFalse('CROTA4' in fixed_hdu_head)

    @patch('utils.Utils.write_fits')
    @patch('utils.fits.open')
    def test_fixImgAxisAndUnits_FluxScaleCorrection(self, mock_read, mock_write):
        hdu = self._createDummyFITS(ndim=2)         # dummy 2D fits
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        # add flux scale headers
        hdu.header['BZERO'] = 1500.0
        hdu.header['BSCALE'] = 2.0
        mock_read.return_value = fits.HDUList([hdu])

        self.assertEqual(self.utils.fixImgAxisAndUnits(infile, outfile), 0)
        assert mock_read.called
        assert mock_write.called
        fixed_hdu = mock_write.call_args[0]
        fixed_hdu_data = fixed_hdu[0]
        fixed_hdu_name = fixed_hdu[1]
        fixed_hdu_head = fixed_hdu[2]

        self.assertEqual(fixed_hdu_data.ndim, 2)        # check dimensions
        self.assertEqual(fixed_hdu_data.shape, (512, 512))
        self.assertEqual(fixed_hdu_name, outfile)       # check file name
        self.assertEqual(fixed_hdu_head['NAXIS'], 2)    # check header
        self.assertEqual(fixed_hdu_head['BSCALE'], 1)
        self.assertEqual(fixed_hdu_head['BZERO'], 0)
        self.assertAlmostEqual(fixed_hdu_data[0, 0] -
                               hdu.data[0, 0], 1500+hdu.data[0, 0], places=1)   # check that output flux is BZERO+BSCALE*input flux

    def test_fromBrightnessTempToJyBeam(self):
        self.assertAlmostEqual(self.utils.fromBrightnessTempToJyBeam(
            nu_GHz=90.5, bmin_arcsec=0.17, bmaj_arcsec=0.20), 0.0002278, places=5)
        self.assertAlmostEqual(self.utils.fromBrightnessTempToJyBeam(
            nu_GHz=230.5, bmin_arcsec=1.0, bmaj_arcsec=1.0), 0.043478, places=5)
        self.assertAlmostEqual(self.utils.fromBrightnessTempToJyBeam(
            nu_GHz=345.8, bmin_arcsec=19.5, bmaj_arcsec=19.5), 37.20, places=1)

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_MissingHeaders(self, mock_read, mock_write):
        hdu = self._createDummyFITS()
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        for keyword in ['BUNIT', 'CDELT1', 'CDELT2', 'CRPIX1', 'CRPIX2']:
            header = copy.copy(hdu.header)
            del header[keyword]
            mock_read.return_value = (hdu.data, header)
            with self.subTest(kw=keyword):
                self.assertEqual(
                    self.utils.convertImgToJyPixel(infile, outfile), -1)
                assert mock_read.called
                assert not mock_write.called

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsJyBeam(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='Jy/beam')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        # beam info available
        hdu.header['BMAJ'] = 0.01667
        hdu.header['BMIN'] = 0.01667
        mock_read.return_value = (hdu.data, hdu.header)
        self.assertEqual(self.utils.convertImgToJyPixel(infile, outfile), 0)
        assert mock_read.called
        assert mock_write.called
        fixed_hdu = mock_write.call_args[0]
        fixed_hdu_data = fixed_hdu[0]
        fixed_hdu_name = fixed_hdu[1]
        fixed_hdu_head = fixed_hdu[2]
        self.assertEqual(fixed_hdu_name, outfile)
        self.assertEqual(fixed_hdu_head['BUNIT'], 'Jy/pixel')

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsJyBeam_SurveyProvided(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='Jy/beam')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        # no beam info, survey provided
        mock_read.return_value = (hdu.data, hdu.header)
        self.assertEqual(self.utils.convertImgToJyPixel(
            infile, outfile, 'nvss'), 0)
        assert mock_read.called
        assert mock_write.called
        fixed_hdu = mock_write.call_args[0]
        fixed_hdu_data = fixed_hdu[0]
        fixed_hdu_name = fixed_hdu[1]
        fixed_hdu_head = fixed_hdu[2]
        self.assertEqual(fixed_hdu_name, outfile)
        self.assertEqual(fixed_hdu_head['BUNIT'], 'Jy/pixel')

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsJyBeam_NoBeamInfoNoSurvey(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='Jy/beam')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)
        self.assertEqual(self.utils.convertImgToJyPixel(
            infile, outfile, 'foo'), -1)

        mock_read.return_value = (hdu.data, hdu.header)
        self.assertEqual(self.utils.convertImgToJyPixel(
            infile, outfile), -1)

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsDN(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='DN')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        for wise_survey in ['wise_3_4', 'wise_4_6', 'wise_12', 'wise_22']:
            with self.subTest():
                header = copy.copy(hdu.header)
                mock_read.return_value = (hdu.data, header)
                mock_read.reset_mock()
                mock_write.reset_mock()
                self.assertEqual(self.utils.convertImgToJyPixel(
                    infile, outfile, wise_survey), 0)
                assert mock_read.called
                assert mock_write.called
                fixed_hdu = mock_write.call_args[0]
                fixed_hdu_data = fixed_hdu[0]
                fixed_hdu_name = fixed_hdu[1]
                fixed_hdu_head = fixed_hdu[2]
                self.assertEqual(fixed_hdu_name, outfile)
                self.assertEqual(fixed_hdu_head['BUNIT'], 'Jy/pixel')
                # position of maxima should match (just scaling)
                self.assertEqual(np.argmax(fixed_hdu_data),
                                 np.argmax(hdu.data))

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsMJysr(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='MJy/sr')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)
        self.assertEqual(self.utils.convertImgToJyPixel(
            infile, outfile), 0)
        assert mock_read.called
        assert mock_write.called
        fixed_hdu = mock_write.call_args[0]
        fixed_hdu_data = fixed_hdu[0]
        fixed_hdu_name = fixed_hdu[1]
        fixed_hdu_head = fixed_hdu[2]
        self.assertEqual(fixed_hdu_name, outfile)
        self.assertEqual(fixed_hdu_head['BUNIT'], 'Jy/pixel')
        # position of maxima should match (just scaling)
        self.assertEqual(np.argmax(fixed_hdu_data), np.argmax(hdu.data))

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsWm2sr(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='W/m^2-sr')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        for msx_survey in ['msx_8_3', 'msx_12_1', 'msx_14_7', 'msx_21_3']:
            with self.subTest():
                mock_read.reset_mock()
                mock_write.reset_mock()
                header = copy.copy(hdu.header)
                mock_read.return_value = (hdu.data, header)
                self.assertEqual(self.utils.convertImgToJyPixel(
                    infile, outfile, msx_survey), 0)
                assert mock_read.called
                assert mock_write.called
                fixed_hdu = mock_write.call_args[0]
                fixed_hdu_data = fixed_hdu[0]
                fixed_hdu_name = fixed_hdu[1]
                fixed_hdu_head = fixed_hdu[2]
                self.assertEqual(fixed_hdu_name, outfile)
                self.assertEqual(fixed_hdu_head['BUNIT'], 'Jy/pixel')
                # position of maxima should match (just scaling)
                self.assertEqual(np.argmax(fixed_hdu_data),
                                 np.argmax(hdu.data))

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsK(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='K')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        # case 1: vgps
        header = copy.copy(hdu.header)
        mock_read.return_value = (hdu.data, header)
        self.assertEqual(self.utils.convertImgToJyPixel(
            infile, outfile, 'vgps'), 0)
        assert mock_read.called
        assert mock_write.called
        fixed_hdu = mock_write.call_args[0]
        fixed_hdu_data = fixed_hdu[0]
        fixed_hdu_name = fixed_hdu[1]
        fixed_hdu_head = fixed_hdu[2]
        self.assertEqual(fixed_hdu_name, outfile)
        self.assertEqual(fixed_hdu_head['BUNIT'], 'Jy/pixel')
        # position of maxima should match (just scaling)
        self.assertEqual(np.argmax(fixed_hdu_data), np.argmax(hdu.data))

        # case 2: no survey
        mock_read.reset_mock()
        mock_write.reset_mock()
        header = copy.copy(hdu.header)
        mock_read.return_value = (hdu.data, header)
        self.assertEqual(self.utils.convertImgToJyPixel(
            infile, outfile), -1)
        # position of maxima should match (just scaling)
        self.assertEqual(np.argmax(fixed_hdu_data), np.argmax(hdu.data))
        assert mock_read.called
        assert not mock_write.called

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsJypixel(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='Jy/pixel')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        # no conversion needed!
        mock_read.return_value = (hdu.data, hdu.header)
        self.assertEqual(self.utils.convertImgToJyPixel(
            infile, outfile), 0)
        assert mock_read.called
        assert mock_write.called
        fixed_hdu = mock_write.call_args[0]
        fixed_hdu_data = fixed_hdu[0]
        fixed_hdu_name = fixed_hdu[1]
        fixed_hdu_head = fixed_hdu[2]
        self.assertEqual(fixed_hdu_name, outfile)
        # data should be identical
        np.testing.assert_array_equal(fixed_hdu_data, hdu.data)
        # and headers too!
        self.assertEqual(fixed_hdu_head, hdu.header)

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_convertImgToJyPixel_UnitsUnknown(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bunit='counts')
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)
        self.assertEqual(self.utils.convertImgToJyPixel(
            infile, outfile), -1)
        assert mock_read.called
        assert not mock_write.called

    @patch('utils.os')
    @patch('utils.montage')
    def test_makeMosaic_Success(self, mock_montage, mock_os):
        outfile = '/out/mosaic.fits'
        input_tbl = '/tmp/input_tbl.txt'

        # setup montage methods
        # mImgTbl output http://montage.ipac.caltech.edu/docs/mImgtbl.html
        def mImgtbl_ret(): return 0
        mImgtbl_ret.stat = 'OK'
        mImgtbl_ret.count = 5
        mImgtbl_ret.badfits = 0
        mock_montage.mImgtbl.return_value = mImgtbl_ret

        self.assertEqual(self.utils.makeMosaic(input_tbl, outfile),  0)
        assert mock_montage.mImgtbl.called
        assert mock_montage.mAdd.called
        assert mock_montage.mConvert.called

    @patch('utils.os')
    @patch('utils.montage')
    def test_makeMosaic_Success(self, mock_montage, mock_os):
        outfile = '/out/mosaic.fits'
        input_tbl = '/tmp/input_tbl.txt'

        # setup montage methods
        # mImgTbl output http://montage.ipac.caltech.edu/docs/mImgtbl.html
        def mImgtbl_ret(): return 0
        mImgtbl_ret.stat = 'OK'
        mImgtbl_ret.count = 5
        mImgtbl_ret.badfits = 0
        mock_montage.mImgtbl.return_value = mImgtbl_ret

        self.assertEqual(self.utils.makeMosaic(input_tbl, outfile),  0)
        assert mock_montage.mImgtbl.called
        assert mock_montage.mAdd.called
        assert mock_montage.mConvert.called

    @patch('utils.os')
    @patch('utils.montage')
    def test_makeMosaic_Success_BackgroundMatchNotOverlapping(self, mock_montage, mock_os):
        outfile = '/out/mosaic.fits'
        input_tbl = '/tmp/input_tbl.txt'

        # setup montage methods
        # mImgTbl output http://montage.ipac.caltech.edu/docs/mImgtbl.html
        def mImgtbl_ret(): return 0
        mImgtbl_ret.stat = 'OK'
        mImgtbl_ret.count = 5
        mImgtbl_ret.badfits = 0
        mock_montage.mImgtbl.return_value = mImgtbl_ret

        # mImgTbl output http://montage.ipac.caltech.edu/docs/mOverlaps.html
        def mOverlaps_ret(): return 0
        mOverlaps_ret.stat = 'OK'
        mOverlaps_ret.count = 0
        mock_montage.mOverlaps.return_value = mOverlaps_ret

        self.assertEqual(self.utils.makeMosaic(
            input_tbl, outfile, background_match=True),  0)
        assert mock_montage.mImgtbl.called
        assert mock_montage.mAdd.called
        assert mock_montage.mConvert.called

    @patch('utils.os')
    @patch('utils.montage')
    def test_makeMosaic_Success_BackgroundMatchNotImplemented(self, mock_montage, mock_os):
        outfile = '/out/mosaic.fits'
        input_tbl = '/tmp/input_tbl.txt'

        # setup montage methods
        # mImgTbl output http://montage.ipac.caltech.edu/docs/mImgtbl.html
        def mImgtbl_ret(): return 0
        mImgtbl_ret.stat = 'OK'
        mImgtbl_ret.count = 5
        mImgtbl_ret.badfits = 0
        mock_montage.mImgtbl.return_value = mImgtbl_ret

        # mImgTbl output http://montage.ipac.caltech.edu/docs/mOverlaps.html
        def mOverlaps_ret(): return 0
        mOverlaps_ret.stat = 'OK'
        mOverlaps_ret.count = 1
        mock_montage.mOverlaps.return_value = mOverlaps_ret

        with self.assertRaises(NotImplementedError):
            self.utils.makeMosaic(
                input_tbl, outfile, background_match=True)

    @patch('utils.os')
    @patch('utils.montage')
    def test_makeMosaic_NoImagesProjected(self, mock_montage, mock_os):
        outfile = '/out/mosaic.fits'
        input_tbl = '/tmp/input_tbl.txt'

        # setup montage methods
        # mImgTbl output http://montage.ipac.caltech.edu/docs/mImgtbl.html
        def mImgtbl_ret(): return 0
        mImgtbl_ret.stat = 'OK'
        mImgtbl_ret.count = 0
        mImgtbl_ret.badfits = 10
        mock_montage.mImgtbl.return_value = mImgtbl_ret

        self.assertEqual(self.utils.makeMosaic(input_tbl, outfile),  -1)
        assert mock_montage.mImgtbl.called
        assert not mock_montage.mAdd.called
        assert not mock_montage.mConvert.called

    @patch('utils.fits.HDUList.writeto', side_effect=Exception())
    def test_write_fits(self, mockWrite):

        hdu = self._createDummyFITS()
        filename = 'test.fits'
        with self.assertRaises(Exception):
            utils.write_fits(None, None)

    @patch('utils.fits.open')
    def test_read_fits_Input2D(self, mock_read):
        hdu = self._createDummyFITS()

        mock_read.return_value = fits.HDUList([hdu])
        data, header = self.utils.read_fits('test.fits')
        assert mock_read.called
        self.assertIsNotNone(data)
        self.assertEqual(data.shape, (512, 512))

    @patch('utils.fits.open')
    def test_read_fits_Input4DFits(self, mock_read):
        hdu = self._createDummyFITS(ndim=4)

        mock_read.return_value = fits.HDUList([hdu])
        data, header = self.utils.read_fits('test.fits')
        assert mock_read.called
        self.assertIsNotNone(data)
        self.assertEqual(data.ndim, 2)
        self.assertEqual(data.shape, (512, 512))

    @patch('utils.fits.open')
    def test_read_fits_InputInvalidChannels(self, mock_read):
        hdu = self._createDummyFITS(ndim=5)

        mock_read.return_value = fits.HDUList([hdu])

        with self.assertRaises(IOError):
            self.utils.read_fits('test.fits')

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_cropImage_BasicWorldUnits(self, mock_read, mock_write):
        hdu = self._createDummyFITS()
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)

        # crop size 1 arcmin == 10 pixels
        self.assertEqual(self.utils.cropImage(
            filename=infile, ra=0, dec=0, crop_size=1*u.arcmin, outfile=outfile), 0)
        assert mock_read.called
        assert mock_write.called
        crop_hdu = mock_write.call_args[0]
        crop_hdu_data = crop_hdu[0]
        crop_hdu_name = crop_hdu[1]
        self.assertEqual(crop_hdu_name, outfile)
        self.assertEqual(crop_hdu_data.shape, (10, 10))

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_cropImage_BasicPixelUnits(self, mock_read, mock_write):
        hdu = self._createDummyFITS()
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)

        # crop size 10 pixels == 1 arcmin
        self.assertEqual(self.utils.cropImage(
            filename=infile, ra=0, dec=0, crop_size=10, outfile=outfile), 0)
        assert mock_read.called
        assert mock_write.called
        crop_hdu = mock_write.call_args[0]
        crop_hdu_data = crop_hdu[0]
        crop_hdu_name = crop_hdu[1]
        self.assertEqual(crop_hdu_name, outfile)
        self.assertEqual(crop_hdu_data.shape, (10, 10))

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_cropImage_CropLargerThanImage(self, mock_read, mock_write):
        hdu = self._createDummyFITS()
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)

        # crop size 10% larger than image size
        self.assertEqual(self.utils.cropImage(
            filename=infile, ra=0, dec=0, crop_size=1.1*hdu.data.shape[0], outfile=outfile, nanfill=False), 0)
        assert mock_read.called
        assert mock_write.called
        crop_hdu = mock_write.call_args[0]
        crop_hdu_data = crop_hdu[0]
        crop_hdu_name = crop_hdu[1]
        self.assertEqual(crop_hdu_name, outfile)
        self.assertGreater(crop_hdu_data.shape, hdu.data.shape)
        assert np.isnan(crop_hdu_data).any()    # should contain NaNs

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_cropImage_CropLargerThanImage_FillWithValue(self, mock_read, mock_write):
        hdu = self._createDummyFITS()
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)

        # crop size 10% larger than image size
        self.assertEqual(self.utils.cropImage(
            filename=infile, ra=0, dec=0, crop_size=1.1*hdu.data.shape[0], outfile=outfile, nanfill=True, nanfill_mode='', nanfill_val=999), 0)
        assert mock_read.called
        assert mock_write.called
        crop_hdu = mock_write.call_args[0]
        crop_hdu_data = crop_hdu[0]
        crop_hdu_name = crop_hdu[1]
        self.assertEqual(crop_hdu_name, outfile)
        self.assertGreater(crop_hdu_data.shape, hdu.data.shape)
        assert not np.isnan(crop_hdu_data).any()    # should NOT contain NaNs
        assert np.isin(999, crop_hdu_data).any()    # but fillval instead

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_cropImage_CropLargerThanImage_FillWithMin(self, mock_read, mock_write):
        hdu = self._createDummyFITS(bkg_std=0)  # constant image
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)

        # crop size 10% larger than image size
        self.assertEqual(self.utils.cropImage(
            filename=infile, ra=0, dec=0, crop_size=1.1*hdu.data.shape[0], outfile=outfile, nanfill=True, nanfill_mode='imgmin', nanfill_val=999), 0)
        assert mock_read.called
        assert mock_write.called
        crop_hdu = mock_write.call_args[0]
        crop_hdu_data = crop_hdu[0]
        crop_hdu_name = crop_hdu[1]
        self.assertEqual(crop_hdu_name, outfile)
        self.assertGreater(crop_hdu_data.shape, hdu.data.shape)
        assert not np.isnan(crop_hdu_data).any()  # should NOT contain NaNs
        # all values = 0, so min = 0 (fill value ignored)
        assert np.isin(0, crop_hdu_data).all()

    @patch('utils.Utils.write_fits')
    @patch('utils.Utils.read_fits')
    def test_cropImage_CropLargerThanSourceSize(self, mock_read, mock_write):
        hdu = self._createDummyFITS()
        infile = 'test_in.fits'
        outfile = 'test_out.fits'

        mock_read.return_value = (hdu.data, hdu.header)

        self.assertEqual(self.utils.cropImage(
            filename=infile, ra=0, dec=0, crop_size=10, source_size=20, outfile=outfile, nanfill=False), -1)
        assert mock_read.called
        assert not mock_write.called

    @patch('utils.fits.open')
    def test_estimateBkgFromAnnulus_PositiveBkg(self, mock_read):
        bkg = 1.0
        hdu = self._createDummyFITS(size=512, bkg_mean=bkg)

        mock_read.return_value = fits.HDUList([hdu])

        # using sigma clip
        bkg_annulus = self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 12, 24, method='sigmaclip')
        self.assertGreater(bkg_annulus, 0)
        self.assertAlmostEqual(bkg_annulus, bkg, places=0)

        # using median
        bkg_annulus = self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 12, 24, method='median')
        self.assertGreater(bkg_annulus, 0)
        self.assertAlmostEqual(bkg_annulus, bkg, places=0)

        assert mock_read.called

    @patch('utils.fits.open')
    def test_estimateBkgFromAnnulus_NegativeBkg(self, mock_read):
        bkg = -1.0
        hdu = self._createDummyFITS(size=512, bkg_mean=bkg)

        mock_read.return_value = fits.HDUList([hdu])

        bkg_annulus = self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 12, 24, method='sigmaclip')
        self.assertLess(bkg_annulus, 0)
        self.assertAlmostEqual(bkg_annulus, bkg, places=0)

        # using median
        bkg_annulus = self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 12, 24, method='median')
        self.assertLess(bkg_annulus, 0)
        self.assertAlmostEqual(bkg_annulus, bkg, places=0)

        mock_read.assert_called()

    @patch('utils.fits.open')
    def test_estimateBkgFromAnnulus_WithSource(self, mock_read):
        bkg = 1.0
        src = 5.0   # src brigthness
        hdu = self._createDummyFITS(size=512, bkg_mean=bkg)

        # simulate extended src of 12x12 px
        sou_size = 6
        hdu.data[250:262, 250:262] = src
        mock_read.return_value = fits.HDUList([hdu])
        self.assertAlmostEqual(self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 12, 24), src, places=0)  # annulus within src
        self.assertAlmostEqual(self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 42, 48), bkg, places=0)  # annulus outside src
        mock_read.assert_called()

    @patch('utils.fits.open')
    def test_estimateBkgFromAnnulus_WithSourceAndLargeRms(self, mock_read):
        bkg = 1.0
        src = 5.0   # src brigthness

        # highly variable background (up to 80% of srcbrigthness)
        hdu = self._createDummyFITS(size=512, bkg_mean=bkg, bkg_std=0.8*src)

        # simulate extended src of 12x12 px
        sou_size = 6
        hdu.data[250:262, 250:262] = 5.0

        # TODO: improve testing (e.g. annulus overlapping w/ src, etc)
        mock_read.return_value = fits.HDUList([hdu])
        self.assertAlmostEqual(self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 12, 24), 5.0, places=0)  # annulus within src
        self.assertLess(self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 42, 48), src)       # annulus outside src
        mock_read.assert_called()

    @patch('utils.fits.open')
    def test_estimateBkgFromAnnulus_OutOfBounds(self, mock_read):
        bkg = 1.0
        hdu = self._createDummyFITS(size=512, bkg_mean=bkg)
        mock_read.return_value = fits.HDUList([hdu])
        self.assertEqual(self.utils.estimateBkgFromAnnulus(
            'test.fits', 1, 1, 12, 24), 0)     # Out of bounds => all pixels masked
        mock_read.assert_called()

    @patch('utils.fits.open')
    def test_estimateBkgFromAnnulus_UnknownMethod(self, mock_read):
        bkg = 1.0
        hdu = self._createDummyFITS(size=512, bkg_mean=bkg)
        mock_read.return_value = fits.HDUList([hdu])
        self.assertEqual(self.utils.estimateBkgFromAnnulus(
            'test.fits', 0, 0, 12, 24, method='unknown'), -1)
        mock_read.assert_called()
