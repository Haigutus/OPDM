# -------------------------------------------------------------------------------
# Name:        OPDM_API
# Purpose:     Expose OPDM functionality in python
#
# Author:      kristjan.vilgo
#
# Created:     31.07.2018
# Copyright:   (c) kristjan.vilgo 2018
# Licence:     MIT
# -------------------------------------------------------------------------------
from requests import Session
from zeep import Client as SOAPClient
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
from zeep.plugins import HistoryPlugin

from lxml import etree

import os
import uuid

import xmltodict

import urllib3

from OPDM import __version__ as package_version

import logging
logger = logging.getLogger(__name__)


def get_element(element_path, xml_tree):
    element = xml_tree.find(element_path, namespaces=xml_tree.nsmap)
    return element


def add_xml_elements(xml_string, parent_element_url, metadata_dict):

    if type(xml_string) is str:
        xml_string = xml_string.encode("UTF-8")

    xml_tree = etree.fromstring(xml_string)
    metadata_element = get_element(parent_element_url, xml_tree=xml_tree)

    for key, value in metadata_dict.items():

        namespace, element_name = key.split(":")

        element_full_name = "{{{}}}{}".format(xml_tree.nsmap[namespace], element_name)

        element = etree.SubElement(metadata_element, element_full_name, nsmap=xml_tree.nsmap)

        if type(value) == str:
            element.text = value

        if type(value) == dict:
            element.text = value["value"]
            element.attrib["operator"] = value["operator"]

    return etree.tostring(xml_tree, pretty_print=True)


