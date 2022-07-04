import argparse
import os

from jamf_api import JamfSchool


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--location_id', default=os.environ.get('JAMF_LOCATION_ID'))
    parser.add_argument('--api_key', default=os.environ.get('JAMF_API_KEY'))
    parser.add_argument('--url', default=os.environ.get('JAMF_URL'))

    args = parser.parse_args()
    if not args.url:
        exit(parser.print_usage())

    j = JamfSchool(args.location_id, args.api_key, args.url)

    devices = j.get_device_list()

    for device in devices:
        print(f"{device.serialNumber}: {device.networkInformation.WiFiMAC}")
