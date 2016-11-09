####################################################################################
# 2016-09-21: DarcMailCLI.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description:
#   This is a fork of Carl Schaefer's (Smithsonian Institution Archives)
#   CmdDArcMailXml.py.
####################################################################################


import os
import re
import argparse
import logging
import logging.config
import yaml
from dir_walker import Walker
from xml_help.CommonMethods import CommonMethods


class DarcMailCLI(object):
    """Refactor of CmdDArcMailXml GetArgs"""
    XML_WRAP = True
    NO_CHUNK = 0
    NO_LIMIT = 0
    NO_LEVELS = 0
    LEVELS = 1
    LOG_NAME = 'dm_xml.log.txt'

    def __init__(self):
        """Constructor for GetArguments"""
        self.account_directory = None
        self.account_name = None
        self.folder_name = None
        self.folder_path = None
        self.chunksize = self.NO_CHUNK
        self.levels = self.LEVELS
        self.max_internal = self.NO_LIMIT
        self.xml_wrap = self.XML_WRAP
        self.log_name = self.LOG_NAME
        self.data_dir = None
        self.xml_dir = None
        self.mbox_structure = None
        #  max_internal      = dmc.ALLOCATE_BY_DISPOSITION

        self._arg_parse()
        self._load_logger()
        self.logger = logging.getLogger()

    def _load_logger(self):
        if not os.path.exists('basic_logger.yml'):
            self._build_basic_logger()

        f = open('basic_logger.yml', 'r')
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    def _build_basic_logger(self):
        f = open('logger_template.yml', 'r')
        fh = open('basic_logger.yml', 'w')
        info = re.compile("info_log")
        errors = re.compile("errors_log")
        for line in f.readlines():
            if info.search(line):
                m = re.compile('info_log')
                l = os.path.normpath(m.sub(os.path.join(self.xml_dir, 'info.log'), line))
                fh.write(l.replace("\t", "\\t"))
                continue
            elif errors.search(line):
                m = re.compile('errors_log')
                l = m.sub(os.path.join(self.xml_dir, 'error.log'), line)
                fh.write(l.replace("\t", "\\t"))
                continue
            fh.write(line)
        fh.close()
        f.close()

    def _arg_parse(self):
        parser = argparse.ArgumentParser(description='Convert mbox into XML.')
        parser.add_argument('--account', '-a', dest='account_name', required=True,
                            help='email account name')
        parser.add_argument('--directory', '-d', dest='account_directory', required=True,
                            help='directory to hold all files for this account')
        parser.add_argument('--folder', '-f', dest='folder_name',
                            help='folder name (generate XML only for this one folder)')
        parser.add_argument('--max_internal', '-m', dest='max_internal',
                            type=int, default=self.NO_LIMIT,
                            help='maximum size in bytes for an internally-stored attachment, default = no limit')
        parser.add_argument('--chunk', '-c', dest='chunk', type=int,
                            default=self.NO_CHUNK,
                            help='number of messages to put in one output XML file, '+ \
                                 'default = no limit')
        parser.add_argument('--no_subdirectories', '-n', dest='no_subdirectories', action='store_true',
                            help='do NOT make subdirectories to hold external content' + \
                                 '(default = make subdirectories)')
        parser.add_argument('--data-dir', '-dd', dest='data_dir', type=str,
                            help='path to store the Email Account XML. Default is in the same directory as the'
                                 'account directory under a new folder /data')

        args = parser.parse_args()
        argdict = vars(args)

        self.account_name = argdict['account_name'].strip()
        self.account_directory = os.path.normpath(os.path.abspath(argdict['account_directory'].strip()))
        CommonMethods.set_store_rtf_body(False)
        CommonMethods.init_hash_dict()
        CommonMethods.set_dedupe()

        if 'max_internal' in argdict.keys():
            self.max_internal = int(argdict['max_internal'])

        if argdict['no_subdirectories']:
            self.levels = self.NO_LEVELS

        if argdict['data_dir']:
            base_path = os.path.normpath(os.path.abspath(os.path.join(self.account_directory, os.pardir)))
            CommonMethods.set_base_path(base_path)
            self.data_dir = os.path.normpath(os.path.abspath(os.path.join(base_path, argdict['data_dir'])))
            self.xml_dir = os.path.normpath(os.path.abspath(os.path.join(base_path, "eaxs_xml")))
            if not os.path.exists(self.data_dir):
                os.mkdir(self.data_dir)

            if not os.path.exists(self.xml_dir):
                os.mkdir(self.xml_dir)

            CommonMethods.set_attachment_dir(self.data_dir.split(os.sep)[-1])
            CommonMethods.set_xml_dir(self.xml_dir.split(os.sep)[-1])
        else:
            base_path = os.path.abspath(os.path.join(self.account_directory, os.pardir))
            self.data_dir = os.path.normpath(os.path.join(base_path, "data"))
            CommonMethods.set_attachment_dir(self.data_dir)
            CommonMethods.set_xml_dir(self.xml_dir)

        if argdict['folder_name']:
            self.folder_name = argdict['folder_name'].strip()

        if 'chunk' in argdict.keys():
            self.chunksize = argdict['chunk']
            CommonMethods.set_chunk_size(self.chunksize)

    def validate(self):
        # TODO: Determine what constitutes a valid structure and what does not.  This basically follows assumptions made
        # TODO: by the original DarcMail, many of which are no longer valid in this context.
        vs = ValidateStructure(self)
        vs.validate()
        self.mbox_structure = vs.structure
        return vs.is_valid

    def convert(self):
        '''
        Runs the whole #!
        :return:
        '''
        wlk = Walker.DirectoryWalker(self.account_directory, self.xml_dir, self.account_name)
        wlk.do_walk()


