#############################################################
# 2016-09-22: MessageType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implements the EAXS message-type
##############################################################

from email.message import Message
import email


import eaxs.eaxs_helpers.Restrictors as restrict
from eaxs.HashType import Hash
from eaxs.HeaderType import Header
from eaxs.IncompleteParseType import IncompleteParse
from eaxs.MultiBodyType import MultiBody
from eaxs.SingleBodyType import SingleBody
from xml_help.CommonMethods import CommonMethods
from eaxs.eaxs_helpers.MessageProcessor import MessageProcessor as MPros

from lxml.ElementInclude import etree
import logging

status = {'RO': 'Seen',
          'O': 'Unseen',
          'A': 'Answered',
          'D': 'Deleted',
          '': None}


class DmMessage:
    """"""

    def __init__(self, rel_path, local_id, message):
        """Constructor for Message"""
        self.logger = logging.getLogger("MessageType")
        self.message = message  # type: Message

        # First parts of the schema message-type
        self.relative_path = rel_path  # type: str
        self.local_id = local_id
        self.message_id = CommonMethods.cdata_wrap(self.message.get("Message-ID"))  # type: str
        if self.message_id == '' or self.message_id is None:
            self.message_id = 'No Message-ID supplied'
        self.mime_version = CommonMethods.cdata_wrap(self.message.get("MIME-Version"))  # type: str
        self.incomplete = []  # type: list[IncompleteParse]

        # xm:message-headers
        xml_d = CommonMethods.tup_to_xml_date(CommonMethods.parsedate_tz(self.message.get("Date")))
        self.orig_date = xml_d  # type: str
        self.m_from = CommonMethods.cdata_wrap(self.message.get("From"))  # type: str
        self.sender = CommonMethods.cdata_wrap(self.message.get("Sender"))  # type: str
        try:
            self.m_to = CommonMethods.cdata_wrap(self.message.get("To"))  # type: str
        except TypeError as te:
            self.logger.error("{}".format(te))
            self.incomplete.append(IncompleteParse('TypeError parsing To Header', te))
        self.cc = CommonMethods.cdata_wrap(self.message.get("Cc"))  # type: str
        self.bcc = CommonMethods.cdata_wrap(self.message.get("Bcc"))  # type: str
        self.in_reply_to = CommonMethods.cdata_wrap(self.message.get("In-Reply-To"))
        self.references = CommonMethods.cdata_wrap(self.message.get("References"))  # type: str
        self.comments = CommonMethods.cdata_wrap(self.message.get("Comments"))  # type: str
        self.keywords = CommonMethods.cdata_wrap(self.message.get("Keywords"))  # type: str
        try:
            self.subject = CommonMethods.cdata_wrap(self.message.get("Subject"))  # type: str
        except TypeError as te:
            self.logger.error("{}".format(te))
            self.incomplete.append(IncompleteParse('TypeError parsing Subject line', te))
        try:
            self.status_flag = status.get(self.message.get("Status"))  # type: str
        except Exception as e:
            self.incomplete.append(IncompleteParse('TypeError parsing Status', e))

        self.headers = []  # type: list[Header]
        self.single_body = []  # type: list[SingleBody]
        self.multiple_body = []  # type: list[MultiBody]

        try:
            self.eol = CommonMethods.get_eol(self.message.as_string())  # type: str
        except KeyError as e:
            self.logger.error("Inspect Message: KeyError {}".format(self.message.get("Message-ID")))
            self.incomplete.append(IncompleteParse('KeyError parsing EOL', e))
        except UnicodeEncodeError as ue:
            self.logger.error("Inspect Message: UnicodeEncodeError {}".format(self.message.get("Message-ID")))
            self.incomplete.append(IncompleteParse('UnicodeEncodeError parsing EOL', ue))
        except LookupError as le:
            self.logger.error("Inspect Message: LookupError {}".format(self.message.get("Message-ID")))
            self.incomplete.append(IncompleteParse('LookupError parsing EOL', le))
        except Exception as er:
            self.incomplete.append(IncompleteParse('LookupError parsing EOL', er))

        self.hash = CommonMethods.get_hash(self.message.as_bytes())  # type: Hash

        self._process_headers()
        self._process_payload()

    def _process_headers(self):
        for key, value in self.message.items():
            if type(value) is email.header.Header:
                value = value.__str__()
            h = Header(key, value)
            self.headers.append(h)

    def _process_payload(self):
        message_processor = MPros(self.message, self.relative_path)
        self.multiple_body = message_processor.process_payloads()

    def render(self, parent=None):
        """
        :type parent: Element

        :param parent:
        :return:
        """
        if parent is not None:
            self.local_id = str(self.local_id)
            message = etree.SubElement(parent, "Message")
            for key, value in CommonMethods.get_messagetype_map().items():
                if self.__getattribute__(key) is not None:
                    if isinstance(self.__getattribute__(key), list):
                        #TODO: Handle this
                        for item in self.__getattribute__(key):
                            if isinstance(item, Header):
                                item.render(message)
                            if isinstance(item, MultiBody):
                                item.render(message)
                        continue
                    if isinstance(self.__getattribute__(key), Hash):
                        self.__getattribute__(key).render(message)
                        continue
                    if isinstance(self.__getattribute__(key), MultiBody):
                        self.__getattribute__(key).render(message)
                        continue
                    child = etree.SubElement(message, value)
                    child.text = self.__getattribute__(key)