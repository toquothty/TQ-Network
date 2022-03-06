# Borrowed sample data from Corey Shafer python RE video
from platform import platform
import re
from netmiko import ConnectHandler
import getpass

username = "developer"
password = "C1sco12345"
devices = {
    "sandbox_CSR": {"host": "sandbox-iosxe-recomm-1.cisco.com", "platform": "cisco_xe"}
}

results = {}

for device_name, device_data in devices.items():
    print(f"Connecting to {device_name}...")

    net_connect = ConnectHandler(
        host=device_data["host"],
        device_type=device_data["platform"],
        username=username,
        password=password,
    )
    results[device_name] = net_connect.send_command("show interface")

print(results)
print("Parsing Results.....")
parsed_result = {}
for device_name, result in results.items():
    parsed_result[device_name] = {}
    parsed_result[device_name]["interface"] = re.search(
        r"([A-Za-z]+[\d]+) is up", result, re.MULTILINE
    )
    parsed_result[device_name]["description"] = re.search(
        r"Description: (.*)$", result, re.MULTILINE
    )
    parsed_result[device_name]["IP"] = re.search(
        r"Internet address is (.*)$", result, re.MULTILINE
    )
    parsed_result[device_name]["input_bits"] = re.search(
        r"input rate (\d*) bits/sec", result, re.MULTILINE
    )
    parsed_result[device_name]["output_bits"] = re.search(
        r"output rate (\d*) bits/sec", result, re.MULTILINE
    )
    parsed_result[device_name]["physical_errors"] = re.search(
        r"(\d* input errors, \d* CRC)", result, re.MULTILINE
    )

for result in results.keys():
    print(f"{device_name} information:")
    print(f"\tInterface: {parsed_result[device_name]['interface'].group(1)}")
    print(f"\tDescription: {parsed_result[device_name]['description'].group(1)}")
    print(f"\tIP: {parsed_result[device_name]['IP'].group(1)}")
    print(
        f"\tIngress Traffic: {parsed_result[device_name]['input_bits'].group(1)} bits/sec"
    )
    print(
        f"\tEgress Traffic: {parsed_result[device_name]['output_bits'].group(1)} bits/sec"
    )
    print(
        f"\tPhysical Errors: {parsed_result[device_name]['physical_errors'].group(1)}"
    )
