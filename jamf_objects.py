from json import JSONEncoder
from typing import List, Optional, Union

from pydantic import BaseModel

"""

Helper Obejects for Jamf JSON Returns

using pydantics BaseModel to create classes.
dataclass has the problem with reserved Names, 
in pydantics it is possible to use a internal 
variable name (not a reserved one) and a mapping
function to translate the JSON name to the variables.

e.g. the reserved name class or from ... can be stored in
a variable class_ or from_ and get translated by:
       class Config:
        fields = {
            'class_': 'class',
            'from_': 'from'
        }
and this is a great way to solve the problem. 
moreover the parser is more precise, and give
more feedback about what is going on inside the model.


"""


class Location(object):
    """
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
    """

    def __init__(self, id=None, name=None, isDistrict=None, street=None, streetNumber=None,
                 postalCode=None, city=None, source=None, asmIdentifier=None, schoolNumber=None):
        self.id = id
        self.name = name
        self.isDistrict = isDistrict
        self.street = street
        self.streetNumber = streetNumber
        self.postalCode = postalCode
        self.city = city
        self.source = source
        self.asmIdentifier = asmIdentifier
        self.schoolNumber = schoolNumber
        if self.schoolNumber is None:
            self.schoolNumber = ""

    def __str__(self):
        return f"{self.id: >4}: {self.name: <30} {self.schoolNumber: <5}"

    def __repr__(self):
        return f"{self.id}: {self.name}"

    @property
    def locationId(self):
        return self.id

    def __eq__(self, other):
        """
        compare other with the locationId

        you can pass in a locationId and get the info if its equal

        :param other:
        :return:
        """
        if isinstance(other, int):
            return self.id == other
        elif isinstance(other, str):
            return str.lower(other) in str.lower(self.name)


class LocationEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class DeviceType(BaseModel):
    value: str = None


class DeviceModel(BaseModel):
    name: str = None
    identifier: str = None
    type: Union[str, DeviceType] = None


class DeviceOS(BaseModel):
    prefix: str = None
    version: str = None


class VppStatus(BaseModel):
    status: str = None


class DeviceOwner(BaseModel):
    id: int = None
    locationId: int = None
    inTrash: bool = None
    deviceCount: int = None
    username: str = None
    email: str = None
    firstName: str = None
    lastName: str = None
    groupIds: List[int] = None
    groups: List[str] = None
    teacherGroups: List[str] = None
    children: List[str] = None
    vpp: List[VppStatus] = None
    notes: str = None
    modified: str = None


class DeviceReagon(BaseModel):
    string: str = None
    coordinates: str = None


class App(BaseModel):
    name: str = None
    vendor: str = None
    identifier: str = None
    version: str = None
    icon: str = None


class ServiceSubscription(BaseModel):
    """
        'CarrierSettingsVersion': '49.0',
        'CurrentCarrierNetwork': '',
        'CurrentMCC': '65535',
        'CurrentMNC': '65535',
        'EID': '89049032004008882600018863497732',
        'ICCID': '8949 2271 9610 5378 353',
        'IMEI': '35 319310 940039 6',
        'IsDataPreferred': True,
        'IsRoaming': False,
        'IsVoicePreferred': False,
        'Label': 'USER_LABEL_PRIMARY',
        'LabelID': '69EA85D2-06BD-41E7-A10E-B28033C09725',
        'PhoneNumber': '',
        'Slot': 'CTSubscriptionSlotOne'
    """
    CarrierSettingsVersion: str = None
    CurrentCarrierNetwork: str = None
    CurrentMCC: str = None
    CurrentMNC: str = None
    EID: str = None
    ICCID: str = None
    IMEI: str = None
    # MEID: Optional[str] = ""  # not present in Doku
    IsDataPreferred: bool = None
    IsRoaming: bool = None
    IsVoicePreferred: bool = None
    Label: str = None
    LabelID: str = None
    PhoneNumber: str = None
    Slot: str = None


class NetworkInformation(BaseModel):
    IPAddress: str = None
    isNetworkTethered: int = None
    BluetoothMAC: str = None
    WiFiMAC: str = None
    VoiceRoamingEnabled: int = None
    DataRoamingEnabled: int = None
    PersonalHotspotEnabled: int = None
    ServiceSubscription: Optional[List[ServiceSubscription]]


class DeviceLastCheckin(BaseModel):
    date: str = None
    timezone_type: int = None
    timezone: str = None


