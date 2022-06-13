# jamf API v1

- zudludesc API implementation
- uses pydantic BaseModel to validate

# Installation

```
python -m venv venv
source ./venv/bin/activate
python -m pip install -r requirements.txt
```

Set the following env variables:

```
JAMF_LOCATION_ID
JAMF_API_KEY
JAMF_URL
```

(if no Location id or api key is provided, it trys to get the info via keyring)

# Usage

Run the `get_wifimac.py`

```
source ./venv/bin/activate
python get_wifimac.py
```

or e.g. with arguments
```
source ./venv/bin/activate
python get_wifimac.py --loaction_id "129832" --api_key "UJIBSIKBI" --url "https:yourlocation.jamfcloud.com/api"
```
