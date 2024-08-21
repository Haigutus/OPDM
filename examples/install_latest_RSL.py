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


# Short guide
# 1. Install python -> https://www.python.org/downloads/release/python-3711/
# 2. Install needed modules -> open cmd and use command "python -m pip install --user opdm-api"    NB! needs opdm-api 0.0.11 or greater, to upgrade add flag --upgrade to install command
# 3. Update settings.py -> just open/edit with any text editor
# 4. Run the script

import OPDM
import logging
import sys
from time import sleep

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def install_latest_rsl(service, list_of_rsl_nodes_eic):
    """Installs the lates available (On remote SP) ruleset library to local client"""

    ## Process
    # Query data from OPDM

    response = service.query_object("RULESET")

    # Remove first part of the response, it is the id of the original query
    ruleset = response['sm:QueryResult']['sm:part'][1:]
    logger.info(f"Query returned {len(ruleset)} RULESET")

    if len(ruleset) == 0:
        logger.error(f"Empty Query returned for RULESET, use this query ID on SP side and Client Elastic/Kibana debugging")
        return

    # Sort out the highest version number RSL
    version_dict = {int(item['opdm:OPDMObject']['pmd:version'].replace(".", "")):{"version":item['opdm:OPDMObject']['pmd:version'], "id":item['opdm:OPDMObject']['opde:Id']} for item in ruleset if item ['opdm:OPDMObject']["opde:Component"]["opdm:Profile"]["opde:Context"]["opde:EDXContext"]["opde:SenderToolboxCode"] in list_of_rsl_nodes_eic}
    latest_RSL = version_dict[max(version_dict.keys())]
    logger.info(f"Latest Official RSL -> {latest_RSL}")

    # Check if the installed version is not the latest already
    try:
        installed_RSL = service.get_installed_ruleset_version()
        logger.info(f"INFO - Currently installed RSL -> {installed_RSL}")
    except Exception as error:
        logger.error("Could not get Currently installed RSL, possible fix - make sure the OPDM user is with Admin rights")
        logger.error(f"Trace -> {error}")
        return


    if latest_RSL["version"] != installed_RSL:

        # Download latest RSL
        try:
            response = service.get_content(latest_RSL["id"], object_type="model")
            logger.info(f"Downloaded {response['sm:GetContentResult']['sm:part'][1]['opdm:OPDMObject']['pmd:fileName']}")

        except KeyError:
            logger.error("Could not get GetContent response from OPDM SP")
            return


        if latest_RSL["version"] not in [rsl["version"] for rsl in service.list_available_rulesets()]:
            wait_time = 10 #s
            logger.warning(f"RSL {latest_RSL['version']} not available for installation, waiting {wait_time}s to try once more")
            sleep(wait_time)


        if latest_RSL["version"] in [rsl["version"] for rsl in service.list_available_rulesets()]:

            # Install latest RSL
            try:
                response = service.install_ruleset(latest_RSL["version"])
                logger.info(f"RSL {latest_RSL['version']} Installed {response}")
            except Exception as error:
                logger.error("Could not install RSL, possible fix - check that OPDM Ealsitc Search is well functioning and correctly configured")
                logger.error(f"Trace -> {error}")
                return


        else:
            logger.error(f"RSL {latest_RSL['version']} not available for installation, possible fix - check that Ealsitc Search is well functioning and correctly configured")

    else:
        logger.info(f"Latest RSL allready installed")


if __name__ == '__main__':
    # Create connection to OPDM
    import settings
    service = OPDM.create_client(settings.OPDM_SERVER, username=settings.OPDM_USERNAME, password=settings.OPDM_PASSWORD)
    logger.info(f"Connection created to OPDM at {settings.OPDM_SERVER} as {settings.OPDM_USERNAME}")
    install_latest_rsl(service, settings.RSL_OFFICIAL_NODES)
