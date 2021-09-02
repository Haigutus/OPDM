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
# 2. Install needed modules -> open cmd and use command "python -m pip install --user opdm-api"    NB! needs opdm-api 0.0.9 or greater, to upgrade add flag --upgrade to install command
# 3. Update settings.py -> just open/edit with any text editor
# 4. Run the script

import OPDM
import settings


## Process
# Create connection to OPDM
service = OPDM.create_client(settings.OPDM_SERVER, username=settings.OPMD_USERNAME, password=settings.OPDM_PASSWORD)
print(f"Connection created to OPDM at {settings.OPDM_SERVER} as {settings.OPMD_USERNAME}")

# Query data from OPDM
_, response = service.query_object("RULESET")

# Remove first part of the response, it is the id of the original query
ruleset = response['sm:QueryResult']['sm:part'][1:]
print(f"Query returned {len(ruleset)} RULESET")

# Sort out the highest versio number RSL
version_dict = {int(item['opdm:OPDMObject']['pmd:version'].replace(".", "")):{"version":item['opdm:OPDMObject']['pmd:version'], "id":item['opdm:OPDMObject']['opde:Id']} for item in ruleset}
latest_RSL = version_dict[max(version_dict.keys())]
print(f"Latest RSL -> {latest_RSL}")

# Check if the install version is not the latest allready
installed_RSL = service.get_installed_ruleset_version()
print(f"Currently installed RSL -> {installed_RSL}")

if latest_RSL["version"] != installed_RSL:

    # Download latest RSL
    response = service.get_content(latest_RSL["id"], object_type="model")
    print(f"Downloaded {response['sm:GetContentResult']['sm:part'][1]['opdm:OPDMObject']['pmd:fileName']}")

    # Install latest RSL
    response = service.install_ruleset(latest_RSL["version"])
    print(f"RSL Installed {response}")

else:
    print(f"Latest RSL allready installed")
