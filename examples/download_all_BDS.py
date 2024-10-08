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
# 2. Install needed modules -> open cmd and use command "python -m pip install --user opdm-api pandas"
# 3. Update settings.py -> just open/edit with any text editor
# 4. Run the script

import OPDM


def download_all_bds(service):
    """Downloads all available official BDS from Central SP to OPDM local client, this is useful if BDS subscription has not been active, but new BDS have been published"""

    # Query data from OPDM
    response = service.query_object("BDS")

    # Remove first part of the response, that is not a boundary metadata, but the id of the original query
    boundaries = response['sm:QueryResult']['sm:part'][1:]
    print(f"Query returned {len(boundaries)} BDS")

    # Download and save files
    print("Downloading all official BDS")

    for boundary in boundaries:

        context = boundary['opdm:OPDMObject'].get("opde:Context")

        if context is not None and context.get("opde:IsOfficial") == "true":


            file_id = boundary['opdm:OPDMObject']['opde:Id']
            file_name = boundary['opdm:OPDMObject']['pmd:fileName']

            print(f"Downloading BDS {file_name} with id {file_id}")

            response = service.get_content(file_id, object_type="model")

            #print(response)  # DEBUG


if __name__ == '__main__':

    import settings
    # Create connection to OPDM
    service = OPDM.create_client(settings.OPDM_SERVER, username=settings.OPDM_USERNAME, password=settings.OPDM_PASSWORD)
    print(f"Connection created to OPDM at {settings.OPDM_SERVER} as {settings.OPDM_USERNAME}")
    download_all_bds(service)