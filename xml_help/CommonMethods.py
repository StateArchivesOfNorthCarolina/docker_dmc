import re
from xml_help.CDataWrap import cdata_wrap as cdw
import eaxs.eaxs_helpers.Restrictors as restrict
from email.message import Message
import hashlib
from eaxs.HashType import Hash

global __LOCALID__
global __ROOTPATH__
global __RELPATH__

__LOCALID__= 0  # type: int


class CommonMethods:

    @staticmethod
    def cdata_wrap(text):
        try:
            if re.search("[<>\'\"]", text) is not None:
                return cdw(text)
            return text
        except TypeError as e:
            if text is None:
                return "Error: No Recipient Found"

    @staticmethod
    def get_content_type(content_type):
        '''
        :param content_type:
        :type content_type : str
        :return: tuple:
        '''

        if re.search(';', content_type) is not None:
            # has a secondary component
            mime = content_type.split(";")[0]
            key, value = content_type.split(";")[1].split("=")
            return [mime, key.strip(), value]
        else:
            # is only a mime type
            return [content_type]

    @staticmethod
    def increment_local_id():
        globals()["__LOCALID__"] += 1
        return globals()["__LOCALID__"]

    @staticmethod
    def get_eol(message):
        """
        :param message
        :type message : str
        :return:
        """
        try:
            if message[-2:] == "\r\n": return restrict.CRLF
            if message[-1:] == "\r": return restrict.CR
            if message[-1:] == "\n" and message[-2:] != "\r\n": return restrict.LF
        except KeyError as ke:
            return restrict.LF

    @staticmethod
    def get_hash(message):
        '''
        Defaulting to SHA1 in this version of the tool.  Future versions give options.
        :return:
        '''
        hsh = hashlib.sha1()
        hsh.update(message)
        return Hash(hsh.hexdigest(), restrict.SHA1)

    @staticmethod
    def set_base_path(path):
        globals()["__ROOTPATH__"] = path

    @staticmethod
    def get_base_path():
        return globals()["__ROOTPATH__"]

    @staticmethod
    def set_attachment_dir(folder='attachments'):
        globals()["__ATTACHMENTS__"] = folder

    @staticmethod
    def get_attachment_directory():
        return globals()["__ATTACHMENTS__"]

    @staticmethod
    def set_store_rtf_body(val=False):
        globals()["__STORE_RTF_BODY__"] = val

    @staticmethod
    def store_rtf_body():
        return globals()["__STORE_RTF_BODY__"]


