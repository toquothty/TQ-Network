# Author: Thomas Toquothty, VCCS, 2018
# This program is intended to build a IaaS Tenant
# When applying to device you can use .create() or .apply()
# .create() will merge or create new but will never overwrite
# .apply() will overwrite existing config but best used for new objects so you don't leave leftover parameters

from netmiko import ConnectHandler
import getpass
from pandevice import firewall, objects, network, policies, device

username = input("USER: ")
password = getpass.getpass("PASSWORD: ")
fw_IP = input("Firewall IP: ")
fw = firewall.Firewall(fw_IP, username, password, vsys="shared")

# Pull in existing configurations to check against during creation
print('Firewall system info: {0}'.format(fw.refresh_system_info()))
vsys_list = device.Vsys.refreshall(fw, name_only=True)
print('Found the following vsys: {0}' .format(vsys_list))
tunnel_list = network.TunnelInterface.refreshall(fw, name_only=True)
print ('Found the following tunnel interfaces: {0}' .format(tunnel_list))
print()
print()

# User input of variables for script to run against.
College_ID = input('Input the Colleges short identifier: ').upper()
# VSYS_ID = input('Input the next vsys ID in line in vsysX format, where X is the new number: ')

while True:
    VSYS_ID = input('Input the next vsys ID in line in vsysX format, where X is the new number: ')
    if str(VSYS_ID) in str(vsys_list):
        print('This Vsys already exists, choose another one ')
        continue
    else:
        break
while True:
    Tunnel_ID = 'tunnel.' + input('Input the tunnel number to use: ')
    if str(Tunnel_ID) in str(tunnel_list):
        print('This Tunnel already exists, choose another one ')
        continue
    else:
        break

VLAN = input('Input the first VLAN: ')
VLAN_Subnet = input('Input the subnets Gateway, i.e 10.10.20.1/24: ')
VSYS_Description = College_ID + '_IAAS_VSYS'
VLAN_DC = input('Input the Domain Controller IP: ')
Campus_MGMT = input('Input the name for the Management Subnets: ')
Campus_MGMT_Subnet = input('Input the Campus Management Subnet, i.e 1.1.1.0/24: ')

# Public PAT is commented out until able to determine how to call shared gateway
# Public_PAT = input('Input the PAT Address assigned for this college: ')


vsys = device.Vsys(name = VSYS_ID, display_name = VSYS_Description)
fw.add(vsys)
vsys.create()
print('The VSYS for college ' + College_ID + ' has been created')


# TODO: Create sub-interface with gateway and zone (COLLEGE VSYS)
subint = network.Layer3Subinterface(name = 'ae4.' + VLAN, tag = VLAN, ip = VLAN_Subnet, comment = College_ID + ' IAAS',
                                    management_profile = 'PingOnly')
vsys.add(subint)
subint.apply()
print('The subinterface ae4.' + VLAN + ' has been assigned to AE Interface')

# This will create the tunnel to be used by IPSEC
# TODO: Change vsys1.add to Shared_IAAS_External_GW
Tunnel = network.TunnelInterface(name = Tunnel_ID, comment = College_ID + ' IAAS TUNNEL')
vsys.add(Tunnel)
Tunnel.create()
print('The tunnel interface, ' + Tunnel_ID + ', has been created for the campus')

# This will create the initial Zone for the VLAN
VLAN_zone = network.Zone(name = College_ID + '_' + VLAN, mode = 'layer3', interface = ['ae4.' + VLAN, Tunnel_ID])
vsys.add(VLAN_zone)
VLAN_zone.create()
print('The Initial VLAN Zone, ' + College_ID + '_' + VLAN + ', for the college has been created')

# This will create the External Zone allowing college to access shared gateway
External_Zone = network.Zone(name = College_ID + '_Untrust', mode = 'external', interface = 'sg1')
vsys.add(External_Zone)
External_Zone.create()
print('The External zone for the, ' + College_ID + ' to Untrust has been created')

# This creates the College IaaS to SO IaaS gateway
Inter_Zone = network.Zone(name = College_ID + '_TO_VCCS_SO', mode = 'external')
vsys.add(Inter_Zone)
Inter_Zone.create()
print('The External zone for the , ' + College_ID + ' IaaS to VCCS SO IaaS has been created')

# TODO: Change vsys.add to vsys4.add
# Return_Zone = network.Zone(name = 'VCCS_SO_TO_' + College_ID, mode = 'external')
# vsys.add(Return_Zone)
# Return_Zone.create()
# print('The External zone for the VCCS SO to IAAS ' + College_ID + ' Zone has been created')

# Add Virtual Router to subinterface
IaaS_VRF = network.VirtualRouter(name = 'IAAS', interface = ['ae4.' + VLAN, Tunnel_ID])
fw.add(IaaS_VRF)
IaaS_VRF.create()
print('The created interfaces, ' + 'ae4.' + VLAN + ' and ' + Tunnel_ID + ' have been added to the IAAS Virtual Router')

# Add static route to IAAS VRF
# TODO: Write user input for routes back to college campus.
route = network.StaticRoute(name = College_ID + '_' + Campus_MGMT, destination = Campus_MGMT_Subnet, nexthop_type ='None',
                            interface = Tunnel_ID)
IaaS_VRF.add(route)
route.create()
print('The route has been added to the IAAS Virtual Router')