class ValidateStructure(object):
    """
     This class is to validate the structure of the mbox hierarchy. Takes a DarcMailCLI object
    """

    def __init__(self, darcmail):
        """Constructor for ValidateStructure
        @type darcmail : DarcMailCLI
        """
        self.darcmail = darcmail
        self.logger = darcmail.logger
        self.folder_name = darcmail.folder_name
        self.folder_path = darcmail.folder_path
        self.account_directory = darcmail.account_directory
        self.structure = None
        self.is_valid = True

    def validate(self):
        """validate: The co-ordinating function. """
        mbox_inventory = []
        if not self.check_account_directory(self.account_directory):
            self.is_valid = False
            return

        self.find_mbox_files(mbox_inventory, self.account_directory)

        if not self.check_folder(mbox_inventory, self.folder_name):
            self.is_valid = False
            return
        if self.folder_name:
            hit = False
            for (fname, mname, dir) in mbox_inventory:
                if self.folder_name == fname:
                    hit = True
                    self.folder_path = os.path.join(dir, mname)
            if not hit:
                # should never get here; was already checked
                self.logger.info('no mbox file {}.mbox under account_directory'.format(self.folder_name))
        self.structure = mbox_inventory

    def check_account_directory(self, dir_path):
        if not os.path.exists(dir_path):
            self.logger.info('account directory {} does not exist'.format(dir_path))
            return False
        if not os.path.isdir(dir_path):
            self.logger.info('{}  is not a directory'.format(dir_path))
            return False
        return True

    def find_mbox_files(self, folder_data, parent):
        for f in os.listdir(parent):
            child = os.path.join(parent, f)
            if os.path.isdir(child):
                self.find_mbox_files(folder_data, child)
            else:
                m = re.match('.*\.mbox$', f)
                if re.match('mbox', f):
                    # This is a readpst mbox structure test to see if it's a placeholder
                    if f.__sizeof__() == 0:
                        self.find_mbox_files(folder_data, child)
                    else:
                        ##  Jeremy M. Gibson (State Archives of North Carolina)
                        ##  2016-16-06 added this section for readpst compatibility
                        head, tail = os.path.split(parent)
                        folder_name = tail
                        folder_mbox = os.path.basename(child)
                        folder_dir = os.path.dirname(child)
                        folder_data.append((folder_name, folder_mbox, folder_dir))
                if m:
                    folder_name = re.sub('\.mbox$', '', f)
                    folder_mbox = os.path.basename(child)
                    folder_dir = os.path.dirname(child)
                    folder_data.append((folder_name, folder_mbox, folder_dir))

    def check_folder(self, mbox_inventory, folder):
        if len(mbox_inventory) == 0:
            self.logger.info('There are no .mbox files located under the account directory')
            return False
        folder_count = {}
        for (folder_name, mbox_name, path) in mbox_inventory:
            if folder_name in folder_count.keys():
                folder_count[folder_name] = folder_count[folder_name] + 1
            else:
                folder_count[folder_name] = 1
        multiple = 0
        duplicate_folders = []
        for folder_name in folder_count.keys():
            if folder_count[folder_name] > 1:
                multiple += 1
                # Jeremy M. Gibson (State Archives of North Carolina)
                # 2016-07-12 find the index of the duplicate folders and store as a list of lists
                duplicate_folders.append([i for i, v in enumerate(mbox_inventory) if v[0] == folder_name])
                self.logger.info('There are {} folders named {} under the account directory'
                                 .format(str(folder_count[folder_name]), folder_name))
        if multiple:
            # Jeremy M. Gibson (State Archives of North Carolina)
            # 2016-07-12 Rename the duplicate .mbox's to make them unique
            # Pattern is [<filename>.mbox, <filename>_001.mbox, <filename>_002.mbox]
            self.rename_dups(duplicate_folders, mbox_inventory)
            return True
        elif folder and folder not in folder_count.keys():
            self.logger.infor('File {}.mbox cannot be found under the account directory'.format(folder))
            return False
        return True

    def rename_dups(self, duplicate_list, inventory):
        """ Automatically rename duplicate folders
        # Jeremy M. Gibson (State Archives of North Carolina)
        # 2016-07-12 Rename the duplicate .mbox's to make them unique

        @type list duplicate_list
        @type list inventory:
        """
        for l in duplicate_list:
            # remove first item from the list
            i = l.pop(0)
            ind = 1
            for fldr in l:
                tup = inventory[fldr]
                original = os.path.join(tup[2], tup[1])
                renamed = os.path.join(tup[2], "{}_{:03d}{}".format(tup[0], ind,'.mbox'))
                renamed_mbox = "{}_{:03d}{}".format(tup[0], ind,'.mbox')
                renamed_fldr = "{}_{:03d}".format(tup[0], ind)
                inventory[fldr] = (renamed_fldr, renamed_mbox, tup[2])
                os.rename(original, renamed)
                ind += 1


if __name__ == "__main__":
    dmcli = DarcMailCLI()
    if dmcli.validate():
        print("Valid")
        dmcli.convert()
    else:
        print("Invalid Folder Structure")
