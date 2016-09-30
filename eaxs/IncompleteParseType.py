#############################################################
# 2016-09-26: IncompleteParseType.py 
# Author: Jeremy M. Gibson (State Archives of North Carolina)
# 
# Description: Implementation of the incomplete-parse-type
##############################################################


class IncompleteParse:
    """"""
    
    def __init__(self, error_type=None, error_location=None):
        """Constructor for IncompleteParse"""
        self.error_type = error_type  # type: str
        self.error_location = error_location  # type: str
        