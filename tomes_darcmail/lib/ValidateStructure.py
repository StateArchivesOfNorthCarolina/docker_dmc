import os
import re

class ValidateStructure(object):
    """
     This class is to validate the structure of the mbox hierarchy. Takes a DarcMail object
    """

    def __init__(self, darcmail):
        """Constructor for ValidateStructure
        @type darcmail : DarcMail
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
                        ##  2016-06-16 added this section for readpst compatibility
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
            self.logger.info('File {}.mbox cannot be found under the account directory'.format(folder))
            return False
        return True

    def rename_dups(self, duplicate_list, inventory):
        """ Automatically rename duplicate folders
        # Jeremy M. Gibson (State Archives of North Carolina)
        # 2016-07-12 Rename the duplicate .mbox's to make them unique

        @type duplicate_list: list
        @type inventory: list
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


