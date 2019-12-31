#!/usr/bin/python3
#
#

import os
import json
import mkisofs
from ipaddress import IPv4Network

def get_files():
	files = {}
	return files

def pxe(bootserver):
	isolinuxtxtnet = ""
	return isolinuxtxtnet

def autoseed(hostdata, tempdir, services):
	if "iso" in hostdata:
		if not os.path.exists(hostdata["iso"]):
			print("  ISO not found on local filesystem (" + hostdata["iso"] + ")...")
			rfiles = get_files()
			if hostdata["iso"] in rfiles:
				print("   Get ISO from " + rfiles[hostdata["iso"]] + "...")
				os.system("wget -O " + hostdata["iso"] + " " + rfiles[hostdata["iso"]])
			else:
				return
	version = "Windows 10 Pro"
	orga = "multiXmedia"
	windomain = "MULTIXMEDIA"
	oobe = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
	oobe += "<unattend xmlns=\"urn:schemas-microsoft-com:unattend\">\n"
	oobe += "<servicing></servicing>\n"
	oobe += "<settings pass=\"windowsPE\">\n"
	oobe += " <component name=\"Microsoft-Windows-International-Core-WinPE\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <SetupUILanguage>\n"
	oobe += "   <UILanguage>DE-AT</UILanguage>\n"
	oobe += "  </SetupUILanguage>\n"
	oobe += "  <InputLocale>0c07:00000407</InputLocale>\n"
	oobe += "  <UILanguage>de-DE</UILanguage>\n"
	oobe += "  <UILanguageFallback>de-DE</UILanguageFallback>\n"
	oobe += "  <UserLocale>de-AT</UserLocale>\n"
	oobe += "  <SystemLocale>de-DE</SystemLocale>\n"
	oobe += " </component>\n"
	oobe += " <component name=\"Microsoft-Windows-Setup\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <DiskConfiguration>\n"
	oobe += "   <Disk wcm:action=\"add\">\n"
	oobe += "    <CreatePartitions>\n"
	oobe += "     <CreatePartition wcm:action=\"add\">\n"
	oobe += "      <Order>2</Order>\n"
	oobe += "      <Type>Primary</Type>\n"
	oobe += "      <Extend>true</Extend>\n"
	oobe += "     </CreatePartition>\n"
	oobe += "     <CreatePartition wcm:action=\"add\">\n"
	oobe += "      <Order>1</Order>\n"
	oobe += "      <Size>500</Size>\n"
	oobe += "      <Type>Primary</Type>\n"
	oobe += "     </CreatePartition>\n"
	oobe += "    </CreatePartitions>\n"
	oobe += "    <ModifyPartitions>\n"
	oobe += "     <ModifyPartition wcm:action=\"add\">\n"
	oobe += "      <Active>true</Active>\n"
	oobe += "      <Format>NTFS</Format>\n"
	oobe += "      <Label>System reserviert</Label>\n"
	oobe += "      <Order>1</Order>\n"
	oobe += "      <PartitionID>1</PartitionID>\n"
	oobe += "      <TypeID>0x27</TypeID>\n"
	oobe += "     </ModifyPartition>\n"
	oobe += "     <ModifyPartition wcm:action=\"add\">\n"
	oobe += "      <Order>2</Order>\n"
	oobe += "      <Active>true</Active>\n"
	oobe += "      <Format>NTFS</Format>\n"
	oobe += "      <Label>System</Label>\n"
	oobe += "      <Letter>C</Letter>\n"
	oobe += "      <PartitionID>2</PartitionID>\n"
	oobe += "     </ModifyPartition>\n"
	oobe += "    </ModifyPartitions>\n"
	oobe += "   <DiskID>0</DiskID>\n"
	oobe += "   <WillWipeDisk>true</WillWipeDisk>\n"
	oobe += "   </Disk>\n"
	oobe += "  </DiskConfiguration>\n"
	oobe += "  <ImageInstall>\n"
	oobe += "   <OSImage>\n"
	oobe += "    <InstallTo>\n"
	oobe += "     <DiskID>0</DiskID>\n"
	oobe += "     <PartitionID>2</PartitionID>\n"
	oobe += "    </InstallTo>\n"
	oobe += "    <WillShowUI>OnError</WillShowUI>\n"
	oobe += "    <InstallFrom>\n"
	oobe += "     <MetaData wcm:action=\"add\">\n"
	oobe += "      <Key>/image/name</Key>\n"
	oobe += "      <Value>" + version + "</Value>\n"
	oobe += "     </MetaData>\n"
	oobe += "    </InstallFrom>\n"
	oobe += "   </OSImage>\n"
	oobe += "  </ImageInstall>\n"
	oobe += "  <UserData>\n"
	oobe += "  <AcceptEula>true</AcceptEula>\n"
	oobe += "  <Organization>" + orga + "</Organization>\n"
	oobe += "  <ProductKey>\n"
	oobe += "   <Key></Key>\n"
	oobe += "   <WillShowUI>OnError</WillShowUI>\n"
	oobe += "  </ProductKey>\n"
	oobe += "  </UserData>\n"
	oobe += " </component>\n"
	oobe += "</settings>\n"

	oobe += "<settings pass=\"specialize\">\n"


	## disable Firewall (PrivateProfile) ##
	oobe += " <component name=\"Networking-MPSSVC-Svc\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <PrivateProfile_EnableFirewall>false</PrivateProfile_EnableFirewall>\n"
	oobe += "  <DomainProfile_EnableFirewall>true</DomainProfile_EnableFirewall>\n"
	oobe += "  <PublicProfile_EnableFirewall>true</PublicProfile_EnableFirewall>\n"
	oobe += " </component>\n"


	## IPs and Routes ##
	oobe += " <component name=\"Microsoft-Windows-TCPIP\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <Interfaces>\n"
	for interface in hostdata["network"]["interfaces"]:
		oobe += "   <Interface wcm:action=\"add\">\n"
		oobe += "    <Identifier>" + hostdata["network"]["interfaces"][interface]["hwaddr"].upper().replace(":", "-") + "</Identifier>\n"
		oobe += "    <Ipv4Settings>\n"
		oobe += "     <DhcpEnabled>false</DhcpEnabled>\n"
		oobe += "     <Metric>10</Metric>\n"
		oobe += "     <RouterDiscoveryEnabled>false</RouterDiscoveryEnabled>\n"
		oobe += "    </Ipv4Settings>\n"
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				oobe += "    <UnicastIpAddresses>\n"
				oobe += "     <IpAddress wcm:action=\"add\" wcm:keyValue=\"1\">" + ipv4["address"] + "/" + str(IPv4Network("0.0.0.0/" + ipv4["netmask"]).prefixlen) + "</IpAddress>\n"
				oobe += "    </UnicastIpAddresses>\n"
		oobe += "    <Routes>\n"
		oobe += "     <Route wcm:action=\"add\">\n"
		oobe += "     <Identifier>1</Identifier>\n"
		oobe += "     <Metric>10</Metric>\n"
		oobe += "      <NextHopAddress>" + hostdata["network"]["gateway"] + "</NextHopAddress>\n"
		oobe += "     <Prefix>0.0.0.0/0</Prefix>\n"
		oobe += "    </Route>\n"
		oobe += "    </Routes>\n"
		oobe += "   </Interface>\n"
	oobe += "  </Interfaces>\n"
	oobe += " </component>\n"
	## DNS-Server ##
	oobe += " <component name=\"Microsoft-Windows-DNS-Client\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <Interfaces>\n"
	for interface in hostdata["network"]["interfaces"]:
		oobe += "   <Interface wcm:action=\"add\">\n"
		oobe += "    <Identifier>" + hostdata["network"]["interfaces"][interface]["hwaddr"].upper().replace(":", "-") + "</Identifier>\n"
		oobe += "    <DNSDomain>" + hostdata["domainname"] + "</DNSDomain>\n"
		oobe += "    <DNSServerSearchOrder>\n"
		dns_n = 1
		for nameserver in hostdata["network"]["nameservers"]:
			oobe += "     <IpAddress wcm:action=\"add\" wcm:keyValue=\"" + str(dns_n) + "\">" + nameserver + "</IpAddress>\n"
			dns_n += 1
		oobe += "    </DNSServerSearchOrder>\n"
		oobe += "    <EnableAdapterDomainNameRegistration>true</EnableAdapterDomainNameRegistration>\n"
		oobe += "    <DisableDynamicUpdate>false</DisableDynamicUpdate>\n"
		oobe += "   </Interface>\n"
	oobe += "  </Interfaces>\n"
	oobe += " </component>\n"


	## windows-domain ##
	oobe += " <component name=\"Microsoft-Windows-Shell-Setup\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <OEMInformation>\n"
	oobe += "   <Manufacturer>" + orga + "</Manufacturer>\n"
	oobe += "   <SupportURL></SupportURL>\n"
	oobe += "   <SupportPhone>+49 (0) 000 / 00000</SupportPhone>\n"
	oobe += "   <HelpCustomized>false</HelpCustomized>\n"
	oobe += "  </OEMInformation>\n"
	oobe += "  <ComputerName>" + hostdata["hostname"] + "</ComputerName>\n"
	oobe += "  <RegisteredOrganization>" + orga + "</RegisteredOrganization>\n"
	oobe += " </component>\n"
