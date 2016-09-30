#############################################################
# 2016-09-26: ParameterType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of the parameter-type
##############################################################


class Parameter:
    """"""

    def __init__(self, name=None, value=None):
        """Constructor for Parameter"""
        self.name = name  # type: str
        self.value = value  # type: str
