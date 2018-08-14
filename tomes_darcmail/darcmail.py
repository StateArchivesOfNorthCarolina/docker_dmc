#!/usr/bin/env python3

""" This module contains a class for converting EML or MBOX to EAXS. This is a fork of 
CmdDArcMailXml.py by Carl Schaefer (Smithsonian Institution Archives). 

Todo:
    * Determine if "DISABLED" features should be re-instated.
"""

__NAME__ = "tomes_darcmail"
__FULLNAME__ = "TOMES DarcMail"
__DESCRIPTION__ = "Part of the TOMES project: converts EML or MBOX to EAXS."
__URL__ = "https://github.com/StateArchivesOfNorthCarolina/tomes-darcmail"
__VERSION__ = "0.0.1"
__AUTHOR__ = "Jeremy M. Gibson"
__AUTHOR_EMAIL__ = "Jeremy.Gibson@ncdcr.gov"

# import modules.
import sys; sys.path.append("..")
import logging
import logging.config
import os
import plac
import sys
import yaml
from tomes_darcmail.lib.BuildEmlDarcmail import BuildEmlDarcmail
from tomes_darcmail.lib.dir_walker.MboxWalker import MboxWalker
from tomes_darcmail.lib.xml_help.CommonMethods import CommonMethods


class DarcMail(object):
    """ A class for converting EML or MBOX to EAXS. This is a fork of CmdDArcMailXml.py by 
    Carl Schaefer (Smithsonian Institution Archives).
    
    Attributes:
        xml_dir(str): The path containing the EAXS file/s.
        data_dir (str): The path containing EAXS attachments.

    Example:
        >>> import os
        >>> sample_mbox = os.path.join("..", "tests", "sample_files", "mbox")
        >>> darcmail = DarcMail("sample_mbox_account", sample_mbox, ".")
        >>> os.path.isdir(darcmail.xml_dir) # False
        >>> darcmail.create_eaxs()
        >>> os.path.isdir(darcmail.xml_dir) # True       
    """

    def __init__(self,
             account_name,
             account_directory,
             output_directory,
             from_eml=False,
             chunksize=0,
             stitch=False,
             data_directory="attachments",
             ##save_json=False, # DISABLED.
             _devel=False,
             _tomes_tool=False):

        """ Sets instance attributes.

        Args:
            - account_name (str): The identifier to use for the email account.
            - account_directory (str): The path to the EML or MBOX account data.
            - output_directory (str): The containing folder in which to write the EAXS file/s.
            - from_eml (bool): Use True to specify an EML source account. Use False to specify
            and MBOX source account.
            - chunksize (int): The ideal number of messages within an EAXS file. If 0, one
            EAXS file will be written. Otherwise, an EAXS file will be written for every
            @chunksize number of messages. Note: this is an estimate as messages within a 
            single email folder are kept intact within each EAXS file.
            - stitch (bool): Use True to combine multiple EAXS files. Otherwise, use False.
            - data_directory (str): The directory in which to write EAXS attachment files.
            - _devel (bool): FOR TOMES DOCKER USE ONLY.
             _tomes_tool (bool): FOR TOMES DOCKER USE ONLY.
        """
        
        # set logging.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.event_logger = logging.getLogger("event_logger")
        self.event_logger.addHandler(logging.NullHandler())

        # function to force os.sep (i.e. replace "/" with "\" on Windows).
        normalize_sep = lambda p: p.replace(os.altsep, os.sep) if (
                os.altsep is not None) else p

        # set argument attributes.
        self.account_name = account_name
        self.account_directory = normalize_sep(account_directory)
        self.output_directory = normalize_sep(output_directory)
        self.eml_struct = from_eml
        self.chunksize = chunksize
        self.stitch = stitch
        self.save_json = False ##save_json # DISABLED.
        self.devel = _devel
        self.tomes_tool = _tomes_tool

        # set computed attributes.
        self.base_path = None
        self.levels = 1
        self.max_internal = 0
        self.xml_dir = None
        self.json_dir = None
        self.data_dir = data_directory
        self.mbox_structure = None
        self.mboxes = None
        self.eaxs = None
        self.emls = None
        self.psts = None
        self._initialize()


    def _initialize(self):
        """ Validates the constructor's argument values; sets common features and attributes.

        Returns:
            None

        Raises:
            TypeError: If @self.account_name is not an identifier.
            NotADirectoryError: If @self.account_directory is not a folder or if the 
            specified output path is not a folder.
            OSError: If the destination path already exists. 
        """

        self.logger.info("Initializing account data.")

        # set global development and "tomes_tool" mode before anything else happens.
        if self.devel:
            self.logger.info("Entering 'dev' mode.")
        if self.tomes_tool:
            self.logger.info("Entering 'Tomes Tool' mode.")
        CommonMethods.set_devel(self.devel)
        CommonMethods.set_from_tomes(self.tomes_tool)

        # set processing/output path.
        CommonMethods.set_process_paths(self.output_directory)
        CommonMethods.set_base_path(CommonMethods.get_process_paths())

        # verify @self.account_name is an identifier.
        if not self.account_name.isidentifier():
            msg = "An account name must contain only letters, numbers, and hyphens"
            msg += " and cannot start with a number."
            self.logger.error(msg)
            raise TypeError(msg)

        # verify @self.account_directory is a folder.
        if not os.path.isdir(self.account_directory):
            msg = "Account directory '{}' does not exist.".format(self.account_directory)
            self.logger.error(msg)
            raise NotADirectoryError(msg)
        
        # if the account is an MBOX, validate it. # DISABLED.
        ##if not self.eml_struct:
        ##    if not self._validate():
        ##        err = "Invalid MBOX structure at: {}".format(self.account_directory)
        ##        self.logger.error(err)
        ##        raise RuntimeError(err)
            
        # set additional globals.
        CommonMethods.set_store_rtf_body(False)
        CommonMethods.init_hash_dict()
        CommonMethods.set_dedupe()
        
        # set data paths.
        self.eaxs = os.path.join(CommonMethods.get_base_path(), "eaxs")
        self.mboxes = os.path.join(CommonMethods.get_base_path(), "mboxes")
        self.emls = os.path.join(CommonMethods.get_base_path(), "emls")
        self.psts = os.path.join(CommonMethods.get_base_path(), "pst")
        self.base_path = os.path.join(self.eaxs, self.account_name)
        self.data_dir = os.path.abspath(os.path.join(self.base_path,
            self.data_dir))
        self.xml_dir = os.path.abspath(os.path.join(self.base_path,
            "eaxs_xml"))

        # verify @self.base_path doesn't exist.
        if os.path.isdir(self.base_path):
            msg = "Output directory '{}' already exists.".format(self.base_path)
            self.logger.error(msg)
            raise OSError(msg)

        # set stitching values.
        if self.stitch and self.chunksize == 0:
            self.logger.warning("Stitch request requires a chunksize of greater than 0.")
            self.logger.info("Ignoring stitch request.")
            self.stitch = False
        CommonMethods.set_chunk_size(self.chunksize)
        CommonMethods.set_stitch(self.stitch)

        # set attachment data and EAXS XML folders.
        CommonMethods.set_rel_attachment_dir(os.path.join(os.path.sep, os.path.join(
            os.path.split(self.base_path)[-1], "attachments")))
        CommonMethods.set_attachment_dir(self.data_dir)
        CommonMethods.set_xml_dir(self.xml_dir)
        
        # toggle JSON output. # DISABLED.
        ##if self.save_json:
        ##    self.json_dir = os.path.abspath(os.path.join(
        ##        self.base_path, "eaxs_json"))
        ##    if not self.eml_struct: 
        ##        CommonMethods.set_store_json()
        ##        CommonMethods.set_json_directory(self.json_dir)
        ##    else:
        ##        self.logger.warning("JSON output not supported with EML accounts.")
        ##        self.logger.info("Ignoring JSON output request.")

        return

        
    def _validate(self): # DISABLED.
        """ Validates @self.account_directory as an MBOX if @self_from_eml if False.

        Returns:
            bool: The return value.
            True if an MBOX structure is valid. Otherwise, False.
        """

        self.logger.info("Validating MBOX at: {}".format(self.account_directory))

        # validate the MBOX.
        vs = ValidateStructure(self)
        vs.validate()
        self.mbox_structure = vs.structure
        
        # report on validity.
        if vs.is_valid:
            self.logger.info("MBOX is valid.")
        else:
            self.logger.warning("MBOX is not valid; serious errors may occur.")
        
        return vs.is_valid


    def _create_data_dirs(self):
        """ Creates output folders.

        Returns:
            None
        """

        self.logger.info("Creating output directories.")

        # create output folders.
        os.makedirs(self.data_dir)
        os.makedirs(self.xml_dir)

        # if needed, create JSON output folder. # DISABLED.
        ##if CommonMethods.get_store_json():
        ##    os.makedirs(self.json_dir)

        return


    def _convert(self):
        """ Converts EML or MBOX to EAXS.

        Returns:
            None
        """

        # if @self.from_eml is True, parse @self.account_directory as EML.
        if self.eml_struct:
            self.logger.info("Converting EML to EAXS.")
            CommonMethods.set_package_type(CommonMethods.PACK_TYPE_EML)
            self._create_data_dirs()
            BuildEmlDarcmail(self)
            return

        # otherwise, parse the account as MBOX.
        self.logger.info("Converting MBOX to EAXS.")
        CommonMethods.set_package_type(CommonMethods.PACK_TYPE_MBOX)
        self._create_data_dirs()
        wlk = MboxWalker(self.account_directory, self.xml_dir, self.account_name)
        wlk._gather_mboxes()
        wlk.do_walk()

        return


    def create_eaxs(self):
        """ Creates an EAXS account.

        Returns:
            None
        """
        
        # run self._convert() and log event data.
        try:
            self._convert()
            self.logger.info("Created EAXS at: {}".format(self.xml_dir))
            self.event_logger.info({"entity": "agent", "name": __NAME__, 
                    "fullname": __FULLNAME__, "uri": __URL__, "version": __VERSION__})
            self.event_logger.info({"entity": "event", "name": "mime_to_eaxs", 
                "agent": __NAME__, "object": "eaxs"})
            self.event_logger.info({"entity": "object", "name": "mime", 
                "category": "representation"})
            self.event_logger.info({"entity": "object", "name": "eaxs", 
                    "category": "representation"})
        except Exception as err:
            self.logger.error(err)
            raise err

        return