#	oobe += " <component name=\"Microsoft-Windows-UnattendedJoin\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
#	oobe += "  <Identification>\n"
#	oobe += "  <Credentials>\n"
#	oobe += "   <Domain>" + hostdata["domainname"] + "</Domain>\n"
#	oobe += "   <Password>passwort</Password>\n"
#	oobe += "   <Username>domainjoin</Username>\n"
#	oobe += "  </Credentials>\n"
#	oobe += "  <JoinDomain>" + windomain + "</JoinDomain>\n"
#	oobe += "  <MachineObjectOU>OU=Clients,DC=" + hostdata["domainname"].replace(".", ",DC=") + "</MachineObjectOU>\n"
#	oobe += "  </Identification>\n"
#	oobe += " </component>\n"

	oobe += "</settings>\n"

	oobe += "<settings pass=\"oobeSystem\">\n"
	oobe += " <component name=\"Microsoft-Windows-Shell-Setup\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <OOBE>\n"
	oobe += "   <HideEULAPage>true</HideEULAPage>\n"
	oobe += "   <HideLocalAccountScreen>true</HideLocalAccountScreen>\n"
	oobe += "   <HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>\n"
	oobe += "   <HideOnlineAccountScreens>true</HideOnlineAccountScreens>\n"
	oobe += "   <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>\n"
	oobe += "   <ProtectYourPC>1</ProtectYourPC>\n"
	oobe += "  </OOBE>\n"
	## post scripts ##
	oobe += "  <FirstLogonCommands>\n"
	cmd_n = 1
