#!/usr/bin/env python3

""" This module contains a class for ???

TODO:
- code clean up and commenting.
- add dunders.
- address errors file tasks.
- setup.py
- gitignore
- 

####################################################################################
# 2016-09-21: DarcMailCLI.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description:
#   This is a fork of Carl Schaefer"s (Smithsonian Institution Archives)
#   CmdDArcMailXml.py.
####################################################################################
"""

# import modules.
import logging
import logging.config
import os
import sys
import yaml
from lib.BuildEmlDarcmail import BuildEmlDarcmail
from lib.dir_walker.MboxWalker import MboxWalker
from lib.xml_help.CommonMethods import CommonMethods


class DarcMail(object):
    """ A class for ... ??? Refactor of CmdDArcMailXml GetArgs

    Attributes:
        ???

    Example:
        ???
    """

    def __init__(self,
                 account_name,
                 account_directory,
                 output_directory,
                 from_eml=False,
                 chunksize=0,
                 stitch=False,
                 data_directory="attachments",
                 save_json=False,
                 _devel=False,
                 _tomes_tool=False
                 ):
        
        """Constructor for GetArguments"""

        # ???
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # convenience functions to clean up path notation.
        self._normalize_sep = lambda p: p.replace(os.sep, os.altsep) if (
                os.altsep == "/") else p
        self._normalize_path = lambda p: self._normalize_sep(os.path.relpath(p))  
        self._join_paths = lambda *p: self._normalize_path(os.path.join(*p))
        
        # ???
        self.account_name = account_name #TODO: Force this to be isidentitifer().
        self.account_directory = self._normalize_path(account_directory)
        self.output_dir = self._normalize_path(output_directory)
        self.eml_struct = from_eml
        self.chunksize = chunksize
        self.stitch = stitch
        self.data_dir = data_directory
        self.save_json = save_json 
        self.devel = _devel
        self.tomes_tool = _tomes_tool

        # ???
        self.base_path = None
        self.folder_name = None
        self.folder_path = None
        self.levels = 1
        self.max_internal = 0
        self.xml_dir = None
        self.json_dir = None
        self.mbox_structure = None
        self.mboxes = None
        self.eaxs = None
        self.emls = None
        self.psts = None

        # ???
        self._initialize()


    def _initialize(self):
        """ ??? Initialize common features and common attributes ??? and sets paths ...

        Returns:
            None
        """

        # ??? do this first because it ca affect other things ...
        CommonMethods.set_devel(self.devel)
        CommonMethods.set_from_tomes(self.tomes_tool)

        # ???
        CommonMethods.set_process_paths(self.output_dir)
        CommonMethods.set_base_path(CommonMethods.get_process_paths())
        
        # ???
        if not os.path.isdir(self.account_directory):
            msg = "Account directory '{}' does not exist.".format(self.account_directory)
            self.logger.error(msg)
            raise NotADirectoryError(msg)

        # ??? Can this go here? Make sure darcmail object is complete enough to pass over.
        if not self.eml_struct:
            if not self._validate():
                err = "Invalid MBOX structure at: {}".format(self.account_directory)
                self.logger.error(err)
                raise RuntimeError(err)
            
        # ???
        CommonMethods.set_store_rtf_body(False)
        CommonMethods.init_hash_dict()
        CommonMethods.set_dedupe()
        
        # ???
        self.eaxs = self._join_paths(CommonMethods.get_base_path(), "eaxs")
        self.mboxes = self._join_paths(CommonMethods.get_base_path(), "mboxes") # TODO: Nitin "Is this supposed to be 'mboxes'? It was "eaxs".
        self.emls = self._join_paths(CommonMethods.get_base_path(), "emls")
        self.psts = self._join_paths(CommonMethods.get_base_path(), "pst")

        # ???
        self.base_path = self._join_paths(self.eaxs, self.account_name)
        self.data_dir = self._normalize_path(os.path.abspath(self._join_paths(self.base_path, self.data_dir)))
        self.xml_dir = self._normalize_path(os.path.abspath(self._join_paths(self.base_path, "eaxs_xml")))

        # ???
        if os.path.isdir(self.base_path):
            msg = "Output directory '{}' already exists.".format(self.base_path)
            self.logger.error(msg)
            raise OSError(msg)

        # ???
        if self.stitch and self.chunksize == 0:
            self.logger.warning("Stich request requires a chunksize of greater than 0.")
            self.logger.info("Ignoring stitch request.")
            self.stitch = False
        CommonMethods.set_chunk_size(self.chunksize)
        CommonMethods.set_stitch(self.stitch)

        # ???
        CommonMethods.set_rel_attachment_dir(self._join_paths(os.path.sep, self._join_paths(os.path.split(self.base_path)[-1], "attachments")))
        CommonMethods.set_attachment_dir(self.data_dir)
        CommonMethods.set_xml_dir(self.xml_dir)
        
        # ???
        if self.save_json: # TODO: Nitin "This is outputting one JSON file per subfolder in the sample MBOX. Is that correct?"
            self.json_dir = self._normalize_path(os.path.abspath(self._join_paths(self.base_path, "eaxs_json")))
            if not self.eml_struct: 
                CommonMethods.set_store_json()
                CommonMethods.set_json_directory(self.json_dir)
            else:
                self.logger.warning("JSON output not supported with EML accounts.")
                self.logger.info("Ignoring JSON output request.")

        return

        
    def _validate(self):
        """ ???

        Returns:
            bool: The return value.
            True if an MBOX structure at @self.account_directory is valid. Otherwise, False."""
        
        # TODO: Determine what constitutes a valid structure and what does not.
        #       This currently follows assumptions made inal DarcMail, many of which are no longer valid in this context.

        # ???
        return True
        #vs = ValidateStructure(self)
        #vs.validate()
        #self.mbox_structure = vs.structure
        #return vs.is_valid
    

    def _data_dir(self):
        """ ???

        Returns:
            None
        """
        # ???
        os.makedirs(self.data_dir)
        os.makedirs(self.xml_dir)

        # ???
        if CommonMethods.get_store_json():
            os.makedirs(self.json_dir)

        return


    def _convert(self):
        """ ???

        Returns:
            None
        """

        # ???
        if self.eml_struct:
            self._data_dir()
            CommonMethods.set_package_type(CommonMethods.PACK_TYPE_EML)
            beml = BuildEmlDarcmail(self)
            return

        # ???
        CommonMethods.set_package_type(CommonMethods.PACK_TYPE_MBOX)
        self._data_dir()
        wlk = MboxWalker(self.account_directory, self.xml_dir, self.account_name)
        wlk._gather_mboxes()
        wlk.do_walk()

        return


    def create_eaxs(self):
        """ ???

        Returns:
            None
        """
        
        # ???
        try:
            self._convert()
            #TODO: Events here.
        except Exception as err:
            self.logger.error(err)
            raise err

        return

