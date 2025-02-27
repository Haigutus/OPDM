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

import os
import base64
import OPDM
import settings
import pandas
import TIME_HELPER
import aniso8601
import pytz
from datetime import datetime

target_date = "2024-10-25"
target_timehorizon = "1D"

# Create connection to OPDM
service = OPDM.create_client(settings.OPDM_SERVER, username=settings.OPDM_USERNAME, password=settings.OPDM_PASSWORD, debug=False)
print(f"Connection created to OPDM at {settings.OPDM_SERVER} as {settings.OPDM_USERNAME}")

reference_time = TIME_HELPER.reference_times[settings.OPDM_MODEL_TIME_REFERENCE](aniso8601.parse_datetime(f"{target_date}T09:30:00+02:00"))
period_start_time = reference_time + aniso8601.parse_duration(settings.OPDM_MODEL_TIME_START_DELTA)
period_end_time = reference_time + aniso8601.parse_duration(settings.OPDM_MODEL_TIME_END_DELTA)

print(period_start_time.isoformat(), period_end_time.isoformat())

start_time = period_start_time

timestamp_list = TIME_HELPER.timestamp_range(period_start_time, period_end_time, "PT1H")

query_log = []
download_log = []
responses = []

object_types = ["IGM", "CGM"]
#object_types = ["CGM"]

for object_type in object_types:
    for start_time in timestamp_list:

        scenario_date = start_time.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M")
        query = {"pmd:timeHorizon": target_timehorizon, "pmd:scenarioDate": {"operator": "is", "value": scenario_date}}

        if object_type == "CGM":
            object_type = {"operator": "is not one of", "value": "IGM,BDS,RULESET"}

        # Query data from OPDM
        query_start = datetime.utcnow()
        response = service.query_object(object_type, metadata_dict=query)
        query_end = datetime.utcnow()

        number_of_responses = len(response['sm:QueryResult']['sm:part'][1:])

        if type(response['sm:QueryResult']['sm:part']) == str:
            number_of_responses = 0

        print(f"Query returned {number_of_responses} {object_type} models for {scenario_date}")

        if number_of_responses > 0:

            query_log.append(
                {
                "id": response['sm:QueryResult']['sm:part'][0]["#text"],
                "start": query_start,
                "end": query_end,
                "object_type": object_type,
                "query": query,
                "count": number_of_responses,
                "opdm_version": response['sm:QueryResult']["@opdm-version"]
                }
            )

            models_metadata = [item["opdm:OPDMObject"] for item in response['sm:QueryResult']['sm:part'][1:]]

            # Remove first part of the response, that is not a boundary metadata, but the id of the original query
            responses.extend(models_metadata)

# Download and log
for metadata_response in responses:

    model_id = metadata_response["opde:Id"]

    # Query data from OPDM
    print(f"Downloading - {metadata_response['pmd:fileName']}")
    query_start = datetime.utcnow()
    download_response = service.get_content(model_id, object_type="model")
    query_end = datetime.utcnow()

    columns = ["pmd:modelPartReference", 'pmd:modelSize', 'pmd:creationDate', 'pmd:scenarioDate', "opde:Object-Type", "pmd:version"]

    download_log_item = {
                "start": query_start,
                "end": query_end,
                "opdm_version": download_response['sm:GetContentResult']["@opdm-version"]
                }

    for column in columns:
        download_log_item[column] = metadata_response.get(column, "")

    download_log.append(download_log_item)



models = pandas.DataFrame(responses)
print(models.columns)

#models['opde:Component'].apply(lambda x: pandas.DataFrame([model["opdm:Profile"] for model in x[0]['opde:Component']])["pmd:TSO"].dropna().unique())

columns_to_export = ["pmd:modelPartReference", 'pmd:modelSize', 'pmd:creationDate', 'pmd:scenarioDate', "opde:Object-Type", "pmd:version", 'pmd:RulesetLibraryVersion']

columns_to_export.extend([column for column in models.columns if "-time" in column])

print(models[columns_to_export])

models[columns_to_export].to_csv(f"model-stat_{target_date}.csv")


query_stat = pandas.DataFrame(query_log)
query_stat["duration"] = (query_stat["end"] - query_stat["start"]).td.total_seconds()
query_stat.to_csv(f"query-stat_{target_date}.csv")

download_stat = pandas.DataFrame(download_log)
download_stat["duration"] = (download_stat["end"] - download_stat["start"]).td.total_seconds()
download_stat.to_csv(f"download-stat_{target_date}.csv")


# PROFILE for a CGM for 2024-07-04T21:30
# profiles = pandas.DataFrame([model["opdm:Profile"] for model in models_metadata[0]['opde:Component']])
# cgm_size = len(profiles["pmd:TSO"].dropna().unique())
# profiles[[column for column in profiles.columns if "-time" in column]].iloc[0].sort_values()
"""
pmd:file-uploaded-time                     2024-07-03T16:54:44.881416535Z
pmd:file-validation-start-time             2024-07-03T16:54:47.515515374Z
pmd:file-validation-end-time               2024-07-03T16:54:52.081439571Z
pmd:model-assembly-start-time              2024-07-03T16:54:58.711944498Z
pmd:model-assembly-end-time                2024-07-03T16:54:58.750634322Z
pmd:model-validation-start-time            2024-07-03T16:54:58.766440196Z
pmd:model-validation-end-time              2024-07-03T16:58:03.575981733Z
pmd:model-submission-start-time            2024-07-03T16:58:03.617312404Z
pmd:model-storage-request-received-time    2024-07-03T16:58:50.607300024Z
pmd:model-submission-ack-time              2024-07-03T16:58:50.607364029Z
pmd:model-publication-start-time           2024-07-03T16:59:15.180419263Z
"""
#models[["pmd:TSO", 'pmd:modelProfile']]
# models[[column for column in models.columns if "-time" in column]].iloc[-1].sort_values()
"""
pmd:file-uploaded-time              2024-07-03T16:54:50.961370541Z
pmd:file-validation-start-time      2024-07-03T16:54:55.615659512Z
pmd:file-validation-end-time        2024-07-03T16:54:57.921848558Z
pmd:model-assembly-start-time       2024-07-03T16:54:58.711944498Z
pmd:model-assembly-end-time         2024-07-03T16:54:58.750634322Z
pmd:model-validation-start-time     2024-07-03T16:54:58.766440196Z
pmd:model-validation-end-time       2024-07-03T16:58:03.575981733Z
pmd:model-publication-start-time    2024-07-03T16:59:15.180419263Z
"""

#service.get_content(profiles['pmd:fullModel_ID'].to_list())

# OPDM version to metadata
# Include all steps timestaps from profile to opdm object/model
# Provide documentation for each step
# Provide puböication end (first subscriber to confirm retrival)?