class Device(BaseModel):
    """
        "UDID": "XXXXXXXXXXXX",
         "locationId": 0,
         "serialNumber": "DMPLXXXXXXX",
         "assetTag": "ASSET-TAG-00001",
         "inTrash": false,
         "class": "ipad",
         "model": [
            {
               "name": "iPad 4 (WiFi)",
               "identifier": "iPad3,4",
               "type": "iPad"
            }
         ],
         "os": [
            {
               "prefix": "iOS",
               "version": "8.3.0"
            }
         ],
         "name": "Device name",
         "owner": [
            {
               "id": 1,
               "locationId": 0,
               "inTrash": false,
               "deviceCount": 1,
               "username": "John",
               "email": "api@jamfschool.com",
               "firstName": "Demo",
               "lastName": "API",
               "groupIds": [
                  1234
               ],
               "groups": [
                  "API Group"
               ],
               "teacherGroups": [],
               "children": [],
               "vpp": [
                  {
                     "status": "Associated"
                  }
               ],
               "notes": "",
               "modified": "2015-05-04 13:37:00"
            }
         ],
         "isManaged": true,
         "isSupervised": true,
         "isBootstrapStored": true,
         "deviceEnrollType": "dep",
         "deviceDepProfile": "Dep Profile",
         "batteryLevel": 0.988,
         "totalCapacity" : 26.4135,
         "availableCapacity": "25.6946",
         "hasPasscode": true,
         "passcodeCompliant": true,
         "hardwareEncryptionEnabled": false,
         "iTunesStoreLoggedIn": true,
         "iCloudBackupEnabled": true,
         "iCloudBackupLatest": "2015-25-08 12:34:56",
         "groupIds": [
            4567
         ],
         "groups": [
            "iPad Groups"
         ],
         "WiFiMAC": "ab:cd:ef:12:34:56",
         "bluetoothMAC": "ab:cd:ef:12:34:56",
         "IPAddress": "127.0.0.1",
         "region": [
            {
               "string": "Netherlands",
               "coordinates": "52.237989,5.534607"
            }
         ],
         "apps": [
           {
             "name": "1Password",
             "vendor": "AgileBits Inc.",
             "identifier": "com.agilebits.onepassword-ios",
             "version": "5.5",
             "icon": "http://is1.mzstatic.com/image/pf/us/r30/Purple7/v4/22/94/98/22949833-5ec2-8a77-4e21-e67d9bad92b3/AppIcon60x60_U00402x.png"
           }
        ],
         "notes": "",
         "lastCheckin": "2015-05-04 13:42:00",
         "modified": "2015-05-04 13:37:00",
         "networkInformation": {
         "IPAddress": "10.0.2.2",
         "isNetworkTethered": "0",
         "BluetoothMAC": "34:a8:eb:03:c3:8f",
         "WiFiMAC": "34:a8:eb:03:d3:1a",
         "VoiceRoamingEnabled": "0",
         "DataRoamingEnabled": "0",
         "PersonalHotspotEnabled": "0",
         "ServiceSubscription": [
            {
                "CarrierSettingsVersion": "41.0",
                "CurrentCarrierNetwork": "iPad",
                "CurrentMCC": "310",
                "CurrentMNC": "410",
                "EID": "89049032004008882600019726686182",
                "ICCID": "8901 3802 2972 1342 9615",
                "IMEI": "35 317310 903145 8",
                "IsDataPreferred": true,
                "IsRoaming": false,
                "IsVoicePreferred": false,
                "Label": "USER_LABEL_PRIMARY",
                "LabelID": "E1E8924B-5C47-49B1-9DB8-E06D36DD835E",
                "PhoneNumber": "",
                "Slot": "CTSubscriptionSlotOne"
            }
        ]
      }
   ]
    """
    UDID: str = None
    locationId: int = None
    serialNumber: str = None
    assetTag: str = None
    class_: str = None
    inTrash: bool = None

    class Config:
        fields = {
            'class_': 'class'
        }

    model: DeviceModel = None

    os: DeviceOS = None

    name: str = None
    owner: DeviceOwner = None

    isManaged: bool = None
    isSupervised: bool = None
    isBootstrapStored: bool = None
    enrollType: str = None  # deviceEnrollType
    depProfile: str = None  # deviceDepProfile
    batteryLevel: str = None
    totalCapacity: str = None
    availableCapacity: str = None
    hasPasscode: bool = None
    passcodeCompliant: bool = None
    hardwareEncryptionEnabled: bool = None
    iTunesStoreLoggedIn: bool = None
    iCloudBackupEnabled: bool = None
    iCloudBackupLatest: str = None
    # groupIds: [int] = None
    groups: List[str] = None

    WiFiMAC: str = None
    bluetoothMAC: str = None
    IPAddress: str = None
    region: DeviceReagon = None

    apps: List[App] = None

    notes: str = None
    lastCheckin: Union[str, DeviceLastCheckin] = None
    modified: str = None
    networkInformation: NetworkInformation = None

    def __eq__(self, other):
        """
        compares other with the serialNumber of the device

        :param other:
        :return:
        """
        return self.serialNumber == other


