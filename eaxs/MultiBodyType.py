#############################################################
# 2016-09-26: MultiBodyType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
# 
# Description: implementation of the multibody type
##############################################################

from eaxs.SingleBodyType import SingleBody
from eaxs.HeaderType import Header
from eaxs.ParameterType import Parameter
from email.message import Message
from xml_help.CommonMethods import CommonMethods
from lxml.ElementInclude import etree
from collections import OrderedDict

class MultiBody:
    """"""
    
    def __init__(self, payload):
        """Constructor for MultiBody
        :type payload : email.message.Message
        """
        self.payload = payload  # type: Message
        self.content_type = None  # type: str
        self.charset = None  # type: str
        self.content_name = None  # type: str
        self.boundary_string = None  # type: str
        self.content_type_comments = None  # type: str
        self.content_type_param = None  # type: [Parameter]
        self.transfer_encoding = None  # type: str
        self.transfer_encoding_comments = None  # type: str
        self.content_id = None  # type: str
        self.content_id_comments = None  # type: str
        self.description = None  # type: str
        self.description_comments = None  # type: str
        self.disposition = None  # type: str
        self.disposition_file_name = None  # type: str
        self.disposition_comments = None  # type: str
        self.disposition_params = None  # type: [Parameter]
        self.other_mime_header = None  # type: [Header]
        self.preamble = None  # type: str
        self.single_bodies = []  # type: list[SingleBody]
        self.multi_bodies = []  # type: list[MultiBody]
        self.epilogue = None  # type: str

        self.multi_map = OrderedDict([
            ("content_type", "ContentType"),
            ("charset", "Charset"),
            ("content_name", "ContentName"),
            ("boundary_string", "BoundaryString"),
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
            ("disposition_params", "DispositionParam"),
            ("other_mime_header", "OtherMimeHeader"),
            ("preamble", "Preamble"),
            ("single_bodies", "SingleBody"),
            ("multi_bodies", "MultiBody"),
            ("epilogue", "Epilogue"),
        ])

    def process_headers(self):
        for header, value in self.payload.items():
            if header == "Content-Type":
                expression = CommonMethods.get_content_type(value)
                self.content_type = expression[0]
                self.boundary_string = expression[2]

    def render(self, parent):
        """
        :type parent: xml.etree.ElementTree.Element
        :param parent:
        :return:
        """
        multi_child_head = etree.SubElement(parent, "MultiBody")
        for key, value in self.multi_map.items():
            if self.__getattribute__(key) is not None:
                if isinstance(self.__getattribute__(key), list):
                    # TODO: Handle this
                    for item in self.__getattribute__(key):
                        if isinstance(item, SingleBody):
                            item.render(multi_child_head)
                        if isinstance(item, MultiBody):
                            item.render(multi_child_head)
                        continue
                    continue
                child = etree.SubElement(multi_child_head, value)
                child.text = self.__getattribute__(key)