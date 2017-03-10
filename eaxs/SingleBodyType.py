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
from email.charset import Charset
from xml_help.CommonMethods import CommonMethods
from urllib.parse import unquote
from lxml.ElementInclude import etree
from collections import OrderedDict
import logging
import re
from bs4 import BeautifulSoup as bsoup


class SingleBody:
    """

    """
    
    def __init__(self, payload=None):
        """Constructor for SingleBody
        :type payload : Message
        """
        if payload is not None:
            self.payload = payload
            self.content_type = self.payload.get_content_type()  # type: str
            self.charset = self.payload.get_content_charset()  # type: str
            self.transfer_encoding = self.payload.get("Content-Transfer-Encoding")  # type: str
            self.content_id = self.payload.get("Content-ID")  # type: str
            self.disposition = self.payload.get_content_disposition()  # type: str
        else:
            self.payload = payload
            self.content_type = None  # type: str
            self.charset = None  # type: str
            self.transfer_encoding = None # type: str
            self.content_id = None  # type: str
            self.disposition = None  # type: str

        self.content_name = None  # type: str
        self.content_type_comments = None  # type: str
        self.content_type_param = []  # type: list[Parameter]
        self.transfer_encoding_comments = None  # type: str
        self.content_id_comments = None  # type: str
        self.description = None  # type: str
        self.description_comments = None  # type: str
        self.disposition_file_name = None  # type: str
        self.disposition_comments = None  # type: str
        self.disposition_params = []  # type: list[Parameter]
        self.other_mime_header = []  # type: list[Header]
        self.body_content = []  # type: list[IntBodyContent]
        self.ext_body_content = []  # type: list[ExtBodyContent]
        self.child_message = None  # type: ChildMessage
        self.phantom_body = None  # type: str
        self.append_body = True
        self.logger = logging.getLogger("SingleBodyType")
        self.body_only = False
        self.soupify = False
        self.body_content_duplicate = False

    def process_headers(self):
        if isinstance(self.payload, str):
            self.body_content = self.payload
            self.body_only = True
            return

        for header, value in self.payload.items():

            if header == "Content-Type":
                expression = CommonMethods.get_content_type(value)
                if len(expression) > 1:
                    self.content_type = expression[0]
                    # Is this a charset identification
                    if expression[1] == 'charset':
                        self.charset = expression[2]
                    else:
                        self.content_type_param.append(Parameter(expression[1], expression[2]))
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
                    self.other_mime_header.append(Header(header, value))

            if header == "Content-ID":
                self.content_id = CommonMethods.cdata_wrap(value)
                continue

            if header == "Content-Description":
                self.content_name = value
                continue

            self.other_mime_header.append(Header(header, value))

    def process_body(self):
        if not self._is_readable():
            # Content-type indicates this message not readable
            # Next check to see if we should store the body externally or discard because of
            # Duplication

            if not self._store_body():
                return
            if self.payload is not None:
                self._full_ext_body()
            else:
                self._simple_ext_body()
        else:
            # This is a plaintext BodyContent block
            # Strip HTML from the block and escape with cdata if necessary
            if self.body_only is False:
                self._process_plaintext_body()
            else:
                try:
                    self.body_content.append(IntBodyContent(CommonMethods.cdata_wrap(self.body_content),
                                                            self.transfer_encoding, self.charset))
                except AttributeError as e:
                    # This message is completely empty
                    self.body_content = []

    def _full_ext_body(self):
        extbody = ExtBodyContent()
        extbody.char_set = self.charset
        extbody.local_id = CommonMethods.increment_local_id()
        extbody.transfer_encoding = self.transfer_encoding
        extbody.eol = CommonMethods.get_eol(self.payload.get_payload())
        extbody.hash = CommonMethods.get_hash(self.payload.as_bytes())
        extbody.body_content = self.payload.get_payload()
        children = OrderedDict({
            "ContentType": self.content_type,
            "Disposition": self.disposition,
            "DispositionFileName": self.disposition_file_name,
            "ContentTransferEncoding": self.transfer_encoding
        })
        extbody.build_xml_file(children)
        self.ext_body_content.append(extbody)
        self.payload = None

    def _simple_ext_body(self):
        extbody = ExtBodyContent()
        extbody.local_id = CommonMethods.increment_local_id()
        extbody.transfer_encoding = self.transfer_encoding
        extbody.hash = CommonMethods.get_hash(bytes(self.body_content, encoding='utf-8'))
        children = OrderedDict({
            "ContentType": self.content_type,
            "Disposition": self.disposition,
            "DispositionFileName": self.disposition_file_name,
            "ContentTransferEncoding": self.transfer_encoding
        })
        extbody.build_xml_file(children)
        self.ext_body_content.append(extbody)
        self.payload = None
        self.body_content = None

    def _process_plaintext_body(self):
        t = ""
        if isinstance(self.payload, Message):
            t = re.sub("\[\[", "\\[\\[", self._soupify(self.payload.get_payload()))
            t = re.sub("]]", "\]\]", t)
        elif isinstance(self.payload, str):
            t = re.sub("\[\[", "\\[\\[", self._soupify(self.payload))
            t = re.sub("]]", "\]\]", t)

        try:
            self.body_content.append(IntBodyContent(CommonMethods.cdata_wrap(t), self.transfer_encoding, self.charset))
        except ValueError as ve:
            self.logger.error("{}".format(ve))
        self.payload = None

    def _store_body(self):
        # Checks to see if the ExtBody is a duplicate of the email body.
        # Remove and note in the ExtBody Disposition.
        if self.disposition_file_name != "rtf-body.rtf":
            return True
        if self.content_type.__contains__("richtext"):
            return True
        elif not CommonMethods.store_rtf_body():
            # Check to see if we have flagged to save body duplicates
            self.disposition_comments = "Attachment is duplicate of BodyContent: Not saved"
            return False
        return True

    def get_attributes(self):
       pass

    def _is_readable(self):
        if self.transfer_encoding == "base64":
            return False
        if self.content_type == "text/plain":
            return True
        if self.content_type == "text/html":
            return True
        if self.charset is not None:
            cs = Charset(self.charset)
        else:
            cs = Charset()
        if self.charset == "us-ascii":
            return True
        if cs.get_body_encoding() == "quoted-printable":
            return True
        if self.body_only:
            return True
        if self.charset is None:
            return False
        return False

    def _soupify(self, body):
        if not self.soupify:
            return body
        soup = bsoup(body, "lxml")
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        return text

    def render(self, parent):
        """
        :type parent: xml.etree.ElementTree.Element
        :param parent:
        :return:
        """
        single_child_head = etree.SubElement(parent, "SingleBody")
        for key, value in CommonMethods.get_singlebody_map().items():
            if self.__getattribute__(key) is not None:
                if isinstance(self.__getattribute__(key), list):
                    if len(self.__getattribute__(key)) == 0:
                        continue
                    if isinstance(self.__getattribute__(key)[0], ExtBodyContent):
                        for ebc in self.ext_body_content:
                            ebc.render(single_child_head)
                        continue
                    if isinstance(self.__getattribute__(key)[0], IntBodyContent):
                        for intb in self.body_content:
                            intb.render(single_child_head)
                        continue
                    continue
                child = etree.SubElement(single_child_head, value)
                try:
                    child.text = self.__getattribute__(key)
                except TypeError as e:
                    print()
