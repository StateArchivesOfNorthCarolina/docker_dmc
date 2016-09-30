#############################################################
# 2016-09-22: Account.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: The parent for the xml representation of a an
# account.  Based on the E-Mail Account XML Schema
##############################################################

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring
from xml.dom import minidom
from eaxs.FolderType import Folder


class Account(object):
    """"""
    
    def __init__(self, account_name):
        """Constructor for Account"""
        self.email_address = []
        self.global_id = account_name  # type: str
        self.reference_account = []  # type: list[ReferenceAccount]
        self.folders = []  # type: list[Folder]

    def add_folder(self, name, filename, relpath):
        fold = Folder(name, filename, relpath)
        self.folders.append(fold)

    def get_folder(self, ind):
        pass

    def build_account_element(self):
        account = Element("Account", self.get_root_element_attributes())
        rough = tostring(account, 'utf-8')
        reparsed = minidom.parseString(rough)
        print(reparsed.toprettyxml(indent="  "))

    @staticmethod
    def get_root_element_attributes():
        return {
            "xmlns": "http://www.archives.ncdcr.gov/mail-account",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://www.history.ncdcr.gov/SHRAB/ar/emailpreservation/mail-account/mail-account.xsd"
        }
