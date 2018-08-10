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


# set global path and validator.
HERE = os.path.dirname(__file__)
VALIDATOR = None


def VALIDATE_EAXS(account_id, sample_data, is_eml=False):
    """ Creates a temporary EAXS with name @account_id using @sample_data.
    
    Returns:
        tuple: The return value.
        The first item is a boolean that is True if the EAXS is valid. 
        The second item is the EAXS file as an lxml.etree._Element. 
    """

    # set XSD data and prevent repeat http requests.
    global VALIDATOR    
    if VALIDATOR is None:
        xsd_path = "https://raw.githubusercontent.com/StateArchivesOfNorthCarolina/tomes-eaxs/master/versions/1/eaxs_schema_v1.xsd"
        xsd = requests.get(xsd_path).text.encode()
        xsd_el = etree.fromstring(xsd)
        VALIDATOR = etree.XMLSchema(xsd_el)
        
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
    return (is_valid, eaxs_el)


class Test_DarcMail(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.here = HERE
        self.validate_eaxs = VALIDATE_EAXS
        self.sample_mbox = os.path.join(self.here, "sample_files", "mbox")
        self.sample_eml = os.path.join(self.here, "sample_files", "eml")


    def test__mbox(self):
        """ Does the sample MBOX yield a valid EAXS? """
        
        is_valid, eaxs_el = self.validate_eaxs("sample_mbox", self.sample_mbox) 
        self.assertTrue(is_valid)
  

    def test__eml(self):
        """ Does the sample EML yield a valid EAXS? """

        is_valid, eaxs_el = self.validate_eaxs("sample_eml", self.sample_eml, is_eml=True) 
        self.assertTrue(is_valid)


# CLI.
def main(account_path: "email account path", 
        from_eml: ("toggle EML processing", "flag", "fe")):
    
    "Creates an EAXS account and prints basic account statistics.\
    \nexample: `python3 test__darcmail sample_files/mbox`\
    \n\nWARNING: Only use this with *small* MBOX|EML data (< 100 messages)."

    # creates EAXS.
    is_valid, eaxs_el = VALIDATE_EAXS("sample", account_path, is_eml=from_eml)
    
    # get folder and message statistics.
    folders = eaxs_el.xpath("//*[local-name()='Folder']")
    messages = eaxs_el.xpath("//*[local-name()='Message']")
    
    # report statistics.
    stats = "EAXS has {} total folders with {} total messages.".format(len(folders), 
            len(messages))
    print(stats)

    
if __name__ == "__main__":
    plac.call(main)