class Client:

    def __init__(self, server, username="", password="", debug=False, verify=False):

        """At minimum server address or IP must be provided
        service = create_client(<server_ip_or_address>)"""

        self.debug = debug
        self.history = HistoryPlugin()
        self.API_VERSION = package_version

        service_wsdl = '{}/opdm/cxf/OPDMSoapInterface?wsdl'.format(server)
        ruleset_wsdl = '{}/opdm/cxf/OPDMSoapInterface/RuleSetManagementService?wsdl'.format(server)

        session = Session()

        # Use this only for testing, correct way is to add OPDM certs to trust store
        if not verify:
            urllib3.disable_warnings()
            session.verify = False

        # Set up client
        self.client = SOAPClient(service_wsdl, transport=Transport(session=session), wsse=UsernameToken(username=username, password=password))
        self.ruleset_client = SOAPClient(ruleset_wsdl, transport=Transport(session=session), wsse=UsernameToken(username=username, password=password))

        if self.debug:
            self.client.plugins = [self.history]
            self.ruleset_client.plugins = [self.history]
            logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.DEBUG)

    def _print_last_message_exchange(self):
        """Prints out last sent and received SOAP messages"""

        messages = {"SENT":     self.history.last_sent,
                    "RECEIVED": self.history.last_received}
        print("-" * 50)

        for message in messages:

            print(f"### {message} HTTP HEADER ###")
            print('\n' * 1)
            print(messages[message]["http_headers"])
            print('\n' * 1)
            print(f"### {message} HTTP ENVELOPE START ###")
            print('\n' * 1)
            print(etree.tostring(messages[message]["envelope"], pretty_print=True).decode())
            print(f"### {message} HTTP ENVELOPE END ###")
            print('\n' * 1)

        print("-" * 50)

    class Operations:

        QueryObject = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                        <sm:Query xmlns:opde="http://entsoe.eu/opde/ObjectModel/1/0"
                                  xmlns:pmd="http://entsoe.eu/opdm/ProfileMetaData/1/0"
                                  xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0"
                                  xmlns:opdm="http://entsoe.eu/opdm/ObjectModel/1/0">
                        <sm:part name="name">{query_id}</sm:part>
                        <sm:part name="query" type="opde:MetaDataPattern">
                            <opdm:OPDMObject>
                                <opde:Components/>
                                <opde:Dependencies/>
                            </opdm:OPDMObject>
                        </sm:part>
                        </sm:Query>"""

        QueryProfile = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                        <sm:Query xmlns:opde="http://entsoe.eu/opde/ObjectModel/1/0"
                                  xmlns:pmd="http://entsoe.eu/opdm/ProfileMetaData/1/0"
                                  xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0"
                                  xmlns:opdm="http://entsoe.eu/opdm/ObjectModel/1/0">
                        <sm:part name="name">{query_id}</sm:part>
                        <sm:part name="query" type="opde:MetaDataPattern">
                            <opdm:Profile/>
                        </sm:part>
                    </sm:Query>"""

        GetContentResult = """<?xml version="1.0" encoding="UTF-8"?>
                                <sm:GetContent xmlns="http://entsoe.eu/opde/ServiceModel/1/0"
                                               xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0"
                                               xmlns:opde="http://entsoe.eu/opde/ObjectModel/1/0"
                                               xmlns:opdm="http://entsoe.eu/opdm/ObjectModel/1/0">
                                    <sm:part name="content-return-mode">{return_mode}</sm:part><!-- PAYLOAD or FILE -->
                                    {identifier_parts}
                                </sm:GetContent>"""


        CreateSubscription = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                                <sm:CreateSubscription xmlns:opdm="http://entsoe.eu/opdm/ObjectModel/1/0" xmlns:pmd="http://entsoe.eu/opdm/ProfileMetaData/1/0" xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0" opdm-version="">
                                   <sm:part name="subscription" type="opde:Subscription">
                                      <opdm:Subscription>
                                         <opdm:SubscriptionID>{subscription_id}</opdm:SubscriptionID>
                                         <opdm:PublicationID>{publication_id}</opdm:PublicationID>
                                         <opdm:Mode>{subscription_mode}</opdm:Mode>
                                         <opdm:MetadataPattern>
                                            <opdm:OPDMObject>
                                               <pmd:Object-Type>{object_type}</pmd:Object-Type>
                                            </opdm:OPDMObject>
                                         </opdm:MetadataPattern>
                                      </opdm:Subscription>
                                   </sm:part>
                                </sm:CreateSubscription>"""

        # METADTA: The default mode. No specific action and the OPDM application will keep the OPDMObject metadata as received.
        # DIRECT_CONTENT: The OPDM application will request the content of the profiles building the OPDMObject.
        # FULL_DEPENDENCIES: The OPDM application will request the content of the profiles building the OPDMObject and the content of all its dependencies.


        StartSubscription = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                                <sm:StartSubscription xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0" opdm-version="">
                                   <sm:part name="subscriptionID">{subscription_id}</sm:part>
                                </sm:StartSubscription>"""

        StopSubscription = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                                <sm:StopSubscription xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0" opdm-version="">
                                   <sm:part name="subscriptionID">{subscription_id}</sm:part>
                                </sm:StopSubscription>"""

        UpdateSubscription = "NOT_IMPLEMENTED"

        DeleteSubscription = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                                <sm:DeleteSubscription xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0" opdm-version="">
                                   <sm:part name="subscriptionID">{subscription_id}</sm:part>
                                </sm:DeleteSubscription>"""

        GetSubscriptions = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                                <sm:GetSubscriptions xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0" opdm-version="">
                                   <sm:part name="filter">{subscription_status}</sm:part>
                                </sm:GetSubscriptions>"""

        # ALL: get all  subscriptions.
        # SUBSCRIBED: get only subscriptions with status “Subscribed”.
        # NOT_SUBSCRIBED: get only subscriptions with status “Not subscribed”.
        # PENDING: get only subscriptions with status “Pending”.
        # DELETED: get only subscriptions with status “Deleted”.

        PublicationsSubscriptionList = """<?xml version="1.0" encoding="UTF-8"?>
                                          <sm:PublicationsSubscriptionList xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0">
                                                <sm:part name="listType">AVAILABLE_PUBLICATIONS</sm:part>
                                          </sm:PublicationsSubscriptionList>"""

        GetProfilePublicationReport = """<sm:GetProfilePublicationReport
                                                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                                            xsi:schemaLocation="http://entsoe.eu/opde/ServiceModel/1/0 ../scheme/opde-service-model.xsd"
                                                            xmlns="http://entsoe.eu/opde/ServiceModel/1/0"
                                                            xmlns:opde="http://entsoe.eu/opde/ObjectModel/1/0"
                                                            xmlns:sm="http://entsoe.eu/opde/ServiceModel/1/0"
                                                            xmlns:pmd="http://entsoe.eu/opdm/ProfileMetaData/1/0"
                                                            xmlns:opdm="http://entsoe.eu/opdm/ObjectModel/1/0">
                                                        <sm:part type="opde:MetaDataPattern">
                                                            <opdm:Profile>
                                                            </opdm:Profile>
                                                        </sm:part>
                                                    </sm:GetProfilePublicationReport>
                                                    """

    def execute_operation(self, operation_xml, return_raw_response=False):
        """ExecuteOperation(payload: xsd:base64Binary) -> return: ns0:resultDto"""
        if type(operation_xml) is str:
            operation_xml = operation_xml.encode("UTF-8")

        response = self.client.service.ExecuteOperation(operation_xml)

        if self.debug:
            logger.debug(etree.tostring(response, pretty_print=True))

        if not return_raw_response:
            response = xmltodict.parse(etree.tostring(response, pretty_print=True),
                                       xml_attribs=True,
                                       force_list=('sm:part',))

        return response

    def publication_request(self, file_path_or_file_object, content_type="CGMES"):
        """PublicationRequest(dataset: ns0:opdeFileDto) -> return: ns0:resultDto,
        ns0:opdeFileDto(id: xsd:string, type: xsd:string, content: xsd:base64Binary)"""

        if type(file_path_or_file_object) == str:

            with open(file_path_or_file_object, "rb") as file_object:
                file_string = file_object.read()

            file_name = os.path.basename(file_path_or_file_object)

        else:
            file_string = file_path_or_file_object.getvalue()
            file_name = file_path_or_file_object.name

        payload = {"id": file_name, "type": content_type, "content": file_string}

        response = self.client.service.PublicationRequest(payload)

        return response

    def get_profile_publication_report(self, model_id="", filename=""):

        if model_id == "" and filename == "":
            logger.error("model_id or filename needs to be defined to get the report")
            return None

        get_profile_publication_report = self.Operations.GetProfilePublicationReport

        if model_id != "":
            logger.debug(f"Query made by model ID -> {model_id}")
            get_profile_publication_report = add_xml_elements(get_profile_publication_report, ".//opdm:Profile", {"pmd:modelId": model_id})

        if filename != "":
            logger.debug(f"Query made by file name -> {filename}")
            get_profile_publication_report = add_xml_elements(get_profile_publication_report, ".//opdm:Profile", {"pmd:filename": filename})

        # import pandas
        # pandas.DataFrame(status['sm:GetProfilePublicationReportResult']['sm:part'][0]['opdm:PublicationReport']['publication:history']['publication:step'])

        return self.execute_operation(get_profile_publication_report)

    def query_object(self, object_type="IGM", metadata_dict=None, components=None, dependencies=None, raw_response=False):
        """
        object_type ->IGM, CGM, BDS
        metadata_dict_example_1 = {'pmd:cgmesProfile': 'SV', 'pmd:scenarioDate': '2018-12-07T00:30:00+01:00', 'pmd:timeHorizon': '1D'}
        metadata_dict_example_2 = {"pmd:timeHorizon": "YR", "pmd:scenarioDate": {"operator": "is after", "value": "2021-12-30T00:00:00"}}
        components_example = [{"opde:Component":"45955-94458-854789358-8557895"}, {"opde:Component":"45955-94458-854789358-8557895"}]
        dependencies_example = [{"opde:DependsOn":"45955-94458-854789358-8557895"}, {"opde:Supersedes":"45955-94458-854789358-8557895"}, {"opde:Replaces":"45955-94458-854789358-8557895"}]

        Metadata Operators

        Operators used to filter datasets based on metadata conditions.

        1. does not exist
            - Types: Date, String
            - Description: Used to return datasets that do not contain the given metadata.
            - Value: No value is required for this operator.

        2. exist
            - Types: Date, String
            - Description: Used to return datasets that contain the given metadata.
            - Value: No value is required for this operator.

        3. is not one of
            - Types: Date, String
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value is not among the mentioned ones.
            - Value: This operator requires at least one value.

        4. is one of
            - Types: Date, String
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value is among the mentioned ones.
            - Value: This operator requires at least one value.

        5. is
            - Types: Date, String
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value is equal to the given value.
            - Value: This operator requires one and only one value.

        6. is not
            - Types: Date, String
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value is not equal to the given value.
            - Value: This operator requires one and only one value.

        7. is between
            - Types: Date
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value belongs to the given range.
            - Value: This operator requires exactly two values.

        8. is not between
            - Types: Date
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value does not belong to the given range.
            - Value: This operator requires exactly two values.

        9. is before
            - Types: Date
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value is before the given value.
            - Value: This operator requires one and only one value.

        10. is after
            - Types: Date
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value is after the given value.
            - Value: This operator requires one and only one value.

        11. contains
            - Types: String
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value contains the given value. The introduced value should not contain either asterisk (*) or white spaces.
            - Value: This operator requires one and only one value.

        12. match regex
            - Types: String
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value matches the given regex.
            - Value: This operator requires one and only one value.

        13. match wildcard
            - Types: String
            - Description: Used to return datasets that contain the given metadata, and verifying the following condition: the metadata value matches the given expression. Using this operator, the user can use expressions that contain logical operators (and/or) and asterisks (*).
            - Value: This operator requires one and only one value.
        """

        query_id = "py_opdm-api{api_version}_{uuid}".format(uuid=uuid.uuid4(), api_version=self.API_VERSION)
        logger.debug(f"Executing query with ID: {query_id}")

        query_object = self.Operations.QueryObject.format(query_id=query_id)

        # Use default object type or passed in object type from function call, if not defined directly in query metadata

        if not metadata_dict:
            metadata_dict = {}
        
        if not metadata_dict.get("pmd:Object-Type"):
            metadata_dict["pmd:Object-Type"] = object_type

        query_object = add_xml_elements(query_object, ".//opdm:OPDMObject", metadata_dict)

        if components:
            for component in components:
                query_object = add_xml_elements(query_object, ".//opde:Components", component)

        if dependencies:
            for dependency in dependencies:
                query_object = add_xml_elements(query_object, ".//opde:Dependencies", dependency)

        logger.debug(query_object)

        return self.execute_operation(query_object, return_raw_response=raw_response)


    def query_profile(self, metadata_dict, raw_response=False):

        """metadata_dict_example = {'pmd:cgmesProfile': 'SV', 'pmd:scenarioDate': '2018-12-07T00:30:00', 'pmd:timeHorizon': '1D'}"""

        query_id = "py_opdm-api{api_version}_{uuid}".format(uuid=uuid.uuid4(), api_version=self.API_VERSION)
        logger.debug(f"Executing query with ID: {query_id}")

        query_profile = self.Operations.QueryProfile.format(query_id=query_id)
        query_profile = add_xml_elements(query_profile, ".//opdm:Profile", metadata_dict)

        logger.debug(query_profile)

        return self.execute_operation(query_profile, return_raw_response=raw_response)

    def get_content(self, content_id, return_payload=False, object_type="file", raw_response=False):
        """
            Downloads one or multiple files or models from OPDM Service Provider to OPDM Client local storage.

            Args:
                content_id (Union[str, List[str]]): The identifier(s) of the content to download. Can be a single string or a list of strings.
                return_payload (bool): If True, returns the file content directly. Defaults to False.
                object_type (str): Type of object to retrieve. Supported types are "file" and "model". Defaults to "file".
                raw_response (bool): If True, returns the raw response from the service. Defaults to False.

            Returns:
                Dict: A dictionary containing metadata and either the filename or the content itself based on `return_payload`.

            Raises:
                ValueError: If an unsupported `object_type` is provided.

            Example:
                result = get_content('<mRID>', return_payload=True)
                content = result['sm:GetContentResult']['sm:part'][1]['opdm:Profile']['opde:Content']
            """

        return_mode = "PAYLOAD" if return_payload else "FILE"
        logger.debug(f"Return mode: {return_mode}")

        # Map object types
        object_types = {"file": "Profile", "model": "OPDMObject"}
        if object_type not in object_types:
            raise ValueError(f"Unsupported object_type. Choose from {list(object_types.keys())}")

        # Ensure list of ID-s
        if type(content_id) is str:
            content_id = [content_id]

        identifier_parts = [
            f"""
                <sm:part name="identifier" type="opde:ShortMetaData">
                    <opdm:{object_types[object_type]}>
                        <opde:Id>{identifier}</opde:Id>
                    </opdm:{object_types[object_type]}>
                </sm:part>
                """ for identifier in content_id
        ]

        identifier_parts_str = '\n'.join(identifier_parts)

        get_content_result = self.Operations.GetContentResult.format(identifier_parts=identifier_parts_str, return_mode=return_mode)

        return self.execute_operation(get_content_result, return_raw_response=raw_response)

    def publication_list(self):

        return self.execute_operation(self.Operations.PublicationsSubscriptionList)

    def subscription_list(self, subscription_status="ALL"):

        """
        ALL: get all  subscriptions.
        SUBSCRIBED: get only subscriptions with status “Subscribed”.
        NOT_SUBSCRIBED: get only subscriptions with status “Not subscribed”.
        PENDING: get only subscriptions with status “Pending”.
        DELETED: get only subscriptions with status “Deleted”.
        """

        subscription_statuses = ["ALL", "SUBSCRIBED", "NOT_SUBSCRIBED", "PENDING", "DELETED"]

        if subscription_status not in subscription_statuses:
            logger.warning(f"Status '{subscription_status}' not supported, supported types are: {subscription_statuses}")
            return None

        get_subscriptions = self.Operations.GetSubscriptions.format(subscription_status=subscription_status)

        return self.execute_operation(get_subscriptions)


    def publication_subscribe(self, object_type="BDS", subscription_id="", publication_id="", mode="DIRECT_CONTENT", metadata_dict=None, raw_response=False):
        """
        Set up subscription for data models. By default sets up subscription for BDS

        objec_type -> IGM, CGM, BDS
        subscription_id -> if empty string, uuid4 is assigned as id
        publication_id -> if empty string, at random suitable publication is selected
        mode -> META, DIRECT_CONTENT, FULL
        metadata_dict_example = {'pmd:TSO': 'ELERING', 'pmd:timeHorizon': '1D'}
        """
        # Get available publications
        available_publications = self.publication_list()['sm:PublicationsSubscriptionListResult']['sm:part'][0]['opdm:PublicationsList']['opdm:Publication']

        object_types = {item['opde:messageType']["@v"].split("-")[-1]: item['opde:publicationID']["@v"] for item in available_publications}

        if object_type not in object_types.keys():
            logger.warning(f"ObjectType '{object_type}' not supported, supported types are: {object_types}")
            return None

        modes = ["META", "DIRECT_CONTENT", "FULL"]
        if mode not in modes:
            logger.warning(f"Mode '{mode}' not supported, supported modes are: {modes}")
            return None

        if subscription_id == "":
            subscription_id = str(uuid.uuid4())

        if publication_id == "":
            publication_id = object_types[object_type]

        publications_ids = [item['opde:publicationID']["@v"] for item in available_publications]
        if publication_id not in publications_ids:
            logger.error(f"Publication '{publication_id}' not supported, supported modes are: {publications_ids}")
            return None

        create_subscription = self.Operations.CreateSubscription.format(subscription_id=subscription_id,
                                                                        publication_id=publication_id,
                                                                        subscription_mode=mode,
                                                                        object_type=object_type)

        if metadata_dict:
            create_subscription = add_xml_elements(create_subscription, ".//opdm:OPDMObject", metadata_dict)

        return self.execute_operation(create_subscription)

    def publication_cancel_subscription(self, subscription_id):
        """Cancel subscription by subscription ID"""

        logger.debug(f"Cancelling subscription with ID -> {subscription_id}")

        stop_response = self.execute_operation(self.Operations.StopSubscription.format(subscription_id=subscription_id))
        delete_response = self.execute_operation(self.Operations.DeleteSubscription.format(subscription_id=subscription_id))

        return delete_response

    def get_installed_ruleset_version(self):
        """Returns a string with the latest ruleset version"""
        return self.ruleset_client.service.GetInstalledRuleSetVersion()

    def list_available_rulesets(self):
        """Returns a list of available rulesets"""
        return self.ruleset_client.service.ListAvailableRuleSets()

    def install_ruleset(self, version=None):
        """Install ruleset library by providing the library version as a string. To get available ruleset libraries use list_available_rulesets()"""
        return self.ruleset_client.service.Install(Version=version)

    def reset_ruleset(self):
        """Reset ruleset library"""
        return self.ruleset_client.service.Reset()


if __name__ == '__main__':

    server = 'https://opde.elering.sise:8443'

    service = Client(server, username="", password="", debug=False)

    ## Subscription example BDS
    #response = service.publication_subscribe("BDS")

    ## Subscription example IGM-s wo RT
    # time_horizons = [f"{item:02d}" for item in list(range(1,32))] + ["ID", "1D", "2D", "YR"]
    # for time_horizon in time_horizons:
    #     print(f"Adding subscription for {time_horizon}")
    #     response = service.publication_subscribe("IGM", subscription_id=f"IGM-{time_horizon}", metadata_dict={'pmd:timeHorizon': time_horizon})
    #     print(response)


    # Query model part example

##    # Available profile meta
##    """
   # "pmd:content-reference": "CGMES/1D/ELERING/20190712/93000/SV/20190712T0930Z_1D_ELERING_SV_001.zip",
   # "pmd:conversationId": "-581868906",
   # "pmd:fileName": "20190712T0930Z_1D_ELERING_SV_001.zip",
   # "pmd:isFullModel": "true",
   # "pmd:TSO": "ELERING",
   # "pmd:modelingAuthoritySet": "http://www.elering.ee/OperationalPlanning",
   # "pmd:timeHorizon": "1D",
   # "pmd:contentType": "CGMES",
   # "pmd:modelProfile": "http://entsoe.eu/CIM/StateVariables/4/1",
   # "pmd:validFrom": "20190712T0930Z",
   # "pmd:modelid": "3c09a995-d250-460d-9b34-09f75fc2cade",
   # "pmd:creationDate": "2019-07-11T18:16:46Z",
   # "pmd:cgmesProfile": "SV",
   # "pmd:version": "001",
   # "pmd:fullModel_ID": "3c09a995-d250-460d-9b34-09f75fc2cade",
   # "pmd:modelPartReference": "ELERING",
   # "pmd:description": "ELERING AP--Base-Network",
   # "pmd:profileSize": "1282790",
   # "pmd:scenarioDate": "2019-07-12T09:30:00Z",
   # "pmd:versionNumber": "001"