#	 "REG.exe add HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkstation\\Parameters /v DomainCompatibilityMode /t REG_DWORD /d 1 /f",
#	 "REG.exe add HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkstation\\Parameters /v DNSNameResolutionRequired /t REG_DWORD /d 0 /f",
	for cmd in ["D:\\wintools\\firefox-setup.exe /S",
	 "powershell -ExecutionPolicy Bypass -File D:\\wintools\\ConfigureRemotingForAnsible.ps1",
	 "msiexec /i D:\\wintools\\check_mk_agent.msi /qn",
	 "D:\\wintools\\thunderbird-setup.exe /S",
	 "D:\\wintools\\foobar2000_v1.4.6.exe /S",
	 "D:\\wintools\\peazip-6.9.0.WIN64.exe /verysilent",
	 "D:\\wintools\\FoxitReader96_L10N_Setup_Prom.exe /verysilent",
	 "D:\\wintools\\iview453g_x64_setup.exe /silent",
	 "D:\\wintools\\LibreOffice_6.3.0_Win_x64.msi /quiet",
	]:
		oobe += "   <SynchronousCommand wcm:action=\"add\">\n"
		oobe += "    <Order>" + str(cmd_n) + "</Order>\n"
		oobe += "    <CommandLine>" + cmd + "</CommandLine>\n"
		oobe += "    <RequiresUserInput>true</RequiresUserInput>\n"
		oobe += "   </SynchronousCommand>\n"
		cmd_n += 1

	for service in services:
		if service != "":
			oobe += "\n"
			#oobe += "   <SynchronousCommand wcm:action=\"add\">\n"
			#oobe += "    <Order>" + str(cmd_n) + "</Order>\n"
			#oobe += "    <CommandLine>D:\\wintools\\service_" + service + ".bat</CommandLine>\n"
			#oobe += "    <RequiresUserInput>true</RequiresUserInput>\n"
			#oobe += "   </SynchronousCommand>\n"
			cmd_n += 1

	oobe += "  </FirstLogonCommands>\n"
	## users ##
	oobe += "  <UserAccounts>\n"
	oobe += "   <LocalAccounts>\n"
	oobe += "    <LocalAccount wcm:action=\"add\">\n"
	oobe += "     <Password>\n"
	oobe += "      <Value>admin</Value>\n"
	oobe += "      <PlainText>true</PlainText>\n"
	oobe += "     </Password>\n"
	oobe += "     <DisplayName>Administrator</DisplayName>\n"
	oobe += "     <Name>administrator</Name>\n"
	oobe += "     <Group>Administrators</Group>\n"
	oobe += "    </LocalAccount>\n"
	oobe += "   </LocalAccounts>\n"
	oobe += "   <AdministratorPassword>\n"
	oobe += "    <Value>admin</Value>\n"
	oobe += "    <PlainText>true</PlainText>\n"
	oobe += "   </AdministratorPassword>\n"
	oobe += "  </UserAccounts>\n"
	oobe += "  <AutoLogon>\n"
	oobe += "   <Username>administrator</Username>\n"
	oobe += "   <Password>\n"
	oobe += "    <Value>admin</Value>\n"
	oobe += "    <PlainText>true</PlainText>\n"
	oobe += "   </Password>\n"
	oobe += "   <Domain></Domain>\n"
	oobe += "   <Enabled>true</Enabled>\n"
	oobe += "  </AutoLogon>\n"
	oobe += " </component>\n"

	oobe += " <component name=\"Microsoft-Windows-Deployment\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <Reseal>\n"
	oobe += "   <Mode>OOBE</Mode>\n"
	oobe += "  </Reseal>\n"
	oobe += " </component>\n"
	oobe += " <component name=\"Microsoft-Windows-International-Core\" processorArchitecture=\"amd64\" publicKeyToken=\"31bf3856ad364e35\" language=\"neutral\" versionScope=\"nonSxS\" xmlns:wcm=\"http://schemas.microsoft.com/WMIConfig/2002/State\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
	oobe += "  <InputLocale>0c07:00000407</InputLocale>\n"
	oobe += "  <SystemLocale>de-DE</SystemLocale>\n"
	oobe += "  <UILanguage>de-DE</UILanguage>\n"
	oobe += "  <UILanguageFallback>de-DE</UILanguageFallback>\n"
	oobe += "  <UserLocale>de-AT</UserLocale>\n"
	oobe += " </component>\n"
	oobe += "</settings>\n"
	oobe += "<cpi:offlineImage cpi:source=\"wim:c:/win10-setup/sources/install.wim#" + version + "\" xmlns:cpi=\"urn:schemas-microsoft-com:cpi\" />\n"
	oobe += "</unattend>\n"
	with open(tempdir + "/Autounattend.xml", "w") as ofile:
		ofile.write(oobe)

	if "iso" in hostdata:
		if not os.path.exists(tempdir + "/auto.iso"):
			copy = {
				"Autounattend.xml": [tempdir + "/Autounattend.xml", "666", "root"],
				"wintools": ["files/windows", "666", "root"],
			}
			for service in services:
				if service != "":
					copy["service_" + service.split("/")[-1]] = [tempdir + "/services/" + service.split("/")[-1], "777", "root"]
			mkisofs.mkisofs(
				tempdir,
				hostdata["iso"],
				tempdir + "/auto.iso",
				"CCCOMA_X64FRE_DE-DE_DV9",
				"boot/etfsboot.com",
				"",
				"-no-emul-boot -hide boot.bin -hide boot.catalog -udf -J -r -allow-limited-size",
				copy
			)


