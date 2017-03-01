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
        self.mbx = None  # type: mailbox.mbox
        self.root = root_level
        self.folders = {}
        self.messages = []
        self.current_relpath = None  # type: str
        self.xml_dir = xml_dir
        self.account = Account(account_name, xml_dir)
        self.logger = logging.getLogger("DirectoryWalker")
        self.total_messages_processed = 0  # type: int
        self.chunks = 0  # type: int
        self.tracking_pos = 0  # type: int
        self.messages_in_folder = 0  # type: int
        self.messages_no_start_fldr = 0  # type: int
        self.message_no_end_flder = 0  # type: int
        self.new_account = True
        self.mboxes = []  # type: list
        self.new_folder = False

    def _gather_mboxes(self):
        for root, dirs, files in os.walk(self.root, topdown=True):
            if len(files) == 0:
                continue
            for f in files:
                nf = os.path.join(root, f)
                if os.path.getsize(nf) == 0:
                    continue
                self.mboxes.append(nf)

    def _do_walk_with_mboxes_inv(self):
        self.start_account()
        for path in self.mboxes:
            self.current_relpath = self.get_rel_path(path)
            self.logger.info('Processing folder found at: {}'.format(path))
            self.new_folder = False
            self.mbx = None
            while not self.new_folder:
                while self.process_mbox(path):
                    # This means the mbox, or Folder, has more messages than the chunksize
                    # Render a folder and then close and reopen account
                    self._fldr_render_reopen(path)
            self._fldr_render_continue(path)
        self.close_account()

    def _fldr_render_reopen(self, path):
        fldr = Folder(self.current_relpath, path)
        fldr.messages = self.messages
        fldr.render()
        self.logger.info('Wrote folder of size {} bytes'.format(fldr.mbox_size))
        self.logger.info('Messages processed: {}'.format(self.total_messages_processed))
        fldr = None
        self.messages = []
        self.close_account()
        self.start_account()
        self.chunks = 0
        self.tracking_pos = 0

    def _fldr_render_continue(self, path):
        fldr = Folder(self.current_relpath, path)
        fldr.messages = self.messages
        fldr.render()
        self.logger.info('Wrote folder of size {} bytes'.format(fldr.mbox_size))
        self.logger.info('Messages processed: {}'.format(self.total_messages_processed))
        fldr = None
        self.messages = []

    def do_walk(self):
        self._do_walk_with_mboxes_inv()
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
                if self.chunks > CommonMethods.get_chunksize() != 0:
                    # Close old account
                    self.close_account()
                    self.start_account()
                    self.chunks = 0

                while self.process_mbox(mbx_path):
                    # This means the mbox, or Folder, has more messages than the chunksize
                    pass

                fldr = Folder(self.current_relpath, mbx_path)
                fldr.messages = self.messages
                fldr.render()
                self.logger.info('Wrote folder of size {} bytes'.format(fldr.mbox_size))
                self.logger.info('Messages processed: {}'.format(self.total_messages_processed))
                fldr = None
                self.messages = []
        self.account.close_account()
        self.logger.info('Total messages processed: {}'.format(self.total_messages_processed))

    def process_mbox(self, path):
        if self.mbx is None:
            self.mbx = mailbox.mbox(path)
        self.messages = []
        try:
            for message in self.mbx:
                if self.tracking_pos < self.total_messages_processed:
                    self.tracking_pos += 1
                    continue
                self.total_messages_processed += 1
                self.chunks += 1
                self.tracking_pos += 1
                e_msg = DmMessage(self.get_rel_path(path), CommonMethods.increment_local_id(), message)
                e_msg.message = None
                self.messages.append(e_msg)
                if self.chunks == CommonMethods.get_chunksize() != 0:
                    # Chunks exceeded within the current folder return without setting that flag
                    # Reset the tracking position.
                    return True
            self.new_folder = True
            self.tracking_pos = self.total_messages_processed
            return False
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
