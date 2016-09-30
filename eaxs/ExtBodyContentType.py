#############################################################
# 2016-09-26: ExtBodyContentType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of ExtBodyContentType
##############################################################

from eaxs.HashType import Hash
from xml_help.CommonMethods import CommonMethods
import uuid
import os
from eaxs.eaxs_helpers.Render import Render
from collections import OrderedDict
import codecs

class ExtBodyContent:
    """"""

    def __init__(self):
        """Constructor for ExtBodyContent"""
        self.attachment_folder = CommonMethods.get_attachment_directory()
        self.attachment_directory = os.path.join(CommonMethods.get_base_path(), self.attachment_folder)
        self.rel_path = None  # type: str
        self.char_set = None  # type: str
        self.transfer_encoding = None  # type: str
        self.local_id = None  # type: int
        self.xml_wrapped = True  # type: bool
        self.eol = None  # type: Eol
        self.hash = None  # type: Hash
        self.body_content = None  # type: str
        self.gid = uuid.uuid4()  # type: uuid

    def set_hash(self, hdigest, ht='SHA1'):
        self.hash = Hash(hdigest, ht)

    def write_ext_body(self, xml):
        if self.xml_wrapped:
            try:
                fn = '{}{}'.format(self.gid, '.xml')
                fh = codecs.open(os.path.join(self.attachment_directory, fn), "w", "utf-8")
                fh.write(xml)
                fh.close()
            except UnicodeDecodeError as e:
                print(e)
            except UnicodeEncodeError as e:
                print(e)

    def build_xml_file(self, children):
        """
        :type children : OrderedDict
        :param children:
        :return:
        """
        chillen = OrderedDict()
        chillen["LocalUniqueID"] = self.gid.__str__()
        for k, v in children.items():
            chillen[k] = v
        chillen["Content"] = self.body_content
        rend = Render("ExternalBodyPart", chillen)
        self.write_ext_body(rend.render())
        self.body_content = None




