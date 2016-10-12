#############################################################
# 2016-09-22: Walker.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description:
##############################################################
import os
from eaxs.MessageType import DmMessage
from xml_help.CommonMethods import CommonMethods
import mailbox
from eaxs.Account import Account
from eaxs.FolderType import Folder
import logging


class DirectoryWalker:
    """"""

    def __init__(self, root_level, xml_dir, account_name):
        """Constructor for DirectoryWalker"""

        self.root = root_level
        self.folders = {}
        self.messages = []
        self.current_relpath = None  # type: str
        self.xml_dir = xml_dir
        self.account = Account(account_name, xml_dir)
        self.logger = logging.getLogger()
        self.total_messages_processed = 0  # type: int
        self.chunks = 0  # type: int
        self.new_account = True

    def do_walk(self):
        for root, dirs, files in os.walk(self.root, topdown=False):
            if len(files) == 0:
                continue
            mbx_path = os.path.join(root, files[0])
            if len(files) > 1 or os.path.getsize(mbx_path) == 0:
                # TODO: Handle this in a rational way.
                pass
            else:
                self.current_relpath = self.get_rel_path(mbx_path)
                self.logger.info('Processing folder found at: {}'.format(mbx_path))

                if self.total_messages_processed == 0:
                    self.start_account()
                if self.chunks > CommonMethods.get_chunksize():
                    # Close old account
                    self.close_account()
                    self.start_account()
                    self.chunks = 0

                self.process_mbox(mbx_path)

                fldr = Folder(self.current_relpath, mbx_path)
                fldr.messages = self.messages
                fldr.render()
                self.logger.info('Wrote folder of size {} bytes'.format(fldr.mbox_size))
                self.logger.info('Messages processed: {}'.format(self.total_messages_processed))
                fldr = None
                self.messages = []

    def process_mbox(self, path):
        mbox = mailbox.mbox(path)
        self.messages = []
        try:
            for message in mbox:
                self.total_messages_processed += 1
                self.chunks += 1
                e_msg = DmMessage(self.get_rel_path(path), CommonMethods.increment_local_id(), message)
                e_msg.message = None
                self.messages.append(e_msg)
        except MemoryError as er:
            self.logger.error("Memory Error {}".format(er))

    def get_rel_path(self, path):
        if self.root == path:
            return "."
        common = os.path.commonprefix([self.root, path])
        common = path.replace(common, '.')
        return os.path.split(common)[0]

    def start_account(self):
        self.account.start_account()
        self.account.write_global_id()
        self.new_account = False

    def close_account(self):
        self.account.close_account()
        self.new_account = True
