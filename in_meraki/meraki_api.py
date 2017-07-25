#!/usr/bin/python3
# cython: language_level=3

"""
Author - Adam Asay
Company - INVITE Networks

Description:
This is an implementation of the Meraki API for Python3.  The MerakiSession Class is used to create the initial session.
An org needs to be selected once
"""

import requests
import json


class ResponseError(Exception):
    """
    Thrown when the is an error in the response
    """


class OrgPermissionError(Exception):
    """
    Thrown when the is an error in the response
    """


class OrgNotValid(Exception):
    """
    Thrown when a method is called that requires and Org, but one has not been set
    """
    def __init__(self):
        self.default = 'An Organization must be specified to complete this request.'

    def __str__(self):
        return repr(self.default)


class MerakiAPI:
    """
    This class handles the connection to the API
    """

    __base_url = 'https://dashboard.meraki.com/api/v0'

    def __init__(self, api_key, logging=None):
        """
        Initilize the connection to the API and validate the api key
        :param api_key: Meraki API Key
        :return: None
        """

        self.__api_key = api_key
        self.__logging = logging
        self.__org_id = None
        self.__org_name = None

        self.headers = {
            'x-cisco-meraki-api-key': format(str(self.__api_key)),
            'Content-Type': 'application/json'
        }

        # Get the list of organizations that we have access to
        self._organizations = self.get_organizations()

    def __get_request(self, url, require_org=True):
        """
        Perform a get request to Meraki
        :param url: URL to be accessed
        :param require_org: Flag to ignore if the org is set or not
        :return: Response
        """

        if require_org and self.__org_id is None:
            raise OrgNotValid

        response = requests.get("{}{}".format(self.__base_url, url), headers=self.headers)

        return self.__return_handler(response.status_code, response.text)

    def __post_request(self, url, post_data, require_org=True):
        """
        Perform a post request to Meraki
        :param url: URL to be posted to
        :param post_data: Dictionary of data to be converted to JSON
        :param require_org: Flag to ignore if the org is set or not
        :return: Response
        """

        if require_org and self.__org_id is None:
            raise OrgNotValid

        response = requests.post("{}{}".format(self.__base_url, url), data=json.dumps(post_data), headers=self.headers)

        return self.__return_handler(response.status_code, response.text)

    def __del_request(self, url, require_org=True):
        """
        Perform a get request to Meraki
        :param url: URL to be accessed
        :param require_org: Flag to ignore if the org is set or not
        :return: Response
        """

        if require_org and self.__org_id is None:
            raise OrgNotValid

        response = requests.delete("{}{}".format(self.__base_url, url), headers=self.headers)

        return self.__return_handler(response.status_code, response.text)

    @staticmethod
    def __is_json(text):
        """
        Validate if the text is json
        :param text: Text to validate
        :return:
        """
        try:
            json.loads(text)
        except ValueError:
            return False
        return True

    def __return_handler(self, status_code, return_text):
        """
        Handles the response from the get request
        :param status_code: HTTP Status Code
        :param return_text: Return text that we want to convert to json
        :return:
        """

        if self.__is_json(return_text):
            return_text = json.loads(return_text)

        else:
            raise ResponseError("Invalid JSON Response StatusCode={}".format(status_code))

        if status_code == 200:
            return return_text
        elif status_code == 201:
            # Successfully Added
            return return_text
        elif status_code == 204:
            # Successfully Deleted
            return return_text
        elif status_code == 400 and return_text['errors'][0].startswith('Email'):
            return return_text
        else:
            print (return_text)
            raise ResponseError("Invalid Response StatusCode={} Message={}".format(status_code, return_text))

    def get_org_id(self):
        """
        Returns the current org_id
        :return: org_id
        """

        return self.__org_id

    def get_org_name(self):
        """
        Returns the current org_name
        :return: org_name
        """

        return self.__org_name

    def get_organizations(self):
        """
        Get the Org IDs associated with the API key
        :return: JSON Orgs
        """

        url = '/organizations'

        return self.__get_request(url, False)

    def get_config_templates(self):
        """
        Returns the configuration templates
        :return: Dict of Admins
        """

        url = "/organizations/{}/configTemplates".format(self.__org_id)

        return self.__get_request(url)

    def get_devices(self, network):
        """
        Returns the devices in a network
        :param network" Network ID we will search through
        :return: Dict of Admins
        """

        url = "/networks/{}/devices".format(network)

        return self.__get_request(url)

    def get_device(self, network, serial):
        """
        Returns the devices in a network
        :param network" Network ID we will search through
        :param serial: The serial number of the device
        :return: Dict of Admins
        """

        url = "/networks/{}/devices/{}".format(network, serial)

        return self.__get_request(url)

    def get_networks(self):
        """
        Returns the networks of an org
        :return: Dict of Admins
        """

        url = "/organizations/{}/networks".format(self.__org_id)

        return self.__get_request(url)

    def get_admins(self):
        """
        Returns the administrators of an org
        :return: Dict of Admins
        """

        url = "/organizations/{}/admins".format(self.__org_id)

        return self.__get_request(url)

    def set_organization(self, org_id):
        """
        Sets the org ID using the id or the name
        :param org_id: Unique identifier of the org id or org name
        :return: None
        """

        self.__org_id = None
        self.__org_name = None

        for org in self._organizations:
            if org['name'] == org_id or str(org['id']) == org_id or org['id'] == org_id:
                self.__org_id = org['id']
                self.__org_name = org['name']
                break

        if self.__org_id is None:
            raise OrgPermissionError("Invalid Organization '{}' for User".format(org_id))

    def update_admin(self, email, name, admin_id, org_access=None, tags=None, tag_access=None, networks=None, net_access=None):
        """
        This will update an admin for an account.  add_admin is accled using the same variables but the admin_id is
        required here
        :param email: Email Address
        :param name: Full name
        :param admin_id: ID of the admin
        :param org_access: full or none
        :param tags:
        :param tag_access:
        :param networks:
        :param net_access:
        :return:
        """

        return self.add_admin(email, name, org_access, tags, tag_access, networks, net_access, admin_id)

    def add_admin(self, email, name, org_access=None, tags=None, tag_access=None, networks=None, net_access=None, admin_id=None):
        """
        Adds an administrator to the Org
        :param email: Email Address
        :param name: Full name
        :param org_access: full or none
        :param tags:
        :param tag_access:
        :param networks:
        :param net_access:
        :param admin_id: ID of the admin for updates only
        :return:
        """

        # Change the URL if this is an update
        if admin_id is None:
            url = "/organizations/{}/admins".format(self.__org_id)
        else:
            url = "/organizations/{}/admins/{}".format(self.__org_id, admin_id)

        post_tags = []

        if org_access is None and tags is None and networks is None:
            print("Administrator accounts must be granted access to either an Organization, Networks, or Tags")
            return None

        if tags is not None and tag_access is None:
            print("If tags are defined you must define matching access arguments.\nFor example, tags = ['tag1', 'tag2'], "
                  "must have matching access arguments: tagaccess = 'full', 'read-only'")
            return None
        elif tag_access is not None and tags is None:
            print("If tag access levels are defined you must define matching tag arguments\nFor example, tags = "
                  "['tag1', 'tag2'] must have matching access arguments: tagaccess = 'full', 'read-only'")
            return None
        elif tag_access is None and tags is None:
            pass
        elif len(tags) != len(tag_access):
            print("The number of tags and access arguments must match.\n")
            print("For example, tags = ['tag1', 'tag2'] must have matching access arguments: tagaccess = "
                  "['full', 'read-only']")
            return None
        elif tags is not None and tag_access is not None:
            x = 0
            while x < len(tags):
                post_tags.append({'tag': tags[x], 'access': tag_access[x]})
                x += 1
        else:
            pass

        post_nets = []

        if networks is not None and net_access is None:
            print("If networks are defined you must define matching access arguments\nFor example networks = "
                  "['net1', 'net2'] must have matching access arguments: netaccess = 'full', 'read-only'")
            return None
        elif net_access is not None and networks is None:
            print("If network access levels are defined you must define matching network arguments\nFor example, networks"
                  " = ['net1', 'net2'] must have matching access arguments: netaccess = 'full', 'read-only'")
            return None
        elif net_access is None and networks is None:
            pass
        elif len(networks) != len(net_access):
            print("The number of networks and access arguments must match.\n")
            print("For example, networks = ['net1', 'net2'] must have matching access arguments: netaccess = "
                  "['full', 'read-only']")
            return None
        elif networks is not None and net_access is not None:
            x = 0
            while x < len(networks):
                post_nets.append({'id': networks[x], 'access': net_access[x]})
                x += 1
        else:
            pass

        post_data = []

        if len(post_tags) == 0 and len(post_nets) == 0:
            post_data = {
                'orgAccess': org_access,
                'email': format(str(email)),
                'name': format(str(name))
            }

        elif len(post_tags) > 0 and len(post_nets) == 0:
            post_data = {
                'name': format(str(name)),
                'email': format(str(email)),
                'orgAccess': org_access,
                'tags': post_tags
            }

        elif len(post_nets) > 0 and len(post_tags) == 0:
            post_data = {
                'name': format(str(name)),
                'email': format(str(email)),
                'orgAccess': org_access,
                'networks': post_nets
            }

        elif len(post_nets) > 0 and len(post_tags) > 0:
            post_data = {
                'name': format(str(name)),
                'email': format(str(email)),
                'orgAccess': org_access,
                'tags': post_tags,
                'networks': post_nets
            }

        return self.__post_request(url, post_data)

    def del_admin(self, admin_id):
        """
        Delete the users access from the org
        :param admin_id: ID off the user account
        :return: Response
        """

        url = "/organizations/{}/admins/{}".format(self.__org_id, admin_id)

        return self.__del_request(url)

    @staticmethod
    def get_single_entry(search, search_key, get_function,  return_key=None):
        """
        This returns a single entry from any of the get functions based on the search criteria
        :param search: What we are searching for
        :param search_key: The key to look in to find the search parameter
        :param get_function: The function to call to get the list to search through
        :param return_key: Returns the specific key, if none returns all attributes
        :return: Result
        """

        search_result = next(entry for entry in get_function() if entry[search_key] == search)

        if return_key is not None and return_key in search_result:
            return search_result[return_key]

        return search_result


