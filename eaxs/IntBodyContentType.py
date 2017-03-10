#############################################################
# 2016-09-26: IntBodyContentType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of the int-body-content-type
##############################################################
from lxml.ElementInclude import etree


class IntBodyContent:
    """"""

    def __init__(self, content=None, transfer_encoding=None, char_set='utf-8'):
        """Constructor for """
        self.content = content  # type: str
        self.char_set = char_set  # type: str
        self.transfer_encoding = transfer_encoding  # type: str

    def render(self, parent):
        """
        :type parent: xml.etree.ElementTree.Element
        :param parent:
        :return:
        """
        int_bdy_head = etree.SubElement(parent, "BodyContent")
        child1 = etree.SubElement(int_bdy_head, "Content")
        child1.text = self.content
        child2 = etree.SubElement(int_bdy_head, "CharSet")
        child2.text = self.char_set
        child3 = etree.SubElement(int_bdy_head, "TransferEncoding")
        child3.text = self.transfer_encoding
