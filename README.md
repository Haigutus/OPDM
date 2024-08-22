# OPDM
Python implementation of OPDM SOAP API. OPDM is used to exchange Electrical Grid Models between ENTSO-E TSO-s and RSC-s

Other relevant API-s:
 - [ECP](https://github.com/Haigutus/ECP)
 - [EDX](https://github.com/Haigutus/EDX)

# Installation

    pip install opdm-api

or

    pip install --user opdm-api

or 

    python -m pip install --user opdm-api


# Usage

## Initialise
    import OPDM

    service = OPDM.Client("https://opdm.elering.sise:8443", username="user", password="pass")

## Upload File
### Upload a file
    response = service.publication_request(file_path_or_objet)

### Upload all files in a directory
    import glob
    imort os
    
    for file_name in glob.glob1(directory_path, "*.zip"):
        service.publication_request(os.path.join(directory_path, file_name))
    
## Get File Upload/Publication Report
    publication_report = service.get_profile_publication_report(model_ID)
    
or

    publication_report = service.get_profile_publication_report(filename="uploaded_file_name.zip")

## Subscribe for Model publications
### Get available Publications
    available_publications = service.publication_list()

### Subscribe for BDS
*available publications: BDS, IGM, CGM*

    response = service.publication_subscribe("BDS")
    
### Subscribe for all IGM-s except RT

    time_horizons = [f"{item:02d}" for item in list(range(1,32))] + ["ID", "1D", "2D", "YR"]
    for time_horizon in time_horizons:
        print(f"Adding subscription for {time_horizon}")
        response = service.publication_subscribe("IGM", subscription_id=f"IGM-{time_horizon}", metadata_dict={'pmd:timeHorizon': time_horizon})
        print(response)
    
## Cancel Subscription
    response = service.publication_cancel_subscription(subscription_id)
    
## Query Data
### Model
*Model consists of multiple files*

    response = service.query_object(object_type = "IGM", metadata_dict = {'pmd:scenarioDate': '2019-07-28T00:30:00', 'pmd:timeHorizon': '1D'})

### File

    response = service.query_profile('pmd:timeHorizon': '1D', 'pmd:cgmesProfile': 'SV'})
    
### Create nice table of returned Query responses

    import pandas
    
    pandas.set_option("display.max_rows", 12)
    pandas.set_option("display.max_columns", 10)
    pandas.set_option("display.width", 1500)
    pandas.set_option('display.max_colwidth', -1)

    print(pandas.DataFrame(response['sm:QueryResult']['sm:part'][1:]))
    

## Download a File
### Download to OPDM Client and return local path to the file
    response = service.get_content(file_UUID)
    print(response['sm:GetContentResult']['sm:part'][1]['opdm:Profile']['opde:Content'])
    
### Download and Save file
    import base64
    response = service.get_content(file_UUID, return_payload=True)
    with open(f"{file_UUID}.zip", 'wb') as cgmes_file:
        report_file.write(base64.b64decode(response['sm:GetContentResult']['sm:part'][1]['opdm:Profile']['opde:Content'].encode()))
        
## Manage Rulesets

### List available Ruleset
    service.list_available_rulesets()
    
### Install Ruleset
    service.install_rulesets(version="2.0.122")
    
### Get installed Ruleset version
    service.get_installed_ruleset_version()
    
### Reset Ruleset
    service.reset_ruleset()

    
## [Examples](https://github.com/Haigutus/OPDM/tree/main/examples)
 - [Download latest Boundary](https://github.com/Haigutus/OPDM/blob/main/examples/download_latest_BDS.py)
 - [Download all Boundaries](https://github.com/Haigutus/OPDM/blob/main/examples/download_all_BDS.py)
 - [Install latest Rule Set](https://github.com/Haigutus/OPDM/blob/main/examples/install_latest_RSL.py)
 - [Upload IGM](https://github.com/Haigutus/OPDM/blob/main/examples/upload_IGMs.py)
    
        

    
    