# CLI.
def main(account_name: ("account identifier"), 
        account_directory: ("source account"),
        output_directory: ("EAXS destination"),
        silent: ("disable console logs", "flag", "s"),
        from_eml: ("toggle EML processing", "flag", "fe"),
        stitch: ("combine chuncked EAXS files", "flag", "st"),
        chunksize: ("messages per chuncked EAXS file (estimate)", "option", "c", int)=0,
        data_directory: ("attachment folder", "option")="attachments"):

    "Converts EML|MBOX to EAXS.\
    \nexample: `python3 darcmail.py sample_mbox ../tests/sample_files/mbox OUTPUT`"

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
        darcmail = DarcMail(account_name, account_directory, output_directory, from_eml,
                stitch, chunksize, data_directory, _DEVEL, _TOMES_TOOL)
        darcmail.create_eaxs()
        logging.info("Done.")
        sys.exit()
    except Exception as err:
        logging.critical(err)
        sys.exit(err.__repr__())


if __name__ == "__main__":
    
    # test for secret flags.
    secrets = ["-dev", "-tt"]
    _DEVEL = secrets[0] in sys.argv
    _TOMES_TOOL = secrets[1] in sys.argv
    
    # remove secret flags; call plac.
    args = [a for a in sys.argv[1:] if a not in secrets]
    plac.call(main, args)
