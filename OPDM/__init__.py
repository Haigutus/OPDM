from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
from OPDM.OPDM_SOAP_API import Client

# Deprecated class name
create_client = Client

