import argparse
import logging
import logging.handlers
import os
import sys

from .enc_dec import decrypt_file, decrypt_folder, encrypt_file, encrypt_folder
from .master_ED import HandleFiles, HandleFolders
from .mciphers import dec_control, enc_control

logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)


def clean(input_file):
    _orig_ = input_file
    for i in range(int(input_file[-1:]), -1, -1):
        file = f'{input_file[:-1]}{i}'
        while os.path.exists(file) and file != f'{input_file[:-1]}{_orig_[-1:]}':
            print(f"\033[2;35mDelete \033[1m{file}🚮\033[0m")
            os.remove(file)
            break


def _clean_(input_file):
    _orig_ = input_file
    for i in range(int(input_file[-1:])):
        file = f'{input_file[:-1]}{i}'
        while os.path.exists(file) and file != f'{input_file[-1:]}{_orig_[-1:]}':
            print(f"\033[2;35mDelete \033[1m{file}🚮\033[0m")
            os.remove(file)
            break


def get_keys(pf):
    with open(pf) as f:
        ps = f.read()
    return ps.split(',')


def main():
    # create argument parser
    parser = argparse.ArgumentParser(
        description='''Encrypt or decrypt files and folders''')
    # Define required arguments
    parser.add_argument(
        '-m', '--mode', choices=["encrypt", "decrypt"], help="\
Mode:encryption or decryption", required=True)
    parser.add_argument('-i', '--input_file', type=str,
                        help='Input file path or folder', required=True)

    parser.add_argument('-Rk', '--random_key', type=str,
                        help='decryption key to be used')
    parser.add_argument('-p', '--passphrase', type=str,
                        help='Encryption/decryption passphrase/password to \
be used')
    parser.add_argument(
        "-c", "--cipher", help="cipher to be used, avaiable ciphers:\
        [\033[1;34mcaesar, PlayfairCipher, vigenere\033[0m]")

    Note = "\033[96mPassword option does not work for caesar cipher\033[0m"

    parser.add_argument("--pass_list", "-pl", help=f"""Provide passwords list or file containing \
password list for decryptiona and encryption
\n{Note}""")

    # Parse the commandline arguments
    args = parser.parse_args()
    input_file = args.input_file

    # Handle file/folder encryption
    if args.mode == 'encrypt':
        print("\033[1;92mComencing encryption process\033[0m")
        # Handle cipher choices
        if args.cipher:
            # Since caesar cipher needs no passphrase, ommit it
            if args.cipher.lower() == 'caesar' or args.cipher.lower() == 'caesarcipher':
                if args.pass_list:
                    print(
                        "\033[91mSorry caesar cipher accepts not password list\033[0m")
                    prompt = input("Press enter to continue")
                    if prompt.lower() == 'c':
                        sys.exit()
                    else:
                        pass
                args.passphrase = None
                args.random_key = None
                enc_control(input_file, args.cipher, args.passphrase)

            if args.pass_list:
                pass_ls = get_keys(args.pass_list)
                e_level = 0
                for pass_key in pass_ls:
                    enc_control(input_file,
                                args.cipher, pass_key)
                    input_file = f'{input_file}'f'.enc{e_level}' if input_file[-4:-1] != "enc" else f'{input_file[:-1]}'f'{e_level}'
                    e_level += 1

                # Clean intermediary files
                _clean_(input_file)

            elif args.passphrase:
                enc_control(input_file, args.cipher, args.passphrase)

        # Handle if passphrase or a password list file is provided
        if os.path.isfile(input_file) and (args.passphrase or args.pass_list):
            if args.pass_list:
                pass_ls = get_keys(args.pass_list)
                e_level = 0
                for pass_key in pass_ls:
                    init = HandleFiles(input_file, pass_key)
                    init.encrypt_file()
                    input_file = f'{input_file}'f'.enc{e_level}' if input_file[-4:-1] != "enc" else f'{input_file[:-1]}'f'{e_level}'
                    e_level += 1

                # Clean intermediary files
                _clean_(input_file)

            elif args.passphrase:
                init = HandleFiles(args.input_file, args.passphrase)
                init.encrypt_file()

        elif os.path.isdir(input_file) and (args.passphrase or args.pass_list):
            if args.pass_list:
                pass_ls = get_keys(args.pass_list)
                e_level = 0
                for pass_key in pass_ls:
                    init = HandleFolders(input_file, pass_key)
                    init.encrypt_folder()
                    input_file = f'{input_file}'f'.enc{e_level}' if input_file[-4:-1] != "enc" else f'{input_file[:-1]}'f'{e_level}'
                    e_level += 1

                # Clean intermediary files
                _clean_(input_file)

            elif args.passphrase:
                init = HandleFolders(input_file, args.passphrase)
                init.encrypt_folder()

        # Handle case where encryption passphrase is not provided
        elif os.path.isfile(input_file) and args.random_key:
            encrypt_file(input_file)

        # Handle case where passphrase is not provided but random key is provided
        elif os.path.isdir(input_file) and args.random_key:
            encrypt_folder(input_file)

        # Handle case where neither passphrase is provided nor -Rk flag is passed
        elif not args.random_key and not args.passphrase and not args.cipher and not args.pass_list:
            print("An encryption passphrase is needed otherwise try the command again with '--Rk' flag to use a randomly generated encryption key")
        logger.info("\033[1;92mDone")

    # Handle file/folder decryption
    if args.mode == 'decrypt':
        if input_file[-4:-1] != "enc":
            print("\033[1mThe file doesn not appear to be encrypted\033[0m")
            sys.exit(0)
        print("\033[1;32mComencing deryption process\033[0m")

        # Handle cipher choices
        if args.cipher:
            # Since caesar cipher needs no passphrase, ommit it
            if args.cipher.lower() == 'caesar' or args.cipher.lower() == 'caesarcipher':

                if args.pass_list:
                    print(
                        "\033[91mOops☠️ aesar cipher accepts not password list\033[0m")
                    prompt = input("Press enter to continue")
                    if prompt.lower() == 'c':
                        sys.exit()
                    else:
                        pass
                args.passphrase = None
                args.random_key = None
                dec_control(input_file, args.cipher, args.passphrase)
            if args.pass_list:
                pass_ls = get_keys(args.pass_list)
                e_level = int(input_file[-1:])
                print(
                    f"\033[1;93mLevel \033[92m{e_level}\033[1;93m encryption detected\033[0m")
                if e_level + 1 != len(pass_ls):
                    print("\033[31mPassword mismatch for the used encryption level\033[0m")
                    sys.exit(1)
                for pass_key in reversed(pass_ls):
                    dec_control(input_file,
                                args.cipher, pass_key)
                    input_file = f'{input_file[:-1]}'f'{e_level - 1}'
                # Clean intermediary files
                clean(input_file)

            elif args.passphrase:
                dec_control(input_file, args.cipher, args.passphrase)

        # Handle if passphrase is provided
        if os.path.isfile(input_file) and (args.passphrase or args.pass_list):
            if args.pass_list:
                pass_ls = get_keys(args.pass_list)
                e_level = int(input_file[-1:])
                print(
                    f"\033[1;93mLevel \033[92m{e_level + 1}\033[1;93m encryption detected\033[0m")
                if e_level + 1 != len(pass_ls):
                    print("\033[31mPassword mismath for the used encryption level\033[0m")
                    sys.exit(1)
                for pass_key in reversed(pass_ls):
                    init = HandleFiles(input_file, pass_key)
                    init.decrypt_file()
                    input_file = f'{input_file[:-1]}'f'{e_level - 1}'

                # Clean intermediary files
                clean(input_file)

            elif args.passphrase:
                init = HandleFiles(input_file, args.passphrase)
                init.decrypt_file()

        elif os.path.isdir(input_file) and args.passphrase:
            if args.pass_list:
                pass_ls = get_keys(args.pass_list)
                e_level = int(input_file[-1:])
                print(
                    f"\033[1;93mLevel \033[92m{e_level}\033[1;93m encryption detected\033[0m")
                if e_level + 1 != len(pass_ls):
                    print("Password mismath for the used encryption level")
                    sys.exit(1)
                for pass_key in reversed(pass_ls):
                    init = HandleFolders(input_file, pass_key)
                    init.decrypt_folder()
                    input_file = f'{input_file[:-1]}'f'{e_level - 1}'

                # Clean intermediary files
                clean(input_file)

            elif args.passphrase:
                init = HandleFolders(input_file, args.passphrase)
                init.decrypt_folder()

        # Handle case where decryption passphrase is not provided
        elif os.path.isfile(input_file) and args.random_key:
            decrypt_file(input_file, args.random_key)

        elif os.path.isdir(input_file) and args.random_key:
            decrypt_folder(input_file, args.random_key)

        # Handle case where neither passphrase is provided nor -Rk flag is passed
        elif not args.random_key and not args.passphrase and not args.cipher:
            print("A decryption passphrase is needed otherwise pass command with '--Rk' or '--cipher' flag to search for encryption key in default key file")
        logger.info("\033[1;92mDone")


if __name__ == "__main__":
    main()
