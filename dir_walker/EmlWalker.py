#############################################################
# 2017-04-03: EmlWalker.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: A walker class to build email messages into an
#              EAXS schema from eml files.  Test data provided
#              by the Utah State Archives
##############################################################
import os
import logging
import email
import gc
import json
from collections import OrderedDict
from email.message import Message

from .. eaxs.MessageType import DmMessage
from .. xml_help.CommonMethods import CommonMethods
from .. eaxs.Account import Account
from .. eaxs.FolderType import Folder


class DefaultListOrderedDict(OrderedDict):
    def __missing__(self, k):
        self[k] = []
        return self[k]


class EmlWalker:
    def __init__(self, acct_directory, xml_dir, acct_name):
        self.account_name = acct_name
        self.account_directory = acct_directory
        self.xml_dir = xml_dir
        self.account = Account(acct_name, xml_dir)
        self.current_folder = None
        self.messages = []
        self.current_relpath = None  # type: str
        self.total_messages_processed = 0
        self.logger = logging.getLogger("EmlWalker")
        self.message_pack = DefaultListOrderedDict()
        self.account.start_account()
        self.account.write_global_id()
        self.chunks = 0
        self.new_account = True
        if CommonMethods.get_store_json():
            self.json_write = CommonMethods.get_json_directory()

    def do_walk(self):
        for root, dirs, files in os.walk(self.account_directory):
            for f in files:
                if root not in self.message_pack:
                    self.message_pack[root] = []
                self.message_pack[root].append(f)
        self.process_folders()

    def process_folders(self):
        for path, files in self.message_pack.items():
            self.current_relpath = self.get_rel_path(path)
            for f in files:
                if CommonMethods.get_chunksize() != 0 and CommonMethods.get_chunksize() == self.chunks:
                    # Render the folder and reopen
                    self._fldr_render_reopen(path)
                    self.chunks = 0
                self.message_generator(os.path.join(path, f))
            self._fldr_render(path)
        self.account.close_account()
        if CommonMethods.get_stitch():
            self.account.stitch_account()

    def message_generator(self, path):
        """
        This is the main method that extracts email messages from an mbox.
        :type path: str
        :param path:
        :return:
        """
        buff = []
        with open(path, 'rb') as fh:
            # Open the eml found at path
            for line in fh.readlines():
                line = CommonMethods.sanitize(line)
                line = line.replace(b'\r\n', b'\n')
                buff.append(line)
        self._transform_buffer(buff, path)
        buff = None

    def _transform_buffer(self, buff, path):
        try:
            mes = email.message_from_bytes(b''.join(buff))  # type: Message
            self.logger.info("Processing Message-ID {}".format(mes.get("Message-ID")))
            self._process_message(mes, path)
            self.total_messages_processed += 1
            self.chunks += 1
        except MemoryError as me:
            print()

    def _process_message(self, mes, path):
        e_msg = DmMessage(self.get_rel_path(path), CommonMethods.increment_local_id(), mes)
        e_msg.message = None
        self.messages.append(e_msg)

    def get_rel_path(self, path):
        if self.account_directory == path:
            return "."
        common = os.path.commonpath([self.account_directory, path])
        rel = os.path.basename(path)
        diff = len(self.account_directory.split(os.path.sep)) - len(path.split(os.path.sep))
        return os.path.join('.', path.split(os.path.sep)[diff])

    def _set_current_relpath(self, path):
        if path == self.current_folder:
            return True
        elif len(self.messages) > 0:
            self._fldr_render(path)
            self.current_folder = path
        else:
            self.current_folder = path

    def _fldr_render(self, path):
        fldr = Folder(self.current_relpath, path)
        fldr.messages = self.messages
        fldr.render()
        if CommonMethods.get_store_json():
            fh = open(os.path.join(self.json_write, self.account_name + ".json"), 'a', encoding='utf-8')
            fh.write(',')
            jsn = fldr.render_json()
            json.dump(jsn, fh, sort_keys=False, indent=4)
            # json.dump(jsn, fh)
            fh.close()
        self.logger.info('Wrote folder of size {} bytes'.format(fldr.mbox_size))
        self.logger.info('Messages processed: {}'.format(self.total_messages_processed))
        fldr = None
        self.messages = []
        gc.collect()

    def _fldr_render_reopen(self, path):
        self._fldr_render(path)
        self.close_account()
        self.start_account()
        self.chunks = 0
        self.tracking_pos = 0
        gc.collect()

    def _fldr_render_continue(self, path):
        self._fldr_render(path)
        gc.collect()

    def start_account(self):
        self.account.start_account()
        self.account.write_global_id()
        self.new_account = False

    def close_account(self):
        self.account.close_account()
        self.new_account = True