##    """
##
##
##    metadata_dict = {'pmd:scenarioDate': '2019-07-12T09:30:00', 'pmd:timeHorizon': '1D', 'pmd:cgmesProfile': 'SV'}
##
##    message_id, response = service.query_profile(metadata_dict)
##    print(json.dumps(response, indent = 4))
##
##    # Create nice table view
##    import pandas
##    pandas.set_option("display.max_rows", 12)
##    pandas.set_option("display.max_columns", 10)
##    pandas.set_option("display.width", 1500)
##    #pandas.set_option('display.max_colwidth', -1)

##    response['sm:QueryResult']['sm:part'].pop(0)
##    print(pandas.DataFrame(response['sm:QueryResult']['sm:part']))


    # Model submission example

    # file_path = r"\\elering.sise\teenused\NMM\data\ACG\Generated Cases Archive\20190713T1530Z__ELERING_EQ_001.zip"
    # response = service.publication_request(file_path)
    # print(etree.tostring(response, pretty_print=True).decode())


    # Publication list example

##    response = service.publication_list()
##    print(json.dumps(response), indent = 4))



    # Query model example

    # query_id, response = service.query_object(object_type = "IGM", metadata_dict = {'pmd:scenarioDate': '2019-07-28T00:30:00', 'pmd:timeHorizon': '1D'})
    #
    # list_of_responses = []
    #
    # for single_response in response['sm:QueryResult']['sm:part'][1:]:
    #     list_of_responses.append(single_response['opdm:OPDMObject'])
    #
    # # Create nice table view
    # import pandas
    # pandas.set_option("display.max_rows", 12)
    # pandas.set_option("display.max_columns", 10)
    # pandas.set_option("display.width", 1500)
    # #pandas.set_option('display.max_colwidth', -1)
    #
    # data = pandas.DataFrame(list_of_responses)


    # Get content example

