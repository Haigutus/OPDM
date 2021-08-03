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
import pandas
import os
import base64
import settings


## Process
# Create connection to OPDM
service = OPDM.create_client(settings.OPDM_SERVER, username=settings.OPMD_USERNAME, password=settings.OPDM_PASSWORD)
print(f"Connection created to OPDM at {settings.OPDM_SERVER} as {settings.OPMD_USERNAME}")

# Query data from OPDM
model_type = "CGM"
metadata = {'pmd:scenarioDate': '2021-08-02T09:30:00', 'pmd:timeHorizon': '1D'}

_, response = service.query_object(model_type, metadata_dict = metadata)

# Remove first part of the response, that is not a boundary metadata, but the id of the original query
models = response['sm:QueryResult']['sm:part'][1:]
print(f"Query returned {len(models)} {model_type}")

# Download and save files
print(f"Downloading {model_type} models")

for model in models:

    for cimxml_file in model['opdm:OPDMObject']['opde:Component']:

        file_id = cimxml_file['opdm:Profile']['opde:Id']
        file_name = cimxml_file['opdm:Profile']['pmd:fileName']
        file_path = os.path.join(settings.EXPORT_FOLDER, file_name)

        print(f"Downloading {file_name} with ID: {file_id}")

        response = service.get_content(file_id, return_payload=True)

        with open(file_path, 'wb') as file_object:
            message64_bytes = response['sm:GetContentResult']['sm:part'][1]['opdm:Profile']['opde:Content'].encode()
            file_object.write(base64.b64decode(message64_bytes))

        print(f"Saved to {file_path}")

