## A simple hashed email storage class
# 
# Supports writing sha256-hashed and salted data and checking 
# these data (e.g., emails) for existence in the stored list.
# 
# Used for implementing simple access restrictions.
# 
import hashlib
import random
import string
import os
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def _check_if_valid_email(email : str):
    """
    Validate that the string is an email.
    """
    if(re.fullmatch(regex, email)):
        return True
    return False

def _get_salt(salt_size = 32):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(salt_size))


class AuthorizationManager:
    def __init__(self, email_list_path = 'hashed_email.txt'):
        self.email_list_path= email_list_path
        if not os.path.exists(self.email_list_path):
            open(self.email_list_path,'a').close()
            print("created a new empty file at {fname}".format(fname=self.email_list_path))
        self.read_email_list()
        self.recently_checked_emails = {}

    def read_email_list(self) -> None:
        """
        Reads a set of hashed emails and their "salt" values from a text file
        and stores them in an internal object.
        """
        with open(self.email_list_path,'r') as f:
            all_dat = f.read().split('\n')

        self.hashed_email_list = [d.split(':') for d in all_dat if len(d)>0]


    def add_to_list(self, new_email : str, check_first = True) -> str:
        """
        Adds the email in the list and optionally checks if the email is in the list.

        This function may be susceptible to timing attacks
        (if the email is in the list it returns faster)
        """
        if not _check_if_valid_email(new_email):
            raise Exception('email not valid - aborting.')

        salt = _get_salt()
        if check_first:
            if self.check_if_in_list(new_email):
                return salt

        h = hashlib.new('sha256')
        h.update( (new_email + salt).encode() )
        hdig = h.hexdigest()
        new_entry_hashed = hdig + ':'+ salt
        with open(self.email_list_path,'a') as f:
            f.write(new_entry_hashed + '\n')

        self.hashed_email_list.append([hdig, salt])

        return salt

    def check_if_in_list(self,  email : str) -> bool:
        """
        Hashes the email with the salts of the DB and checks 
        if there is a match. 
        """

        if not _check_if_valid_email(email):
            raise Exception('email not valid - aborting.')

        for hashed_email, salt in self.hashed_email_list:
            h = hashlib.new('sha256')
            h.update( (email + salt).encode() )
            dig= h.hexdigest()
            if dig == hashed_email:
                return True

        return False


if __name__ == '__main__':
    am = AuthorizationManager()

