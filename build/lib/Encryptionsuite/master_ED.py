import base64
# import subprocess
import logging
import logging.handlers
import os
import sys

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)


class HandleFiles:

    def __init__(self, input_file, passphrase):
        self.input_file = input_file
        self.passphrase = passphrase

    # generate encryption key for the file using a passphrase
    @staticmethod
    def generate_enc_key(passphrase):
        salt = b'salt_'  # Add a salt for added security
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Adjust the number of iterations as needed for security
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return key

    # function to read and encrypt the file
    def encrypt_file(self):
        try:

            # open the file for encryption
            with open(self.input_file, 'rb') as file:
                data = file.read()

            key = HandleFiles.generate_enc_key(self.passphrase)
            cipher = Fernet(key)
            encrypted_data = cipher.encrypt(data)

            # Append '.encrypted' to the file name
            print("\033[1;35mModifying file name\033[0m")
            file = self.input_file
            e_level = int(file[-1:]) + 1 if file[-4:-1] == 'enc' else 0
            output_file = f'{file[:-1]}{e_level}' if file[-4:-
                                                          1] == 'enc' else f'{file}.enc{e_level}'

            # write out encrypted file data to a new file
            with open(output_file, 'wb') as file:
                file.write(encrypted_data)

                # remove/permanently delete input_file
                # subprocess.run(['rm', '-r', f'{self.input_file}'])

            logger.info(
                f"\033[1m{self.input_file}\033[0m encrypted successfully with key=\033[36m{self.passphrase}\033[0m")

            print(f"File saved as {output_file}")
        except KeyboardInterrupt:
            print("\nExiting")
            sys.exit(1)
        except Exception as e:
            logger.error(f"\033[31m{e}\033[0m")
        return output_file

    def decrypt_file(self):
        try:
            # Ensure the key is of type bytes
            key = HandleFiles.generate_enc_key(self.passphrase)
            cipher = Fernet(key)

            # open the file for decryption
            with open(self.input_file, 'rb') as file:
                encrypted_data = file.read()

            decrypted_data = cipher.decrypt(encrypted_data)

            # Extract encryption infor from the encrypted file for decide on appropriate file name
            file = self.input_file
            e_level = int(file[-1:]) - 1 if file[-4:-
                                                1] == 'enc' and int(file[-1:]) != 0 else ''
            fname = f'{file[:-1]}{e_level}' if e_level != '' else file[:-4]
            with open(fname, 'wb') as file:
                file.write(decrypted_data)
            logger.info(
                    f"\033[1m{self.input_file}\033[0m decrypted successfully as \033[1m{self.input_file[:-1]}{int(self.input_file[-1:]) -1}\033[0m with key=\033[32m{self.passphrase}\033[0m")
        except KeyboardInterrupt:
            print("\nExiting")
            sys.exit(1)
        except Exception as e:
            print(f"\033[31m{e}\033[0m")


class HandleFolders:
    def __init__(self, folder, passphrase):
        self.passphrase = passphrase
        self.folder = folder

    def encrypt_folder(self):
        try:
            # Iterate over all files in the folder
            for root, dirs, files in os.walk(self.folder):
                for file in files:
                    input_file = os.path.join(root, file)
                    print(f"\033[1;34mEncrypting{input_file}\033[0m", end="\r")
                    init = HandleFiles(input_file, self.passphrase)
                    init.encrypt_file()
        except KeyboardInterrupt:
            print("\nExiting")
            sys.exit(1)
        except Exception as e:
            print(f"Sorry:: \033[31m{e}\033[0m")

    def decrypt_folder(self):
        try:
            # Iterate over all files in the folder
            for root, dirs, files in os.walk(self.folder):
                for file in files:
                    if file[-4:-1] == "enc":
                        input_file = os.path.join(root, file)
                        print(
                            f"\033[1;34mDecrypting{input_file}\033[0m", end="\r")
                        init = HandleFiles(input_file, self.passphrase)
                        init.decrypt_file()
        except KeyboardInterrupt:
            print("\nExiting")
            sys.exit(1)
        except Exception as e:
            print(f"Sorry:: \033[31m{e}\033[0m")


if __name__ == "__main__":
    init = HandleFiles('test.docx', 'skye')
    init.encrypt_file()
