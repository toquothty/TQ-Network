# Author: Thomas Toquothty, VCCS
# This program is to do an operational check of Palo devices.

from pandevice import firewall

fw = firewall.Firewall('IP', 'USER', 'PASS')

#(fw.version, fw.platform, fw.serial)
#refresh_system_info(fw.version, fw.platform, fw.serial)
#print(fw.version, fw.platform, fw.serial)

element_response = fw.op('show system info')
xml_response = fw.op('show system info', xml=True)

print(xml_response)
print()
print(element_response)