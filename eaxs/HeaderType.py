#############################################################
# 2016-09-22: HeaderType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of EAXS header-type
##############################################################
import re

import xml_help.CDataWrap as CD
from eaxs.eaxs_helpers.Render import Render


class Header:
    """"""

    def __init__(self, name, value, cdata=False):
        """Constructor for Header"""
        self.name = name  # type: str
        self.value = value  # type: str
        self.cdata = cdata
        if re.search("[<>\'\"]", value) is not None:
            self.cdata = True

    def render(self):
        if not self.cdata:
            r = Render('Header', {self.name: self.value})
        else:
            r = Render('Header', {self.name: CD.cdata_wrap(self.value)})
        return r.render()
