from netmiko import ConnectHandler
import getpass
import sys

platform = 'cisco_xe'
username = input("USER: ")
password = getpass.getpass("PASSWORD: ")
ip_address_file = open('C:\Python\IPs.txt', 'r')  # Read from this file the IPs needed

for host in ip_address_file:
	host = host.strip()  # Ignore white space at the end of the line in file
	print("Connecting to host: ", host)
	net_connect = ConnectHandler(device_type=platform, ip=host, username=username, password=password)
	makeFile = open("C:\Python\\" + host + ".txt", "w")
	makeFile.write(host) 
	makeFile.write("\n" * 2 + "Software Version: " + "\n" + net_connect.send_command("show version | s XE Software"))
	makeFile.write("\n" * 2 + "Router Serial: " + "\n" + net_connect.send_command("show version | s ID"))
	makeFile.write("\n" * 2 + "Default Route Learned: " + "\n" + net_connect.send_command("show ip route 0.0.0.0"))
	makeFile.write("\n" * 2 + "BGP Neighbor Summary: " + "\n" + net_connect.send_command("show ip bgp summary"))
	makeFile.write("\n" * 2 + "OSPF Neighbor Summary: " + "\n" + net_connect.send_command("show ip ospf neighbor"))
	print("*****END*****")
	print()
