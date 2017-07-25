#!/usr/bin/python3
# cython: language_level=3

"""
Author - Adam Asay
Company - INVITE Networks

Description:
"""

from pysnmp.hlapi import *


class MerakiSNMP:
    """
    Used to pull Meraki Details using SNMP
    """

    def __init__(self, user, auth, priv, logging=None):
        """
        :param user: Username
        :param auth: Auth
        :param priv: Priv
        """

        self.__user = user
        self.__auth = auth
        self.__priv = priv
        self.__logging = logging

    def snmp_get(self, oid):
        """
        Returns the result of a snmp query
        :param oid: mib
        :return:
        """

        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   UsmUserData(self.__user, self.__auth, self.__priv),
                   UdpTransportTarget(('snmp.meraki.com', 16100)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if errorIndication:
            print(errorIndication)

        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                return varBind[1]

    def get_modem_status(self, mac):
        """
        Returns the status of the LTE modem
        :param mac: MAC address of the device
        :return: String
        """

        oid_prefix = "1.3.6.1.4.1.29671.1.1.4.1.14"
        oid = "{}.{}".format(oid_prefix, self.mac_to_decimal(mac))

        return self.snmp_get(oid) or "No Modem"

    @staticmethod
    def mac_to_decimal(mac):
        """
        Converts a mac address into decimal notation
        :param mac: mac address to convert
        :return: Converted String
        """

        split = mac.split(":")
        converted = []

        for hex_value in split:
            converted.append(str(int(hex_value, 16)))

        return ".".join(converted)