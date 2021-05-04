# OPDM
Python implementation of OPDM SOAP API. OPDM is used to exchange Electrical Grid Models between ENTSO-E TSO-s and RSC-s

# Installation

    pip install opdm-api

or

    pip install --user opdm-api

or 

    python -m pip install --user opdm-api


# Usage

## Initialise
    import OPDM

    service = OPDM.create_client("https://opdm.elering.sise:8443", username="user", password="pass")

## Upload File
### Upload a file
    response = service.publication_request(file_path_or_objet)

### Upload all files in a directory
    import glob
    imort os
    
    for file_name in glob.glob1(directory_path, "*.zip"):
        service.publication_request(os.path.join(directory_path, file_name))
    
## Get File Upload/Publication Report
    publication_report = get_profile_publication_report(model_ID)
    
or

    publication_report = get_profile_publication_report(filename="uploaded_file_name.zip")

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
    response = publication_cancel_subscription(subscription_id)
    
## Query Data
### Model
*Model consists of multiple files*

    query_id, response = service.query_object(object_type = "IGM", metadata_dict = {'pmd:scenarioDate': '2019-07-28T00:30:00', 'pmd:timeHorizon': '1D'})

### File

    query_id, response = service.query_profile('pmd:timeHorizon': '1D', 'pmd:cgmesProfile': 'SV'})
    
### Create nice table of returned Query responses

    import pandas
    
    pandas.set_option("display.max_rows", 12)
    pandas.set_option("display.max_columns", 10)
    pandas.set_option("display.width", 1500)
    pandas.set_option('display.max_colwidth', -1)

    print(pandas.DataFrame(response['sm:QueryResult']['sm:part'][1:]))
    
### Query latest boundary

    import pandas
    
    # Query data from OPDM
    _, response = service.query_object("BDS")
    
    boundaries = response['sm:QueryResult']['sm:part'][1:]

    # Convert to dataframe for sorting out the latest boundary
    boundary_data = pandas.DataFrame([x['opdm:OPDMObject'] for x in boundaries])

    # Convert date and version to respective formats
    boundary_data['date_time'] = pandas.to_datetime(boundary_data['pmd:scenarioDate'])
    boundary_data['version'] = pandas.to_numeric(boundary_data['pmd:versionNumber'])

    # Sort out official boundary
    official_boundary_data = boundary_data[boundary_data["opde:Context"] == {'opde:IsOfficial': 'true'}]

    # Get latest boundary meta
    latest_boundary_meta = boundaries[list(official_boundary_data.sort_values(["date_time", "version"], ascending=False).index)[0]]

## Download a File
### Download to OPDM Client and return local path to the file
    response = service.get_content(file_UUID)
    print(response['sm:GetContentResult']['sm:part'][1]['opdm:Profile']['opde:Content'])
    
### Download and Save file
    response = service.get_content(file_UUID, return_payload=True)
    with open(f"{file_UUID}.zip", 'wb') as cgmes_file:
        report_file.write(response['sm:GetContentResult']['sm:part'][1]['opdm:Profile']['opde:Content'])
        

    
    
