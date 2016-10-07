#############################################################
# 2016-09-26: SingleBodyType.py 
# Author: Jeremy M. Gibson (State Archives of North Carolina)
# 
# Description: 
##############################################################

from eaxs.HeaderType import Header
from eaxs.ChildMessageType import ChildMessage
from eaxs.ParameterType import Parameter
from eaxs.IntBodyContentType import IntBodyContent
from eaxs.ExtBodyContentType import ExtBodyContent
from email.message import Message
from xml_help.CommonMethods import CommonMethods
from urllib.parse import unquote
import logging
from lxml.ElementInclude import etree
from collections import OrderedDict


class SingleBody:
    """"""
    
    def __init__(self, payload):
        """Constructor for SingleBody
        :type payload : Message
        """
        self.payload = payload
        self.content_type = None  # type: str
        self.charset = None  # type: str
        self.content_name = None  # type: str
        self.content_type_comments = None  # type: str
        self.content_type_param = None  # type: list[Parameter]
        self.transfer_encoding = None  # type: str
        self.transfer_encoding_comments = None  # type: str
        self.content_id = None  # type: str
        self.content_id_comments = None  # type: str
        self.description = None  # type: str
        self.description_comments = None  # type: str
        self.disposition = None  # type: str
        self.disposition_file_name = None  # type: str
        self.disposition_comments = None  # type: str
        self.disposition_params = None  # type: list[Parameter]
        self.other_mime_header = None  # type: list[Header]
        self.body_content = None  # type: IntBodyContent
        self.ext_body_content = []  # type: list[ExtBodyContent]
        self.child_message = None  # type: ChildMessage
        self.phantom_body = None  # type: str

        self.append_body = True
        self.logger = logging.getLogger()
        self.sb_map = OrderedDict([
            ("content_type", "ContentType"),
            ("charset", "Charset"),
            ("content_name", "ContentName"),
            ("content_type_comments", "ContentTypeComments"),
            ("content_type_param", "ContentTypeParam"),
            ("transfer_encoding", "TransferEncoding"),
            ("transfer_encoding_comments", "TransferEncodingComments"),
            ("content_id", "ContentId"),
            ("content_id_comments", "ContentIdComments"),
            ("description", "Description"),
            ("description_comments", "DescriptionComments"),
            ("disposition", "Disposition"),
            ("disposition_file_name", "DispositionFileName"),
            ("disposition_comments", "DispositionComments"),
            ("disposition_params", "DispositionParams"),
            ("other_mime_header", "OtherMimeHeader"),
            ("body_content", "BodyContent"),
            ("ext_body_content", "ExtBodyContent"),
            ("child_message", "ChildMessage"),
            ("phantom_body", "Phantom_Body")
        ])

    def process_headers(self):
        for header, value in self.payload.items():

            if header == "Content-Type":
                expression = CommonMethods.get_content_type(value)
                if len(expression) > 1:
                    self.content_type = expression[0]
                    self.charset = expression[2]
                    # self.logger.info('Captured {} : {}'.format(header, value))
                    continue
                else:
                    self.content_type = expression[0]
                    continue
            if header == "Content-Transfer-Encoding":
                self.transfer_encoding = value
                continue
            if header == "Content-Disposition":
                try:
                    self.disposition = value.split(";")[0]
                    fn = value.split(";")[1].split("=")[1]
                    if len(fn.split("''")) > 1:
                        self.disposition_file_name = unquote(fn.split("''")[1])
                    else:
                        self.disposition_file_name = unquote(fn)
                    continue
                except IndexError as e:
                    self.logger.error("{}: {}".format(e, value))
            self.logger.info('Not Captured {} : {}'.format(header, value))

    def process_body(self):
        if not self.content_type.__contains__("plain"):
            if self._store_body():
                extbody = ExtBodyContent()
                extbody.char_set = self.charset
                extbody.local_id = CommonMethods.increment_local_id()
                extbody.transfer_encoding = self.transfer_encoding
                extbody.eol = CommonMethods.get_eol(self.payload.get_payload())
                extbody.hash = CommonMethods.get_hash(self.payload.as_bytes())
                extbody.body_content = self.payload.get_payload()
                children = OrderedDict({"ContentType": self.content_type,
                            "Disposition": self.disposition,
                            "DispositionFileName": self.disposition_file_name,
                            "ContentTransferEncoding": self.transfer_encoding})
                extbody.build_xml_file(children)
                self.ext_body_content.append(extbody)
                self.payload = None
        else:
            self.body_content = CommonMethods.cdata_wrap(self.payload.get_payload())
            self.payload = None

    def _store_body(self):
        if self.disposition_file_name != "rtf-body.rtf":
            return True
        elif not CommonMethods.store_rtf_body():
            self.disposition_comments = "Attachment is duplicate of BodyContent: Not saved"
            return False
        return True

    def get_attributes(self):
       pass

    def render(self, parent):
        """
        :type parent: xml.etree.ElementTree.Element
        :param parent:
        :return:
        """
        single_child_head = etree.SubElement(parent, "SingleBody")
        for key, value in self.sb_map.items():
            if self.__getattribute__(key) is not None:
                if isinstance(self.__getattribute__(key), list):
                    if len(self.__getattribute__(key)) == 0:
                        continue
                    if isinstance(self.__getattribute__(key)[0], ExtBodyContent):
                        for ebc in self.ext_body_content:
                            ebc.render(single_child_head)
                        continue
                    continue

                child = etree.SubElement(single_child_head, value)
                child.text = self.__getattribute__(key)
