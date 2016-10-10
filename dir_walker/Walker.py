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
        self.account.start_account()
        self.account.write_global_id()

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
                self.process_mbox(mbx_path)
                fldr = Folder(self.current_relpath, mbx_path)
                fldr.messages = self.messages
                fldr.render()
        self.account.close_account()

    def process_mbox(self, path):
        mbox = mailbox.mbox(path)
        self.messages = []
        print('Processing mbox found at: {}\n'.format(path))
        try:
            for message in mbox:
                e_msg = DmMessage(self.get_rel_path(path), CommonMethods.increment_local_id(), message)
                e_msg.message = None
                self.messages.append(e_msg)
        except MemoryError as e:
            print("TODO: Add Logger, handle Memory Error")
        print('Processed mbox found at: {}\n'.format(path))

    def get_rel_path(self, path):
        if self.root == path:
            return "."
        common = os.path.commonprefix([self.root, path])
        common = path.replace(common, '.')
        return os.path.split(common)[0]