##    model_or_modelpart_UUID = "3c09a995-d250-460d-9b34-09f75fc2cade"
##    response = service.get_content(model_or_modelpart_UUID)
##    print(json.dumps(response, indent = 4))
##    print(response['sm:GetContentResult']['sm:part']['opdm:Profile']['opde:Content'])




 # SOAP API
"""
Prefixes:
     ns0: http://soap.interfaces.application.components.opdm.entsoe.eu/
     xsd: http://www.w3.org/2001/XMLSchema

Global elements:
     ns0:ExecuteOperation(ns0:ExecuteOperation)
     ns0:ExecuteOperationResponse(ns0:ExecuteOperationResponse)
     ns0:PublicationRequest(ns0:PublicationRequest)
     ns0:PublicationRequestResponse(ns0:PublicationRequestResponse)
     ns0:opde-file(ns0:opdeFileDto)

Global types:
     ns0:ExecuteOperation(payload: xsd:base64Binary)
     ns0:ExecuteOperationResponse(return: ns0:resultDto)
     ns0:PublicationRequest(dataset: ns0:opdeFileDto)
     ns0:PublicationRequestResponse(return: ns0:resultDto)
     ns0:opdeFileDto(id: xsd:string, type: xsd:string, content: xsd:base64Binary)
     ns0:resultDto(_value_1: ANY)
     xsd:ENTITIES
     xsd:ENTITY
     xsd:ID
     xsd:IDREF
     xsd:IDREFS
     xsd:NCName
     xsd:NMTOKEN
     xsd:NMTOKENS
     xsd:NOTATION
     xsd:Name
     xsd:QName
     xsd:anySimpleType
     xsd:anyURI
     xsd:base64Binary
     xsd:boolean
     xsd:byte
     xsd:date
     xsd:dateTime
     xsd:decimal
     xsd:double
     xsd:duration
     xsd:float
     xsd:gDay
     xsd:gMonth
     xsd:gMonthDay
     xsd:gYear
     xsd:gYearMonth
     xsd:hexBinary
     xsd:int
     xsd:integer
     xsd:language
     xsd:long
     xsd:negativeInteger
     xsd:nonNegativeInteger
     xsd:nonPositiveInteger
     xsd:normalizedString
     xsd:positiveInteger
     xsd:short
     xsd:string
     xsd:time
     xsd:token
     xsd:unsignedByte
     xsd:unsignedInt
     xsd:unsignedLong
     xsd:unsignedShort

Bindings:
     Soap11Binding: {http://opde.entsoe.eu/opdm/Message#v1}OPDMSoapInterfaceSoapBinding

Service: OPDMSoapInterface
     Port: OPDMSoapInterfacePort (Soap11Binding: {http://opde.entsoe.eu/opdm/Message#v1}OPDMSoapInterfaceSoapBinding)
         Operations:
            ExecuteOperation(payload: xsd:base64Binary) -> return: ns0:resultDto
            PublicationRequest(dataset: ns0:opdeFileDto) -> return: ns0:resultDto
"""
