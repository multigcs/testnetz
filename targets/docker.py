#!/usr/bin/python3
#
#

import os
import json


def diskimages_get(hostdata, tempdir):
	diskimages = {}
	return diskimages


def info(hostdata, tempdir):
	print(hostdata["hostname"])
	os.system("docker ps -a | grep " + hostdata["hostname"] + "")


def boot(hostdata, tempdir, force = False):
	print(" build docker image")

	dns = ""
	for nameserver in hostdata["network"]["nameservers"]:
		if dns == "":
			dns = nameserver

	## kill and remove ##
	if force == True:
		print("docker rm -f " + hostdata["hostname"] + " 2>/dev/null")
		os.system("docker rm -f " + hostdata["hostname"])
#		print("docker rmi -f " + hostdata["hostname"] + " 2>/dev/null")
#		os.system("docker rmi -f " + hostdata["hostname"])
	## build and run ##
	extraopts = ""
	print("(cd " + tempdir + "; docker build " + extraopts + " -t " + hostdata["hostname"] + " .)")
	os.system("(cd " + tempdir + "; docker build " + extraopts + " -t " + hostdata["hostname"] + " .)")
	print("docker run --cpus='" + str(hostdata["vcpu"]) + "' --memory='" + str(hostdata["memory"]) + "m' --net=none --hostname='" + hostdata["hostname"] + "' --dns='" + dns + "' --dns-search='" + hostdata["domainname"] + "' --name '" + hostdata["hostname"] + "' -d -t -i " + hostdata["hostname"] + "")
	os.system("docker run --cpus='" + str(hostdata["vcpu"]) + "' --memory='" + str(hostdata["memory"]) + "m' --net=none --hostname='" + hostdata["hostname"] + "' --dns='" + dns + "' --dns-search='" + hostdata["domainname"] + "' --name '" + hostdata["hostname"] + "' -d -t -i " + hostdata["hostname"] + "")
	print("nsenter -n -t $(docker inspect --format {{.State.Pid}} " + hostdata["hostname"] + ") ip route add default via " + hostdata["network"]["gateway"] + "")
	## ovs network ##
	for interface in hostdata["network"]["interfaces"]:
		if "ipv4" in hostdata["network"]["interfaces"][interface]:
			for ipv4 in hostdata["network"]["interfaces"][interface]["ipv4"]:
				if interface == "auto":
					idev = "eth0"
				else:
					idev = interface
				if "bridge" in hostdata["network"]["interfaces"][interface]:
					options = ""
					if "hwaddr" in hostdata["network"]["interfaces"][interface]:
						options += " --macaddress=" + hostdata["network"]["interfaces"][interface]["hwaddr"]
					options += " --ipaddress='" + ipv4["address"] + "/" + ipv4["netmask"] + "'"
					print("./ovs-docker add-port " + hostdata["network"]["interfaces"][interface]["bridge"] + " " + idev + " '" + hostdata["hostname"] + "'" + options)
					os.system("./ovs-docker del-port " + hostdata["network"]["interfaces"][interface]["bridge"] + " " + idev + " '" + hostdata["hostname"] + "' 2>/dev/null")
					os.system("./ovs-docker add-port " + hostdata["network"]["interfaces"][interface]["bridge"] + " " + idev + " '" + hostdata["hostname"] + "'" + options)



	os.system("nsenter -n -t $(docker inspect --format {{.State.Pid}} " + hostdata["hostname"] + ") ip route add default via " + hostdata["network"]["gateway"] + "")


	## help commands ##
	print("#docker exec -t -i " + hostdata["hostname"] + " /bin/bash")
	print("#ovs-vsctl show")


def docker2post(dockerfile, tempdir, dockerdata):
	script = ""
	copy = ""
	copy += "mkdir -p " + tempdir + "\n"
	with open(dockerfile) as docker_file:
		hostdata = docker_file.read()
		multiline = False
		lines = hostdata.split("\n")
		ln = 0
		while ln < len(lines):
			if lines[ln].startswith("FROM "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("CMD "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("WORKDIR "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("VOLUME "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("ARG "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("USER "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("STOPSIGNAL "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("LABEL "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("EXPOSE "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("MAINTAINER "):
				while lines[ln].endswith("\\"):
					script += "## " + lines[ln] + "\n"
					ln += 1
				script += "## " + lines[ln] + "\n"
			elif lines[ln].startswith("RUN "):
				lines[ln] = lines[ln][4:]
				while lines[ln].endswith("\\"):
					script += lines[ln] + "\n"
					ln += 1
				script += lines[ln] + "\n"
			elif lines[ln].startswith("ENV "):
				add = ""
				while lines[ln].endswith("\\"):
					add += lines[ln].rstrip("\\")
					ln += 1
				add += lines[ln] + "\n"
				for eline in add.strip().split("\n"):
					script += "export " + eline.split()[1] + "=\"" + eline.split()[2] + "\""
			elif lines[ln].startswith("ADD ") or lines[ln].startswith("COPY "):
				add = ""
				while lines[ln].endswith("\\"):
					add += lines[ln].rstrip("\\")
					ln += 1
				add += lines[ln] + "\n"
				for aline in add.split.strip()("\n"):
					if len(aline.split()) > 2:
						if aline.split()[1].startswith("--"):
							opt = aline.split()[1].split("=")[1]
							script += "chown -R " + opt + " " + target + "\n"
							source = aline.split()[2]
							target = aline.split()[3]
						else:
							source = aline.split()[1]
							target = aline.split()[2]
						copy += "mkdir -p " + tempdir + "/" + target + "\n"
						if source.startswith("http://") or source.startswith("https://"):
							copy += "wget -O " + tempdir + "" + "/" + target + " " + source + "\n"
						else:
							copy += "cp -a " + source + " " + tempdir + "" + "/" + target + "\n"
			elif lines[ln] != "":
				while lines[ln].endswith("\\"):
					script += "#### " + lines[ln] + "\n"
					ln += 1
				script += "#### " + lines[ln] + "\n"
			else:
				script += "\n"
			ln += 1
	return script, copy