# CLI.
def main(account_name: ("???"), 
        account_directory: ("???"),
        output_directory: ("???"),
        silent: ("disable console logs", "flag", "s"),
        from_eml: ("???", "flag", "fe"),
        stitch: ("???", "flag", "st"),
        save_json: ("???", "flag", "j"),
        devel: ("???", "flag",),
        tomes_tool: ("???", "flag"),
        chunksize: ("???", "option", "c", int)="0",
        data_directory: ("???", "option")="attachments"):

    "Converts mbox|eml to EAXS XML.\
    \nexample: `python3 DarcMailCLI.py sample_mbox ../tests/sample_files/mbox sample_eaxs`"

    # make sure logging directory exists.
    logdir = "log"
    if not os.path.isdir(logdir):
        os.mkdir(logdir)

    # get absolute path to logging config file.
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(config_dir, "logger.yaml")
    
    # load logging config file.
    with open(config_file) as cf:
        config = yaml.safe_load(cf.read())
    if silent:
        config["handlers"]["console"]["level"] = 100
    logging.config.dictConfig(config)
    
    # make tagged version of EAXS.
    logging.info("Running CLI: " + " ".join(sys.argv))
    try:
        darcmail = DarcMail(account_name, account_directory, output_directory, from_eml, chunksize, stitch, data_directory, save_json, devel, tomes_tool)
        darcmail.create_eaxs()
        for i in darcmail.__dict__:
            print(i, darcmail.__dict__[i], type(darcmail.__dict__[i]), sep=" | ")
        logging.info("Done.")
        sys.exit()
    except Exception as err:
        raise err
        logging.critical(err)
        sys.exit(err.__repr__())


if __name__ == "__main__":
    import plac
    plac.call(main)
    #darcmail = DarcMail("sm", "tests/sample_files/mbox", "FOO", from_eml=False)
    #darcmail = DarcMail("se", "tests/sample_files/eml", "FOO", from_eml=True)
    #darcmail.create_eaxs()
    #for i in darcmail.__dict__:
    #    print(i, darcmail.__dict__[i], type(darcmail.__dict__[i]), sep=" | ")
