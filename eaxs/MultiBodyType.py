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
from xml_help.ContentTypeHandler import ContentTypeHandler


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

    def process_headers(self):
        for header, value in self.payload.items():
            if header == "Content-Type":
                expression = CommonMethods.get_content_type(value)
                self.content_type = expression[0]
                self.boundary_string = expression[2]
