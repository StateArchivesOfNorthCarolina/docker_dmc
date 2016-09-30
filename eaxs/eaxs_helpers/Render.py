#############################################################
# 2016-09-22: Render.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Renders a single Element and its children
##############################################################
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring
from xml.dom import minidom


class Render:
    """"""

    def __init__(self, root, children=None):
        """Constructor for Render
        @type root: str
        @type children: dict
        """
        self.root = Element(root)  # type: Element
        self.children = children
        self._build_element()

    def _build_element(self):
        if self.children:
            for e_type, value in self.children.items():
                child = SubElement(self.root, e_type)
                child.text = value

    def render(self):
        rough = tostring(self.root, 'utf-8')
        reparsed = minidom.parseString(rough)
        return reparsed.toprettyxml(indent="  ")

    def add_child(self, name, value):
        child = SubElement(self.root, name)
        child.text = value
