#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import logging
import os
import plac
import requests
import tempfile
import unittest
from lxml import etree
from tomes_darcmail.darcmail import DarcMail

# enable logging.
logging.basicConfig(level=logging.DEBUG)


# set path and XSD data.
HERE = os.path.dirname(__file__)
XSD_PATH = "https://raw.githubusercontent.com/StateArchivesOfNorthCarolina/tomes-eaxs/master/versions/1/eaxs_schema_v1.xsd"
XSD = requests.get(XSD_PATH).text.encode()
XSD_EL = etree.fromstring(XSD)
VALIDATOR = etree.XMLSchema(XSD_EL)


def VALIDATE_EAXS(account_id, sample_data, is_eml=False):
    """ Creates a temporary EAXS with name @account_id using @sample_data.
    
    Returns:
        bool: The return value.
        True if the EAXS is valid per @XSD_PATH. Otherwise, False. """

    # create temporary folder.
    temp_dir = tempfile.TemporaryDirectory(dir=HERE)
    
    # make the EAXS.
    logging.info("Creating EAXS at: {}".format(temp_dir.name))       
    darcmail = DarcMail(account_id, sample_data, temp_dir.name, from_eml=is_eml)
    darcmail.create_eaxs()
    eaxs = os.path.join(temp_dir.name, "eaxs", account_id, "eaxs_xml", "{}.xml".format(
        account_id))
    
    # validate EAXS.
    logging.info("Validating EAXS at: {}".format(eaxs))
    eaxs_el = etree.parse(eaxs)
    is_valid = VALIDATOR.validate(eaxs_el)

    temp_dir.cleanup()
    logging.info("XML validation yielded: {}".format(is_valid))
    return is_valid


class Test_DarcMail(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.here = HERE 
        self.sample_mbox = os.path.join(self.here, "sample_files", "mbox")
        self.sample_eml = os.path.join(self.here, "sample_files", "eml")
        self.xsd_path = XSD_PATH
        self.xsd = XSD
        self.xsd_el = XSD_EL
        self.validator = VALIDATOR
        self._validate_EAXS = VALIDATE_EAXS


    def test__mbox(self):
        """ Does the sample MBOX yield a valid EAXS? """
        
        is_valid = self._validate_EAXS("sample_mbox", self.sample_mbox) 
        self.assertTrue(is_valid)
  

    def test__eml(self):
        """ Does the sample EML yield a valid EAXS? """

        is_valid = self._validate_EAXS("sample_eml", self.sample_eml, is_eml=True) 
        self.assertTrue(is_valid)


# CLI.
def main(account_path: "email account path", 
        from_eml: ("toggle EML processing", "flag", "fe")):
    
    "Creates and validates an EAXS account.\
    \nWARNING: Only use this with *small* MBOX|EML data (< 100 messages).\
    \nexample: `python3 test__darcmail sample_files/mbox`"

    # creates EAXS.
    is_valid = VALIDATE_EAXS("sample", account_path, is_eml=from_eml)
    print(is_valid)


if __name__ == "__main__":
    plac.call(main)
