#############################################################
# 2016-09-22: FolderType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implements the EAXS folder-type complex type
##############################################################
import os
from eaxs.MessageType import DmMessage
from lxml.ElementInclude import etree
import re
from xml_help.CommonMethods import CommonMethods


class Folder:
    """"""

    def __init__(self, relpath, mbox_path):
        """Constructor for Folder"""
        self.name = mbox_path.split(os.sep)[-2]  # type: str
        self.relpath = relpath
        self.messages = []  # type: list[DmMessage]
        self.folders = []  # type: list[Folder]
        self.mbox_size = os.path.getsize(mbox_path)

    def add_folder(self, name, relpath):
        fold = Folder(name, relpath)
        self.folders.append(fold)

    def get_folder(self, i):
        return self.folders[i]

    def render(self):
        folder = etree.Element("Folder")
        name = etree.SubElement(folder, "Name")
        name.text = self.name
        if len(self.messages) > 0:
            for mes in self.messages:
                """
                :type mes: DmMessage
                """
                mes.render(folder)
        outfile = open(CommonMethods.get_eaxs_filename(), "ab")
        etree.ElementTree(folder).write(outfile, encoding="utf-8", pretty_print=True)
        folder = None
