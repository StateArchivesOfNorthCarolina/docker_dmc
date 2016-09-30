#############################################################
# 2016-09-22: MessageType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implements the EAXS message-type
##############################################################

from email.message import Message

import eaxs.eaxs_helpers.Restrictors as restrict
from eaxs.HashType import Hash
from eaxs.HeaderType import Header
from eaxs.IncompleteParseType import IncompleteParse
from eaxs.MultiBodyType import MultiBody
from eaxs.SingleBodyType import SingleBody
from xml_help.CommonMethods import CommonMethods
from eaxs.eaxs_helpers import MessageProcessor


class DmMessage:
    """"""

    def __init__(self, rel_path, local_id, message):
        """Constructor for Message"""
        self.message = message  # type: Message
        self.relative_path = rel_path  # type: str
        self.local_id = local_id  # type: int
        self.message_id = CommonMethods.cdata_wrap(self.message.get("Message-ID"))  # type: str
        self.mime_version = self.message.get("MIME-Version")  # type: str
        self.m_from = CommonMethods.cdata_wrap(self.message.get("From"))  # type: str
        self.m_to = CommonMethods.cdata_wrap(self.message.get("To"))  # type: str
        self.subject = self.message.get("Subject")  # type: str
        self.reference = []  # type: []
        self.headers = []  # type: list[Header]
        self.status_flag = self.message.get("Status")  # type: str
        self.single_body = []  # type: list[SingleBody]
        self.multiple_body = []  # type: list[MultiBody]
        self.incomplete = None  # type: IncompleteParse
        try:
            self.eol = CommonMethods.get_eol(self.message.as_string())  # type: str
        except:
            self.eol = restrict.LF
        self.hash = CommonMethods.get_hash(self.message.as_bytes())  # type: Hash

        self._process_headers()
        self._process_payload()

    def _process_headers(self):
        for key, value in self.message.items():
            h = Header(key, value)
            self.headers.append(h)

    def _process_payload(self):
        message_processor = MessageProcessor.MessageProcessor(self.message, self.relative_path)
        self.multiple_body = message_processor.process_payloads()
