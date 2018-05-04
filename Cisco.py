from netmiko import ConnectHandler
import getpass
import sys


Config_Out = open('C:\Python\Output.txt', 'a')  # Create/Append the following file

platform = 'cisco_ios'
username = input("USER: ")
password = getpass.getpass("PASSWORD: ")
sys.stdout = Config_Out  # Write past here to the file created
ip_address_file = open('C:\Python\IPs.txt', 'r')  # Read from this file the IPs needed

for host in ip_address_file:
	host = host.strip()  # Ignore white space at the end of the line in file
	net_connect = ConnectHandler(device_type=platform, ip=host, username=username, password=password)
	output = net_connect.send_command("show version | s uptime")
	print(output)
	output = net_connect.send_command("show version | s Processor")
	print(output)
	output = net_connect.send_command("show version | s Software")
	print(output)
	print("*****END*****")
	print()
