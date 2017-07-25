#!/usr/bin/python3
# cython: language_level=3

"""
Author - Adam Asay
Company - INVITE Networks

Description:
"""

#!/usr/bin/python3
# cython: language_level=3

"""
Author - Adam Asay
Company - INVITE Networks

Description: Meraki API
"""


from meraki_api import *
from meraki_snmp import *


class MerakiSession(MerakiAPI, MerakiSNMP):
    """
    This is a generic meraki session.  It is used to access info a crossed the Meraki API, and SNMP
    """

    def __init__(self, api_key, snmp_user, snmp_auth, snmp_priv, logging=None):
        """
        Initilize the connection to the API and validate the api key
        :param api_key: Meraki API Key
        :return: None
        """

        # Initialize the API
        MerakiAPI.__init__(self, api_key, logging)

        # Initialize SNMP
        MerakiSNMP.__init__(self, snmp_user, snmp_auth, snmp_priv)

