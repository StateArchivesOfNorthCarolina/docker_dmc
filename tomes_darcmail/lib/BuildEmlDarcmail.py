import logging
from tomes_darcmail.lib.dir_walker.EmlWalker import EmlWalker


class BuildEmlDarcmail(object):
    def __init__(self, darcmail):
        self.logger = logging.getLogger("Main_Eml")
        self.account_directory = darcmail.account_directory
        self.account_name = darcmail.account_name
        self.xml_dir = darcmail.xml_dir
        emwalk = EmlWalker(self.account_directory, self.xml_dir, self.account_name)
        self.logger.info("XML dir is {}".format(self.xml_dir))
        self.logger.info("Processing {} \n to {}".format(self.account_directory, self.xml_dir))
        emwalk.do_walk()


