#############################################################
# 2016-09-22: HeaderType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of EAXS header-type
##############################################################
import re
from lxml.ElementInclude import etree
from xml_help.CommonMethods import CommonMethods


class Header:
    """"""

    def __init__(self, name, value, cdata=False):
        """Constructor for Header"""
        self.cdata = cdata
        self.name = name  # type: str
        self.value = CommonMethods.cdata_wrap(value)  # type: str

    def render(self, parent):
        """
         :type parent: xml.etree.ElementTree.Element
         :param parent:
         :return:
         """
        child = etree.SubElement(parent, "Header")
        child1 = etree.SubElement(child, "Name")
        child1.text = self.name
        child2 = etree.SubElement(child, "Value")
        child2.text = self.value

