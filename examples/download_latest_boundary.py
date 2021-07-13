# Short guide
# 1. Install python -> https://www.python.org/downloads/release/python-3711/
# 2. Install needed modules -> open cmd and use command "python -m pip install --user opdm-api pandas"
# 3. Update settings
# 4. Run the script

import OPDM
import pandas
import os
import base64

## Settings
OPMD_USERNAME = "user"
OPDM_PASSWORD = "pass"
OPDM_SERVER = "https://opde.elering.sise:8443"
EXPORT_FOLDER = os.getcwd()  # Write here path to specific folder, for now it will write file to the same location from where the script is ran


## Process
# Create connection to OPDM
service = OPDM.create_client(OPDM_SERVER, username=OPMD_USERNAME, password=OPDM_PASSWORD)
print(f"Connection created to OPDM at {OPDM_SERVER} as {OPMD_USERNAME}")

# Query data from OPDM
_, response = service.query_object("BDS")

# Remove first part of the response, that is not a boundary metadata, but the id of the original query
boundaries = response['sm:QueryResult']['sm:part'][1:]
print(f"Query returned {len(boundaries)} BDS")

# Convert to dataframe for sorting out the latest boundary
boundary_data = pandas.DataFrame([x['opdm:OPDMObject'] for x in boundaries])

# Convert date and version to respective formats
boundary_data['date_time'] = pandas.to_datetime(boundary_data['pmd:scenarioDate'])
boundary_data['version'] = pandas.to_numeric(boundary_data['pmd:versionNumber'])

# Sort out official boundary
official_boundary_data = boundary_data[boundary_data["opde:Context"] == {'opde:IsOfficial': 'true'}]

# Get latest boundary meta
latest_boundary_meta = boundaries[list(official_boundary_data.sort_values(["date_time", "version"], ascending=False).index)[0]]

print("Downloading latest BDS")
# Download and save files
current_directory = os.getcwd()

for boundary_file in latest_boundary_meta['opdm:OPDMObject']['opde:Component']:

    id = boundary_file['opdm:Profile']['opde:Id']
    file_name = boundary_file['opdm:Profile']['pmd:fileName']
    file_path = os.path.join(EXPORT_FOLDER, file_name)

    print(f"Downloading {file_name} with id {id}")

    response = service.get_content(id, return_payload=True)

    with open(file_path, 'wb') as file_object:
        message64_bytes = response['sm:GetContentResult']['sm:part'][1]['opdm:Profile']['opde:Content'].encode()
        file_object.write(base64.b64decode(message64_bytes))

    print(f"Saved to {file_path}")

