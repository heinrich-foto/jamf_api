import re
from datetime import datetime
from functools import reduce
from random import random

import keyring as keyring
import requests as requests
from pydantic import ValidationError
from requests.auth import HTTPBasicAuth

from jamf_objects import User, Device, DeviceGroup, Placeholder, Location, UserGroup, Profile

DEBUG = True

def parse_serialnumber(serialnumber: str):
    if serialnumber.startswith("S"):  # remove Serialnumber preix if present.
        serialnumber = serialnumber[1:]
    regex = re.compile("[A-Z0-9]{12}")
    if regex.fullmatch(serialnumber):
        return serialnumber
    else:
        raise ValueError(f"given serialnumber: *{serialnumber}* is not a valid serialnumber.")


class JamfSchool(object):
    def __init__(self, network_id: str, api_pw: str, url: str):
        """
        if network_id or api_pw is None, the value gets extracted from keyring
        :param network_id:
        :param api_pw:
        :param url:
        """
        if any(elem is None for elem in (network_id, api_pw)):
            network_id = keyring.get_password("mz-jamf", "network_id")
            api_pw = keyring.get_password("mz-jamf", "api_pw")

        if url is None:
            url = keyring.get_password("mz-jamf", "url")

        if any(elem is None for elem in (network_id, api_pw, url)):
            print("please provide an HTTPBasicAuth API key for the jamf api.")
            print("network id and api pw is needed.")
            print("provide it in class initiation,")
            print("or as keyring objekt from mz-jamf as network_id, api_pw and url")
            raise ValueError("not enough info to initialize. provide a network_id, api_pw and url")

        self.__authObject = HTTPBasicAuth(network_id, api_pw)
        # https://api.zuludesk.com/, https://apiv6.zuludesk.com/ and https://oursubdomain.jamfcloud.com/api/
        if url.endswith("/"):
            self.url = url[:-1]
        else:
            self.url = url
        self.headers = {"X-Server-Protocol-Version": "3"}
        del api_pw
        del network_id

        self.locations = self.__location_list()
        self.users: [User] = None
        self.devices = None

    def find_location(self, value):
        try:
            index = self.locations.index(value)
        except ValueError:
            print("no location found.")
            return None
        return self.locations[index]

    def device_get_list(self):
        return self.get_device_list()

    def get_device_udid(self, serialnumber: str):
        """
        returns first device found - in the list.
        dosnt returns the howl list - only the UUID


        :return:
        """
        devices = self.get_device_list(serialnumber=serialnumber)
        if devices is not None:
            return devices[0].UDID

    def get_device_list(self, includeApps: bool = None,
                        inTrash: bool = None, hasOwner: bool = None,
                        owner: int = None, managed: bool = None, supervised: bool = None,
                        groups: str = None, ownergroups: str = None, serialnumber: str = None,
                        model: str = None, location: str = None, name: str = None, asserttag: str = None,
                        enrollType: str = None, bootstrapTokenStored: bool = None) -> [Device]:
        """
        returns the filtered list of devices that match the given criteria.

        :param includeApps:	includeApps optional	Boolean	Include (true) or exclude (false) the list of installed apps
        :param inTrash:	inTrash optional	Boolean	Filter by devices in trash
        :param hasOwner:	hasOwner optional	Boolean	Filter by devices that have an owner
        :param owner:	owner optional	Integer	Filter by userId
        :param managed:	managed optional	Boolean	Filter by managed status
        :param supervised:	supervised optional	Boolean	Filter by supervision status
        :param groups:	groups optional	String	Filter by groupId's. Separate multiple entries with a comma (for example: 1,40,31)
        :param ownergroups:	ownergroups optional	String	Filter by user groupId's. Separate multiple entries with a comma (for example: 1,2,3)
        :param serialnumber:	serialnumber optional	String	Filter by serialnumber
        :param model:	model optional	String	Filter by model identifier (for example: iPad3,4)
        :param location:	location optional	String	Filter by location ID
        :param name:	name optional	String	Filter by owner name
        :param asserttag:	asserttag optional	String	Filter by assert tag
        :param enrollType:	enrollType optional	String	Filter by type of enrollment. Options are: manual, depPending, ac2Pending, dep and ac2
        :param bootstrapTokenStored: 	bootstrapTokenStored optional	Boolean	Filter by Bootstrap Token status
        :return:
        """
        api_name = "devices"
        path = "/".join((self.url, api_name))
        print("")
        payload = {arg_key: arg_value for arg_key, arg_value in locals().items() if arg_value is not None
                   and arg_key != "path" and arg_key != "self"}
        r = requests.get(path, params=payload, auth=self.__authObject)
        if r.status_code == 200:
            # return [Device.from_json(entry) for entry in r.json().get(name)]
            # return self.Devices.from_dict(r.json())

            retrun_list = []
            for entry in r.json().get(api_name):
                # print(entry)
                try:
                    device = Device(**entry)
                    retrun_list.append(device)
                except TypeError as e:
                    print(f"{e}: {entry}")
                except ValidationError as e:
                    print(f"{e}: {entry}")
            # return [Device.from_dict(entry) for entry in r.json().get(name)]
            return retrun_list
        else:
            raise ValueError(r.text)

    def get_device_details(self, serialNumber: str = None, udid: str = None, includeApps: bool = False) -> Device:
        """
        Devices - Get Details

        since: 1.0.0

        GET

        :param serialNumber:
        :param udid:
        :param includeApps:
        :return:
        """
        if isinstance(serialNumber, str) and udid is None:
            udid = self.get_device_udid(serialnumber=serialNumber)
        if udid is not None:
            api_endpoint_name = "devices"
            path = "/".join((self.url, api_endpoint_name, udid))
            payload = {"includeApps": includeApps}
            r = requests.get(path, params=payload, auth=self.__authObject)
            if r.status_code == 200:
                try:
                    return Device(**r.json().get("device"))
                except NameError as e:
                    print(f"{e} -> {udid} {serialNumber} {r.json()}")
                except ValidationError as e:
                    print(f"{e} -> {udid} {serialNumber} {r.json()}")

    def device_assign_new_owner(self, udid: str = None, user: str = None) -> bool:
        """
        Devices - Assign new owner

        since: 1.0.0

        Assign a new owner to a device

         (search for device udid via `device_get_list_filtered_by(serialnumber)` )

         user id: The ID of the user that will become the owner of the device.
         Provide a 0 as value to remove the current owner from the device


        :param udid: device udid
        :param user: user id
        :return: bool
        """
        if udid is not None:
            path = "/".join((self.url, "devices", udid, "owner"))
            # assign the given owner to the given device
            payload = {
                "user": f"{user}"
            }
            r = requests.put(path, json=payload, auth=self.__authObject)
            if r.status_code != 200:
                # error occured
                try:
                    print(f"Error {r.json().get('code')}: {r.json().get('message')}")
                    print(f"failed to assign new owner to device: {user} -> {udid}")
                    return False
                except ValueError:
                    print("FatalError in response tor assigning new owner")
                    return False
            else:
                if DEBUG:
                    print(f"new owner for device: {user} -> {udid}")
                return True

    def device_groups_list(self):
        """
        DeviceGroups - List DeviceGroups

        1.0.0

        Get a list of all DeviceGroups

        GET https://api.zuludesk.com/devices/groups

        :return:
        """
        path = "/".join((self.url, "devices", "groups"))
        r = requests.get(path, auth=self.__authObject)
        r_value: [DeviceGroup] = []
        if r.status_code != 200:
            print("error, cant get list of devicegroups.")
        elif r.status_code == 200:
            # TODO in APi Doc is DeviceGrpoups returned, but in reality its deviceGroups
            for res in r.json()["deviceGroups"]:
                r_value.append(DeviceGroup(**res))
        return r_value

    def device_add_to_group(self, groupId: int = None, udids: [str] = None):
        """
        DeviceGroups - Add devices to DeviceGroup (static only)

        since 1.0.0

        Add devices to a DeviceGroup

        POST https://api.zuludesk.com/devices/groups/add

        :param groupId: The DeviceGroup ID
        :param udids: Array of udids of devices to add to the device group.
        :return:
        """
        path = "/".join((self.url, "devices", "groups", "add"))
        payload = {arg_key: arg_value for arg_key, arg_value in locals().items() if arg_value is not None
                   and arg_key != "name" and arg_key != "path" and arg_key != "self"}
        r = requests.post(path, json=payload, auth=self.__authObject)
        if r.status_code != 200:
            print("error, cant add device to group.")

    def device_remove_from_group(self, groupId: int = None, udids: [str] = None):
        """
        DeviceGroups - Remove devices from DeviceGroup (static only)

        since 1.0.0

        Remove devices from a DeviceGroup

        POST https://api.zuludesk.com/devices/groups/remove

        :param groupId: The DeviceGroup ID
        :param udids: Array of udids of devices to add to the device group.
        :return:
        """
        path = "/".join((self.url, "devices", "groups", "remove"))
        payload = {arg_key: arg_value for arg_key, arg_value in locals().items() if arg_value is not None
                   and arg_key != "name" and arg_key != "path" and arg_key != "self"}
        r = requests.post(path, json=payload, auth=self.__authObject)
        if r.status_code != 200:
            print("error, cant add device to group.")

    def device_create_group(self, name: str = None, locationId: int = 0, description: str = "",
                            information: str = "", collectionType: str = "none", shared: bool = False):
        """
        DeviceGroups - Create DeviceGroup (static only)

        since 1.0.0

        Create a new DeviceGroup

        :param name:            Name
        :param locationId:      Location ID (defaults to 0)
        :param description:     Description (defaults to "")
        :param information:     Information (defaults to "")
        :param collectionType:  Collection Type ( "none", "article", "list" or "runningTiles"; defaults to "none")
        :param shared:          This is a shared group

        :return:
        """
        path = "/".join((self.url, "devices", "groups"))
        payload = {arg_key: arg_value for arg_key, arg_value in locals().items() if arg_value is not None
                   and arg_key != "path" and arg_key != "self"}
        allowed_collectionTypes = ["none", "article", "list", "runningTiles"]
        if collectionType not in allowed_collectionTypes:
            print(f"given collection type is not in allowed range of ")
            return None
        r = requests.post(path, json=payload, auth=self.__authObject)
        if r.status_code == 200:
            return r.json().get("id")

    def device_update_details(self, udid: str, assetTag: str = None, notes: str = None):
        if udid is not None:
            path = "/".join((self.url, "devices", udid, "details"))
            payload = {}
            try:
                payload.update({"assetTag": assetTag})
            except ValueError:
                pass
            try:
                payload.update({"notes", notes})
            except ValueError:
                pass
            if payload:
                r = requests.post(path, json=payload, auth=self.__authObject)
                return r
            raise Exception(ValueError, "no payload set")
        else:
            raise Exception(ValueError, "no udid provided")

    def dep_device_list(self):
        """
        Automated_Device_Enrollment - Find a Automated Device Enrollment device

        Get a single Automated Device Enrollment placeholder

        since: 3.0.0

        GET https://api.zuludesk.com/dep

        "placeholders": [
        {
            "id": 5468,
            "userId": 453,
            "locationId": 12345,
            "model": "Apple TV",
            "color": "Black",
            "serialNumber": "DY3QC7BCG9XX",
            "status": "empty",
            "dateAdded": 1505111388,
            "datePushed": 1505457703,
            "profileName": "",
            "placeholderName": "Test TV"
        }
        ]

        :return:
        """

        path = "/".join((self.url, "dep",))  # ":DMPF24PDQ1GC"))
        payload = {}
        r = requests.get(path, headers=self.headers, auth=self.__authObject)
        r_value: [Placeholder] = []
        if r.status_code == 200:
            for entry in r.json().get("placeholders"):
                r_value.append(Placeholder(**entry))
        # every time i get a 404 Error. "Not Found" -> solution is easy - add the v.3 X-Server-Proto Header
        # https://community.jamf.com/t5/jamf-school/jamf-school-zuludesk-api-endpoint-for-dep-returns-404/td-p/259810
        elif r.status_code == 404:
            print("error, cant communicate with the endpoint")
            print(f"{r.reason}")
        return r_value

    def update_dep(self, serialNumber: str, deviceName: str = None, userID: str = None, groupIds: [int] = None,
                   profilId: int = None):
        """
        Automated_Device_Enrollment - Update Automated Device Enrollment device

        since 3.0.0

        Update a Automated Device Enrollment device

        POST https://api.zuludesk.com/dep/:serial

        :param serialNumber:
        :param deviceName: Optional Device name to set upon enrollment
        :param userID: Optional ID of the user to make the owner upon enrollment
        :param groupIds: Optional Array of group IDs to apply upon enrollment
        :param profilId: Optional ID of the Automated Device Enrollment profile to assign to the device.
                         If profileId is 0, then the placeholder will be unassigned from a profile.
        :return:
        """
        path = "/".join((self.url, "dep", serialNumber))  # ":DMPF24PDQ1GC"))
        payload = {arg_key: arg_value for arg_key, arg_value in locals().items() if arg_value is not None
                   and arg_key != "name" and arg_key != "path" and arg_key != "self" and arg_key != "serialNumber"}
        r = requests.post(path, json=payload, headers=self.headers, auth=self.__authObject)
        if r.status_code == 200:
            print(f"{r.json().get('message')} for {serialNumber}")
        elif r.status_code == 404:
            print(f"error, cant communicate with the endpoint")

        # TODO Asset Tag is missing in update - and in get methodes for placeholders, but present in the UI
        # TODO location for DEP cannot be changed via API
        # TODO PlaceholderName - for What is it there, can not change it.
        # TODO Placeholder for new unknown devices?
        # TODO profileName - inconsistent, everything else is done via ids and this is done via name...
        # https://ideas.jamf.com/ideas/JN-I-25819

    def get_dep(self, serialNumber: str) -> Placeholder:
        """
        Automated_Device_Enrollment - Find a Automated Device Enrollment device

        since 3.0.0

        Get a single Automated Device Enrollment placeholder

        GET https://api.zuludesk.com/dep/:serial

        "placeholder": {
            "id": 5468,
            "userId": 453,
            "locationId": 12345,
            "model": "Apple TV",
            "color": "Black",
            "serialNumber": "DY3QC7BCG9XX",
            "status": "empty",
            "dateAdded": 1505111388,
            "datePushed": 1505457703,
            "profileName": "",
            "placeholderName": "Test TV"
        }
        :return:
        """
        path = "/".join((self.url, "dep", serialNumber))
        r = requests.get(path, headers=self.headers, auth=self.__authObject)
        if r.status_code == 200:
            return Placeholder(**r.json()["placeholder"])
        elif r.status_code == 404:
            print(f"{r.json().get('message')} for {serialNumber}")
        else:
            print("cnat get dep placeholder, endpoint communication error.")

    def location_list(self):
        """
            Locations - Get a list of locations
            https://api.zuludesk.com/locations/
            since 2.0.0

            {
                "locations": [
                    {
                        "id": 0,
                        "name": "District Location",
                        "isDistrict": true,
                        "street": null,
                        "streetNumber": null,
                        "postalCode": null,
                        "city": null,
                        "source": "default",
                        "asmIdentifier": null,
                        "schoolNumber": "12AB"
                    }
                ]
            }
        """
        return self.locations

    def __location_list(self):
        path = "/".join((self.url, "locations"))

        r = requests.get(path, auth=self.__authObject)
        if r.status_code == 200:
            try:
                return [Location(**loc) for loc in r.json().get("locations")]
            except:
                print("Cant parse json to a locations list")
                return [None]
        else:
            print("cannot connect to api")

    def user_list(self, inTrash: bool = None, hasDevice: bool = None, memberOf: str = None, locationId: str = None) -> [
        User]:
        """:arg
        Users - List users
        Get a list of all users in your organisation, optionally with filters

        since: 1.0.0

        https://api.zuludesk.com/users

        Feld	Typ	Beschreibung
        inTrash optional	Boolean
        Filter by users in trash

        hasDevice optional	Boolean
        Filter by users that are owner of one or more devices

        memberOf optional	String
        Filter by groupId's. Separate multiple entries with a comma (for example: 1,40,31)

        locationId optional	String
        Filter by locationId

        Returns

        {
            "code": 200,
            "count": 1,
            "users": [
                {
                    "id": 1234,
                    "locationId": 0,
                    "status": "Active",
                    "deviceCount": 1,
                    "email": "api@zuludesk.com",
                    "username": "John",
                    "domain": "",
                    "firstName": "API",
                    "lastName": "Demo",
                    "groupIds": [
                        1234
                    ],
                    "groups": [
                        "API Group"
                    ],
                    "vpp": [
                        {
                            "status": "Associated"
                        }
                    ],
                    "teacherGroups": [],
                    "children": [],
                    "notes": "",
                    "modified": "2015-05-04 13:37:00"
                }
            ]
        }
        """

        path = "/".join((self.url, "users"))
        r_value: [User] = []  # holds the parsed users
        # payload = {arg_key: arg_value for arg_key, arg_value in locals().items() if arg_value is not None
        #           and arg_key != "self" and arg_key != "path" and arg_key != "r_value"}
        payload = {
            "locationId": f"{locationId}",
            "hasDevice": True
        }
        r = requests.get(path, json=payload, auth=self.__authObject)
        if r.status_code == 200:

            for u in r.json().get("users"):
                try:
                    r_value.append(User(**u))
                except ValidationError as e:
                    print(f"cant convert json to user object in {u} with error {e}")
        else:
            print(f"ERROR: user list {r.status_code}")
            return [None]
        befor_cleanup = len(r_value)
        if locationId is None:
            return r_value
        r_value = [i for i in r_value if i.locationId == locationId]
        after_cleanup = len(r_value)
        if DEBUG:
            print("api request, dosnt use payload, list needed to be filtered afterwords")
            print(f"{befor_cleanup:6} != {after_cleanup:6}")
        return r_value

    def get_user_group_list(self) -> [UserGroup]:
        """
        Groups - List groups

        since 1.0.0

        Get a list of all groups

        GET https://api.zuludesk.com/users/groups
        """
        path = "/".join((self.url, "users", "groups"))
        r_value: [UserGroup] = []
        r = requests.get(path, auth=self.__authObject)
        if r.status_code == 200:
            for g in r.json()["groups"]:
                try:
                    r_value.append(UserGroup(**g))
                except ValidationError as e:
                    print(f"cant convert json to User Group object in {g} with error {e}")
        else:
            print(f"ERROR: user list {r.status_code}")
            return [None]
        return r_value

    def create_user_group(self, name: str = None, description: str = None, locationId: int = None,
                          acl: UserGroup = None):
        """
        Groups - Create group

        since 1.0.0

        Create a new group

        POST https://api.zuludesk.com/users/groups

        name	String	Name

        description optional	String	Description

        locationId int (String)	Location ID

        acl  Object
        :return:
        """
        path = "/".join((self.url, "users", "groups"))
        payload = {arg_key: arg_value for arg_key, arg_value in locals().items() if arg_value is not None
                   and arg_key != "self" and arg_key != "path"}
        r = requests.get(path, json=payload, auth=self.__authObject)
        if r.status_code != 200:
            e = ""
            if r.status_code in (400, 404):
                e = r.json()["message"]
            print(f"error in creating the group {e}")
        else:
            print()
            print(f"group: {name} {r.json()['message']}")

    @staticmethod
    def generate_username(location_prefix: str = None, firstName: str = None, lastName: str = None) -> str:
        """
        generate a username string as jamf username,
        it requires a Location Prefix
                    a firstName
                    a lastName
        it is basically a concatenation and string replacement action.

        :str jamf_username
        """

        for required_variable in ["location_prefix", "firstName", "lastName"]:
            if locals().get(required_variable) is None:
                print(f"ERROR: {required_variable} is required to create a jamf username string.")
                return ""

        spcial_char_map = {ord(u'ä'): 'ae', ord(u'ü'): 'ue', ord(u'ö'): 'oe',
                           ord(u'Ä'): 'Ae', ord(u'Ü'): 'Ue', ord(u'Ö'): 'Oe',
                           ord(u'ß'): 'ss',
                           ord('é'): 'e', ord('è'): 'e', ord('ê'): 'e',
                           }
        rep = ('Dr. ', ''), ('von ', '')

        firstName = reduce(lambda a, kv: a.replace(*kv), rep, firstName)
        lastName = reduce(lambda a, kv: a.replace(*kv), rep, lastName)
        location_prefix = location_prefix.translate(spcial_char_map)

        firstName = re.split(' |-', firstName)[0]
        lastName = re.split(' |-', lastName)[0]

        return f"{location_prefix}-{firstName}{lastName}".translate(spcial_char_map)

    def create_user(self, username: str = None,
                    password: str = None,
                    storePassword: bool = None,
                    domain: str = None,
                    email: str = None,
                    firstName: str = None,
                    lastName: str = None,
                    memberOf: [] = None,
                    teacher: [int] = None,
                    children: [int] = None,
                    notes: str = None,
                    exclude: bool = None,
                    locationId: str = None,
                    ) -> (str, str):
        """
        Users - Create user

        since: 1.0.0


        POST https://api.zuludesk.com/users

        username	String
        Username (must be unique within your organisation)

        password	String
        Password

        storePassword optional	Boolean
        Store the password locally

        domain optional	String
        Logon domain (for example the Active Directory domain this user resides in)

        email	String
        E-mail address

        firstName	String
        First Name

        lastName	String
        Last Name

        memberOf	Array[Mixed]
        Array with ID's [Integer] or names [String] of the groups to make the new user a member of. If the group does not exists yet, it will be created

        teacher optional	Array[Integer]
        Array with ID's of groups this user can manage using the Jamf Teacher apps

        children optional	Array[Integer]
        Array with ID's of users that this user can manage using the Jamf Parent app

        notes optional	String
        Notes

        exclude optional	Boolean
        Don't apply Teacher restrictions

        locationId optional	String
        Location ID

        :return: on success (username, password)
                 on failure EmailAddressInUse|UsernameInUse | LocationNotFound
        """

        path = "/".join((self.url, "users"))

        # check for required variables
        for required_variable in ["username", "firstName", "lastName", "locationId"]:
            if locals().get(required_variable) is None:
                print(f"ERROR: {required_variable} is required to create a user.")
                return None

        if notes is None:
            notes = ""

        if email is None:
            # is required, but can be empty... omg... zulu-jamf profis
            # and in this what for is storePassword ... jamf - i dont know what "Store the password locally" means.
            email = ""

        if memberOf is not None:
            # check if it is a list otherwise place the str inside a list
            if isinstance(memberOf, str):
                memberOf = [memberOf]

        notes = " ".join([notes, "user_created:", datetime.now().strftime("%Y-%m-%d_%H-%M")])

        if password is None:
            password = f"{random.randint(111111, 999999)}"
            if DEBUG:
                print(f"INFO: random password is generated {password}")

            # add password to notes fild, if random generated
            notes = " ".join([notes, "PW:", password]).lstrip()

        payload = {arg_key: arg_value for arg_key, arg_value in locals().items() if arg_value is not None
                   and arg_key != "name" and arg_key != "self" and arg_key != "path"
                   and arg_key != "required_variable"}

        r = requests.post(path, json=payload, auth=self.__authObject)
        if r.status_code == 200:
            try:
                return username, password
            except:
                print("ERROR in json get message for user create methode.")
        elif r.status_code == 400:
            print(f'Error: {r.json().get("message")} for {username}')
            return None, None
        elif r.status_code == 404:
            print(f'Error: {r.json().get("message")} for {username}')
            return None, None

    def find_similar_users(self, firstName: str = None, lastName: str = None,
                           match_any: bool = False, locationId: str = None,
                           inTrash: bool = None, hasDevice: bool = None, memberOf: str = None) -> [User]:
        if self.users is None:
            self.users = self.user_list()
        if locationId is None:
            users = self.users
        else:
            users = self.user_list(inTrash=inTrash, hasDevice=hasDevice, memberOf=memberOf, locationId=locationId)

        # TODO Fuzzy Match - and some Umlaut matches...
        if match_any:
            return [u for u in users if any(x in u.name for x in [firstName, lastName])]
        else:
            # print("hallo")
            return [u for u in users if all(x in u.name for x in [firstName, lastName])]

    def get_profiles(self) -> [Profile]:
        """
        Profiles - Get a list of profiles

        since: 2.0.0

        GET https://api.zuludesk.com/profiles/
        "profiles": [
                {
                    "id": 2555,
                    "locationId": 0,
                    "identifier": "com.zuludesk.MDM.iOS.86e383f458875997be55a0a7b494b17d",
                    "name": "Demo Profile A",
                    "description": "Test profile",
                    "platform": "iOS"
                },
                {
                    "id": 2728,
                    "identifier": "com.zuludesk.MDM.iOS.8da185b41642945bd4be19c2feaf34ae",
                    "name": "VPP Invite Web Clip",
                    "description": "Automatically created profile",
                    "platform": "universal"
                }
            ]

        :return:
        """
        path = "/".join((self.url, "profiles"))

        r = requests.get(url=path, auth=self.__authObject)
        if r.status_code == 200:
            try:
                return [Profile(**entry) for entry in r.json().get("profiles")]
            except KeyError:
                print("profiles not found in response")

    def move_device_location(self, uuid: str = None):
        """
        first - move device to different mdm server via asm.
         -> because it is not possible to move them by dep profil stuff.

        is the device already enrolled?

        unassign Profil

        save Groups -> try to assign afterwords
        save Asset Tag -> set asset Tag afterword

        move device to new location

        move device to different mdm server



        :return:
        """
        pass