# TODO: Create four generic starter policies (COLLEGE VSYS)
rulebase = policies.Rulebase()
vsys.add(rulebase)
# TODO: College Zone Outbound (COLLEGE VSYS)
College_Out = policies.SecurityRule(name = College_ID + ' Outbound', fromzone = College_ID + '_' + VLAN,
                                    tozone = College_ID + '_Untrust', service = 'any', action = 'allow')
rulebase.add(College_Out)
College_Out.create()
print('Internal ' + College_ID + ' IaaS to Outbound rule created')

# TODO: College Zone to SO Zone (COLLEGE VSYS)
College_SO = policies.SecurityRule(name = College_ID + 'to SO Servers',
                                   fromzone = [College_ID + '_' + VLAN, College_ID + '_TO_VCCS_SO'],
                                   tozone = [College_ID + '_' + VLAN, College_ID + '_TO_VCCS_SO'],
                                   service = 'any', action = 'allow')
rulebase.add(College_SO)
College_SO.create()
print('Internal ' + College_ID + ' IaaS to VCCS SO IaaS Rule created')

College_Inbound = policies.SecurityRule(name = 'Inbound From ' + College_ID + 'Campus',
                                        fromzone = College_ID + '_Untrust', source = Campus_MGMT_Subnet,
                                        tozone = College_ID + '_' + VLAN, service = 'any', action = 'allow')
rulebase.add(College_Inbound)
College_Inbound.create()
print('External rule allowing ' + College_ID + ' campus subnets inbound created')

Deny_Log = policies.SecurityRule(name = 'Deny Log', fromzone = 'any', tozone = 'any', action = 'deny')
rulebase.add(Deny_Log)
Deny_Log.create()
print('Catch all deny rule created for logging purposes')

# Creates the NoNAT
# College_NoNAT = policies.NatRule(name = 'NO_NAT_' + College_ID, tozone = 'Shared_Untrust', source = VLAN_Subnet,
#                                  to_interface = Tunnel_ID)
# sg1_rulebaserulebase.add(College_NoNAT)
# College_NoNAT.create()
# print('The college NO NAT has been created')

# Creates the IaaS Zone PAT
# College_PAT = policies.NatRule(name = College_ID + '_IAAS_PAT', tozone = 'Shared_Untrust', source = VLAN_Subnet,
#                                source_translation_type = 'dynamic-ip-and-port',
#                                source_translation_translated_addresses = Public_PAT)
# rulebase.add(College_PAT)
# College_PAT.create()
# print('The college IaaS PAT has been created')

# TODO: Change vsys1.add to vsys.4 for prod
#IAAS_DC = objects.AddressObject(name = College_ID + '_IAAS_DC', value = VLAN_DC,
#                                    description= College_ID + 'IaaS Domain Controller')
#vsys.add(IAAS_DC)
#IAAS_DC.apply()
#IaaS_DCs = objects.AddressGroup(name = 'IaaS_DCs', static_value = [IAAS_DC])
#vsys.add(IaaS_DCs)
#IaaS_DCs.create()
#print('The college IAAS has been created and added the the IaaS_DCs group')


# TODO: Change vsys1.add to vsys4.add for prod)
#IAAS_MGMT = objects.AddressObject(College_ID + '_IAAS_MGMT', Campus_MGMT)
#vsys.add(IAAS_MGMT)
#IAAS_MGMT.create()
#print('The college Campus management subnets have been created')


# TODO: Add Group to vRealize Access Rule as source (SO VSYS)
# College_vRealize = policies.SecurityRule(name = 'vRealize Access', source = [XXX_MGMT])
# vsys4.rulebase.add(College_vRealize)
# College_vRealize.create()
# print('Adds college management subnet to vRealize')

# TODO: Add group to vRom Access Rule as source (SO VSYS)
# College_vRom = policies.SecurityRule(name = 'vROM Access', source = [XXX_MGMT])
# vsys4.rulebase.add(College_vRom)
# College_vRom.create()
# print('Adds college management subnet to vRom')

# TODO: Create Rule for IaaS-Allowed-DC (SO VSYS)
# College_DC = policies.SecurityRule(name = 'XXX-Allowed-DCs', fromzone = ['VCCS_SO_TO_TEST', 'VCCS_SO_IAAS_700'],
#                                   source = '10.70.80.10', tozone = ['VCCS_SO_TO_TEST', 'VCCS_SO_IAAS_700'],
#                                   destination = ['VCCS_IAAS_CoreServers'], service = 'any', action = 'allow')
# vsys4.rulebase.add(College_DC)
# College_DC.create()
# print('Rule created to allow IaaS DC to access SO DC')

# TODO: Source: VCCS-SO-to-COLLEGE, VCCS_SO_IAAS_700
# SO_to_College = policies.SecurityRule(name = 'VCCS-to-Colleges', fromzone = ['InternalManagement', 'VCCS_SO_IAAS_700'],
#                                      source = 'VCCS_IAAS_CoreServers', tozone = ['VCCS_SO_TO_TEST'],
#                                      service = 'any', action = 'allow')
# vsys4.rulebase.add(CO_to_College)
# CO_to_College.create()
# print('Rule created to allow IaaS DC to access SO DC')
#
# fw.commit(sync=True)

