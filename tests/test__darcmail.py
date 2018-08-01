#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import hashlib
import logging
import os
import random
import requests
import shutil
import subprocess
import time
import unittest
from lxml import etree
from tomes_darcmail.darcmail import DarcMail

# enable logging.
logging.basicConfig(level=logging.DEBUG)


# load EAXS XSD.
XSD = requests.get("https://raw.githubusercontent.com/StateArchivesOfNorthCarolina/tomes-eaxs/master/versions/1/eaxs_schema_v1.xsd").text.encode()


# generate random folder name based on SHA-256 hash of time plus a random number.
def MAKE_DIRNAME():
    _dirname = "{}{}".format(time.time(), random.random())
    sha256 = hashlib.sha256()
    sha256.update(_dirname.encode())
    dirname = "_" + sha256.hexdigest()[:10]
    return dirname


class Test_DarcMail(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.sample_mbox = "sample_files/mbox"
        self.sample_eml = "sample_files/eml"
        self.make_dirname = MAKE_DIRNAME
        self.xsd = XSD
        self.validator = etree.XMLSchema(etree.fromstring(self.xsd))


    def test__mbox(self):
        """ Is the EAXS from the sample MBOX valid? """
        
        # create account ID and temporary dirname.
        account_id = "sample"
        dirname = self.make_dirname()
        
        # make the EAXS.
        darcmail = DarcMail(account_id, self.sample_mbox, dirname)
        darcmail.create_eaxs()
        eaxs = os.path.join(dirname, "eaxs", account_id, "eaxs_xml", "{}.xml".format(
            account_id))
        logging.info("Created EAXS file: {}".format(eaxs))
        
        # validate EAXS.
        eaxs_el = etree.parse(eaxs)
        is_valid = self.validator.validate(eaxs_el)

        # delete temp output.
        try:
            pass#???shutil.rmtree(dirname)
        except Exception as err:
            logging.warning("Can't delete temporary folder: {}".format(dirname))
            logging.error(err)

        self.assertTrue(is_valid)
        

    def QUest__eml(self):
        """ Is the EAXS from the sample EML valid? """

        # create temporary dirname.
        dirname = self.make_dirname()
        eaxs_path = self.normalize_path("../OUTPUT", "eaxs", dirname)
        eaxs = self.normalize_path(eaxs_path, "eaxs_xml", "{}.xml".format(dirname))
        
        # make the EAXS and validate it.
        result = self.run_darcmail(dirname, self.sample_eml, True)
        if not result:
            test = False
        else:
            eaxs = etree.parse(eaxs)
            test = self.validator.validate(eaxs)

        # delete temp output.
        try:
            shutil.rmtree(eaxs_path)
        except Exception as err:
            logging.warning("Can't delete folder: {}".format(eaxs_path))
            logging.error(err)

        self.assertTrue(test)


if __name__ == "__main__":
    pass #???
