#!/usr/bin/env python3

# import modules.
import logging
import os
import requests
import unittest
from lxml import etree

# enable logging.
logging.basicConfig(level=logging.DEBUG)


# load EAXS XSD.
XSD = requests.get("https://raw.githubusercontent.com/StateArchivesOfNorthCarolina/tomes-eaxs/master/eaxs_schema.xsd").text.encode()


class Test_DarcMailCLI(unittest.TestCase):


    def setUp(self):

        # set attributes.
        self.sample_folder = "sample_files"
        self.xsd = XSD
        self.validator = etree.XMLSchema(etree.fromstring(self.xsd))


    def test__mbox(self):
        """ ??? """
        
        s = etree.parse("../OUTPUT/eaxs/sampleml/eaxs_xml/sampleml.xml_LID_0.xml")
        return self.validator.validate(s)
        

    def test__eml(self):
        """ ??? """

        return True
