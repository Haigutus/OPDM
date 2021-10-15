# MIT License
#
# Copyright (c) 2021 Kristjan Vilgo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
from getpass import getpass

import OPDM
from subscribe_for_BDS import subscribe_for_bds
from subscribe_for_RSL import subscribe_for_rsl
from download_all_BDS import download_all_bds
from install_latest_RSL import install_latest_rsl
from subscribe_for_CGMs import subscribe_for_cgms
from subscribe_for_IGMs import subscribe_for_igms
from settings import RSL_OFFICIAL_NODES

def yes_no(question=""):
    yes_list = ["y", "Y", "yes", "Yes"]
    answer = input(f"{question} Yes = {yes_list}; No = Enter  \n")

    return answer in yes_list

parser = argparse.ArgumentParser(description="""Commandline tool to help users to configure fresh installations of OPDM client""",
                                 epilog="""Copyright (c) Kristjan Vilgo 2021; Licence: MIT""")

opdm_client_help = 'OPDM client base url with port, for example -> https://opde.elering.sise:8443\n'
username_help = 'OPDM User Name with Administrator rights\n'
password_help = 'OPDM password\n'
parser.add_argument('--opdm_client', type=str, help=opdm_client_help)
parser.add_argument('--username', type=str, help=username_help)
parser.add_argument('--password', type=str, help=password_help)
parser.add_argument('--subscribe_rsl', action='store_true', help=subscribe_for_rsl.__doc__)
parser.add_argument('--subscribe_bds', action='store_true', help=subscribe_for_bds.__doc__)
parser.add_argument('--install_rsl', action='store_true', help=install_latest_rsl.__doc__)
parser.add_argument('--download_bds', action='store_true', help=download_all_bds.__doc__)
parser.add_argument('--subscribe_igm', action='store_true', help=subscribe_for_igms.__doc__)
parser.add_argument('--subscribe_cgm', action='store_true', help=subscribe_for_cgms.__doc__)
parser.add_argument('--silent', action='store_true', help='Set flag to use this tool in a automated manner without interactive user input')

parser.print_usage()

arg = parser.parse_args()


if not arg.opdm_client and  arg.silent == False:
    arg.opdm_client = str(input(opdm_client_help))

if not arg.username and  arg.silent == False:
    arg.username = str(input(username_help))

if not arg.password and  arg.silent == False:
    arg.password = str(getpass(password_help + " NB! Typed characters will not be displayed\n"))


service = OPDM.create_client(arg.opdm_client, username=arg.username, password=arg.password)
print(f"Connection created to OPDM at {arg.opdm_client} as {arg.username}")


if arg.install_rsl == False and arg.silent == False:
    arg.install_rsl = yes_no("Would you like to istall latest QoCDC ruleset?")

if arg.install_rsl: install_latest_rsl(service, RSL_OFFICIAL_NODES)


if arg.subscribe_rsl == False and arg.silent == False:
    arg.subscribe_rsl = yes_no("Would you like to add subscription for QoCDC rulests?")

if arg.subscribe_rsl: subscribe_for_rsl(service)


if arg.download_bds == False and arg.silent == False:
    arg.download_bds = yes_no("Would you like to download all official BDS to your OPDM client?")

if arg.download_bds: download_all_bds(service)


if arg.subscribe_bds == False and arg.silent == False:
    arg.subscribe_bds = yes_no("Would you like to add subscription for BDS?")

if arg.subscribe_bds: subscribe_for_bds(service)


if arg.subscribe_igm == False and arg.silent == False:
    arg.subscribe_igm = yes_no("Would you like to add subscription for all IGM-s except RT (real time) [Relevant for RSC-s]?")

if arg.subscribe_igm: subscribe_for_igms(service)


if arg.subscribe_cgm == False and arg.silent == False:
    arg.subscribe_cgm = yes_no("Would you like to add subscription for CGM-s?")

if arg.subscribe_cgm: subscribe_for_cgms(service)


print("All done")






