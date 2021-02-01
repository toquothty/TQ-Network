import json
import requests
import getpass
import urllib3

# Global variables pulling URL, username and password.
# Initialize token which apic_login() function will fill to be passed.
APIC_URL = "https://10.1.111.11/"
username = input("USER: ")
password = getpass.getpass("PASSWORD: ")
token = ""

def apic_login():
    """ Login to APIC """

    global token
    token = ""
    err = ""

    try:
        response = requests.post(
            url=APIC_URL + "api/aaaLogin.json",
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=json.dumps(
                {
                    "aaaUser": {
                        "attributes": {
                            "name": username,
                            "pwd": password
                        }
                    }
                }
            ),
            verify=False
        )
        json_response = json.loads(response.content)
        token = json_response['imdata'][0]['aaaLogin']['attributes']['token']
        print(token)

        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
    except requests.exceptions.RequestException as err:
        print("HTTP Request failed")
        print(err)

    return token


def get_tenants():
    """ Get Tenants """


    url = APIC_URL + "api/node/class/fvTenant.json"
    print('GET request resource: ', url)

    try:
        response = requests.get(
            url,
            headers={
                "Cookie": "APIC-cookie=" + token,
                "Content-Type": "application/json; charset=utf-8",
            },
            verify=False
        )

        # Write Tenants to file in json format
        with open("C:\Python\ACI_Tenants.txt", "w") as outfile:
            outfile.write('Response HTTP Status Code: {status_code}\n'.format(
                status_code=response.status_code))
            tenants = json.dumps(response.json(), indent=4)
            outfile.write(tenants)

    except requests.exceptions.RequestException:
        print("HTTP Request failed")


def get_devices():
    """ Get Devices """


    url = APIC_URL + "api/node/class/topology/pod-1/topSystem.json"
    print('GET request resource: ', url)

    try:
        response = requests.get(
            url,
            headers={
                "Cookie": "APIC-cookie=" + token,
                "Content-Type": "application/json; charset=utf-8"
            },
            verify=False)

        # Write ACI Devices to text in json format.
        with open("C:\Python\ACI_Devices.txt", "w") as outfile:
            outfile.write('Response HTTP Status Code: {status_code}\n'.format(
                status_code=response.status_code))
            devices = json.dumps(response.json(), indent=4)
            outfile.write(devices)

    except requests.exceptions.RequestException:
        print("HTTP Request failed")


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print('=========================LOGIN TO APIC=====================')
apic_login()
print('=========================GET TENANTS=======================')
get_tenants()
print('=========================GET DEVICES=======================')
get_devices()

# TODO: Pull all VPCs, total number of Up Links, be able to compare at quick glance
# TODO: Pull OSPF instance/routes/number of routes/routing peers
