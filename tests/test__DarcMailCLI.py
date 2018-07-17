#!/usr/bin/env python3

# import modules.
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

# enable logging.
logging.basicConfig(level=logging.DEBUG)


# load EAXS XSD.
XSD = requests.get("https://raw.githubusercontent.com/StateArchivesOfNorthCarolina/tomes-eaxs/master/eaxs_schema.xsd").text.encode()


# generate random folder name based on SHA-256 hash of time plus a random number.
def MAKE_DIRNAME():
    _dirname = "{}{}".format(time.time(), random.random())
    sha256 = hashlib.sha256()
    sha256.update(_dirname.encode())
    dirname = sha256.hexdigest()[:10]
    return dirname


# function to run DarcMailCLI.
def RUN_DARCMAIL(dirname, source, eml=False):
    
    # add "./" before the command if not Windows.
    slash = ""
    if os.name != "nt":
        slash = "./"

    # construct the command; run it.
    cmd = "{}DarcMailCLI.py -a {} -d {} -c 100 -st".format(slash, dirname, source)
    if eml:
        cmd += " -fe"
    try:
        logging.info("Running: {}".format(cmd))
        a = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                check=True, cwd="../", shell=True)
        return True
    except subprocess.CalledProcessError as err:
        logging.error(err)
        return False


class Test_DarcMailCLI(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.sample_mbox = "tests/sample_files/mbox"
        self.sample_eml = "tests/sample_files/eml"
        self.make_dirname = MAKE_DIRNAME
        self.run_darcmail = RUN_DARCMAIL
        self.xsd = XSD
        self.validator = etree.XMLSchema(etree.fromstring(self.xsd))
        self.normalize_path = lambda *p: os.path.normpath(os.path.join(*p)).replace("\\", "/")


    def test__mbox(self):
        """ Is the EAXS from the sample MBOX valid? """
        
        # create temporary dirname.
        dirname = self.make_dirname()
        eaxs_path = self.normalize_path("../OUTPUT", "eaxs", dirname)
        eaxs = self.normalize_path(eaxs_path, "eaxs_xml", "{}.xml".format(dirname))
        
        # make the EAXS and validate it.
        result = self.run_darcmail(dirname, self.sample_mbox)
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
        

    def test__eml(self):
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
