# Borrowed sample data from Corey Shafer python RE video
from platform import platform
import re
from netmiko import ConnectHandler
import getpass

platform = "cisco_xe"  # Set platform that netmiko will match against
username = "developer"
password = getpass.getpass("Password: ")
devices = ["sandbox-iosxe-recomm-1.cisco.com"]

results = []
target_interfaces = []

for device in devices:
    print(f"Connecting to {device}...")

    net_connect = ConnectHandler(
        host=device,
        device_type=platform,
        username=username,
        password=password,
    )
    results = net_connect.send_command("show interface")
    print("Parsing Results.....")

    # Search for interfaces that are up
    for interface in re.finditer(r"([A-Za-z]+[\d]+) is up", results, re.MULTILINE):
        target_interfaces.append(interface.group(1))

    for interface in target_interfaces:

        show_interface = net_connect.send_command(f"show interface {interface}")

        IP = re.search(
            r"Internet address is (\d*\.\d*\.\d*\.\d*/\d*)",
            show_interface,
            re.MULTILINE,
        )
        input_bits = re.search(
            r"input rate (\d*) bits/sec", show_interface, re.MULTILINE
        )
        output_bits = re.search(
            r"output rate (\d*) bits/sec", show_interface, re.MULTILINE
        )
        physical_errors = re.search(
            r"(\d* input errors, \d* CRC)", show_interface, re.MULTILINE
        )
        print(f"Interface: {interface}")
        if IP:
            print(f"\tIP: {IP.group(1)}")
        else:
            print(f"\tIP: None")
        print(f"\tIngress Traffic: {input_bits.group(1)} bits/sec")
        print(f"\tEgress Traffic: {output_bits.group(1)} bits/sec")
        print(f"\tPhysical Errors: {physical_errors.group(1)}")