class User(BaseModel):
    """
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

    """
    id: int = -1
    locationId: int = -1
    status: str = ""
    deviceCount: int = 0
    email: str = ""
    username: str = ""
    domain: str = ""
    firstName: str = ""
    lastName: str = ""
    groupIds: List[int] = None
    groups: List[str] = None
    vpp: List[VppStatus] = None
    teacherGroups: List[str] = None
    children: List[str] = None
    notes: str = ""
    modified: str = None
    name: str = ""
    exclude: str = ""

    def __str__(self):
        return f"{self.username}"

    def __repr__(self):
        return self.username

    def __eq__(self, other):
        if isinstance(other, str):
            return self.username == other
        elif isinstance(other, int):
            return self.id == other
        else:
            raise ValueError("wrong type passed.")


class UserEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class GroupAcl(BaseModel):
    """     "allow", "deny", "inherit"
                    "selfService": "inherit",
                    "selfServiceInfo": "allow",
                    "selfServiceLocation": "allow",
                    "selfServiceClearPasscode": "allow",
                    "selfServiceLock": "inherit",
                    "selfServiceWipe": "inherit",
                    "selfServiceUnenroll": "inherit",
                    "teacher": "allow",
                    "parent": "inherit"
        selfService are not used in jamf-school
        only teacher and parent
    """
    selfService: Optional[str] = "inherit"
    selfServiceInfo: Optional[str] = "inherit"
    selfServiceLocation: Optional[str] = "inherit"
    selfServiceClearPasscode: Optional[str] = "inherit"
    selfServiceLock: Optional[str] = "inherit"
    selfServiceWipe: Optional[str] = "inherit"
    selfServiceUnenroll: Optional[str] = "inherit"
    teacher: Optional[str] = "inherit"
    parent: Optional[str] = "inherit"

    def as_teacher(self):
        self.teacher = "allow"
        self.parent = "inherit"


class UserGroup(BaseModel):
    """
            "id": 1234,
            "locationId": 0,
            "name": "API Group",
            "description": "",
            "userCount": 1,
            "acl": [
                {
                    -> GroupAcl
                }
            ],
            "modified": "2015-05-04 13:37:00"
    """
    id: int = -1
    locationId: int = -1
    name: str = None
    description: str = None
    userCount: int = -1
    acl: GroupAcl = None
    modified: str = None


class ValueObject(BaseModel):
    value: str = ""


class Devices(BaseModel):
    devices: List[Device] = None


class Profile(BaseModel):
    """
    'id' = {int} 5
    'locationId' = {int} 1
    'type' = {dict: 1} {'value': 'default'}
    'status' = {dict: 1} {'value': 'Active'}
    'identifier' = {str} 'com.zuludesk.MDM.iOS.dd9dcb5b6e21874a2601188e30ea6e75'
    'name' = {str} 'Alle Geräte - Blacklist'
    'description' = {str} 'BlackList'
    'platform' = {str} 'iOS'
    'daysOfTheWeek' = {list: 0} []
     __len__ = {int} 0
    'isTemplate' = {bool} False
    'startTime' = {NoneType} None
    'endTime' = {NoneType} None
    'useHolidays' = {bool} False
    'restrictedWeekendUse' = {bool} False

    """
    id: int = None
    locationId: int = None
    identifier: str = None
    name: str = None
    description: str = None
    platform: str = None
    type: ValueObject = None
    status: ValueObject = None
    daysOfTheWeek: List[str] = None
    isTemplate: bool = None
    startTime: str = None
    endTime: str = None
    useHolidays: bool = None
    restrictedWeekendUse: bool = None


class DeviceGroup(BaseModel):
    """
    "description": "Simple group",
    "information": "extra info here",
    "id": 2,
    "isSmartGroup": false,
    "locationId": 0,
    "members": 123,
    "name": "Device Group 1",
    "shared": false,
    "imageUrl": "https://www.zuludesk.com/storage/deviceGroupPhotos/1234567/devicegroup28dc86f067f89c1e72148f639d4cc62c.png",
    "type": "normal"

    """
    description: str = "",
    information: str = "",
    id: int = -1,
    isSmartGroup: bool = False,
    locationId: int = -1,
    members: int = 0,
    name: str = "",
    shared: bool = False,
    imageUrl: Optional[str] = "",
    type: str = ""

    def __eq__(self, other, exact: bool = True):  # second argument dosnt get used any
        if isinstance(other, int):
            return other == self.id
        else:
            return self.match(other=other, exact=exact)

    def match(self, other: str, exact: bool = True):
        if exact:
            return other == self.name
        else:
            return other in self.name


class Placeholder(BaseModel):
    """
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
    """
    id: int = -1
    userId: int = None
    locationId: int = None
    model: str = ""
    color: str = ""
    serialNumber: str = ""
    status: str = ""
    dateAssigned: str = ""
    dateAdded: str = ""
    datePushed: str = ""
    profileName: Optional[str] = ""
    placeholderName: str = ""
    placeholderDeviceName: str = ""
    deviceName: Optional[str] = ""
