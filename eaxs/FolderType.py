#############################################################
# 2016-09-22: FolderType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implements the EAXS folder-type complex type
##############################################################
import os
from eaxs.MessageType import Message


class Folder:
    """"""

    def __init__(self, name, mailb, relpath):
        """Constructor for Folder"""
        self.name = name
        self.relpath = relpath
        self.messages = []  # type: [Message]
        self.folders = []  # type: [Folder]
        self.mbox_path = mailb  # type: str
        self.mbox_size = os.path.getsize(self.mbox_path)

    def add_folder(self, name, filename, relpath):
        fold = Folder(name, filename, relpath)
        self.folders.append(fold)

    def get_folder(self, i):
        return self.folders[i]