#!/usr/bin/python3
#
#
#

import json
import os
import time
from datetime import datetime
import glob
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET

import subprocess
import spice
from HtmlPage import *
from VisGraph import *
from bs import *

inventory = {}
ipv4_ips = {}



class HTTPServer_RequestHandler(BaseHTTPRequestHandler):
	color_n = 0
	colors = ["#008080", "#0000FF", "#FF0000", "#800000", "#FFFF00", "#808000", "#00FF00", "#008000", "#00FFFF", "#000080", "#FF00FF", "#800080"]

	def load_ovs(self):
		bridges = {}
		alltags = []
		bridge = ""
		port = ""
		ovsshow = os.popen("ovs-vsctl show").read()
		ovsshow = os.popen("ovs-vsctl show").read()
		for line in ovsshow.split("\n"):
			if line.strip().startswith("Bridge"):
				bridge = line.split()[1].strip("\"")
				port = ""
				bridges[bridge] = {}
			elif line.strip().startswith("Port"):
				port = line.split()[1].strip("\"")
				bridges[bridge][port] = {}
				bridges[bridge][port]["tag"] = ""
				bridges[bridge][port]["trunks"] = []
				bridges[bridge][port]["vlan_mode"] = ilink = os.popen("ovs-vsctl --columns=vlan_mode list port " + port).read().split()[2].replace("[]", "access/trunk")
			elif line.strip().startswith("Interface"):
				interface = line.split()[1].strip("\"")
				bridges[bridge][port]["interface"] = interface
				ilink = os.popen("ovs-vsctl --columns=external_ids find interface name=" + interface).read()
				bridges[bridge][port]["vm-name"] = ""
				for part in ilink.split(":", 1)[1].strip().strip("{}").split(","):
					if "=" in part:
						name = part.strip().split("=")[0].strip().strip("\"")
						value = part.strip().split("=")[1].strip().strip("\"")
						bridges[bridge][port][name] = value
				if "vm-id" in bridges[bridge][port] and "iface-id" in bridges[bridge][port]:
					dominfo = os.popen("virsh dominfo " + bridges[bridge][port]["vm-id"] + " | grep '^Name:'").read()
					if " " in dominfo:
						bridges[bridge][port]["vm-name"] = dominfo.split()[1]
			elif line.strip().startswith("type:"):
				itype = line.split()[1].strip("\"")
				bridges[bridge][port]["type"] = itype
				bridges[bridge][port]["mac"] = "-----"
				ifconfig = os.popen("ifconfig " + interface).read()
				for iline in ifconfig.split("\n"):
					if iline.strip().startswith("inet "):
						bridges[bridge][port]["ip"] = iline.strip().split()[1]
					elif iline.strip().startswith("ether "):
						bridges[bridge][port]["mac"] = iline.strip().split()[1]
			elif line.strip().startswith("tag:"):
				itag = line.split()[1].strip("\"")
				bridges[bridge][port]["tag"] = itag
			elif line.strip().startswith("trunks:"):
				trunks = line.split(":", 1)[1].strip().strip("[]").split(",")
				for trunk in trunks:
					bridges[bridge][port]["trunks"].append(trunk.strip())
		for bridge in bridges:
			for port in bridges[bridge]:
				if bridges[bridge][port]["tag"] != "":
					alltags.append(int(bridges[bridge][port]["tag"]))
				for trunk in bridges[bridge][port]["trunks"]:
					alltags.append(int(trunk))
		alltags = set(alltags)
		return bridges, alltags


	def show_ovs(self, setport = "", settag = "", settrunk = "", vmod = ""):
		hosts = {}
		for hostfile in glob.glob("hosts/*.json"):
			with open(hostfile) as json_file:
				hostdata = json.load(json_file)
				hosts[hostdata["hostname"]] = hostdata
		html = HtmlPage("vNetwork", "OVS-Overview", "");
		html.add("<div class='modal fade' id='vlanModal' tabindex='-1' role='dialog' aria-labelledby='vlanModalLabel' aria-hidden='true'>\n")
		html.add("  <div class='modal-dialog' role='document'>\n")
		html.add("    <div class='modal-content'>\n")
		html.add("      <div class='modal-header'>\n")
		html.add("        <h5 class='modal-title' id='vlanModalLabel'>Select Tag-Mode: <input id='vlanModalTag' type='text'> -&gt; <b id='vlanModalPort'>-1</b></h5>\n")
		html.add("        <button type='button' class='close' data-dismiss='modal' aria-label='Close'><span aria-hidden='true'>&times;</span></button>\n")
		html.add("      </div>\n")
		html.add("      <div class='modal-footer'>\n")
		html.add("        <button onClick=\"location.href='?port=' + $('#vlanModalPort').html() + '&trunk=' + $('#vlanModalTag').val() + '';\" type='button' class='btn btn-primary' data-dismiss='modal'>Tagged</button>\n")
		html.add("        <button onClick=\"location.href='?port=' + $('#vlanModalPort').html() + '&tag=' + $('#vlanModalTag').val() + '';\" type='button' class='btn btn-primary' data-dismiss='modal'>Untagged</button>\n")
		html.add("      </div>\n")
		html.add("    </div>\n")
		html.add("  </div>\n")
		html.add("</div>\n")
		html.add("<div class='modal fade' id='vlanModeModal' tabindex='-1' role='dialog' aria-labelledby='vlanModeModalLabel' aria-hidden='true'>\n")
		html.add("  <div class='modal-dialog' role='document'>\n")
		html.add("    <div class='modal-content'>\n")
		html.add("      <div class='modal-header'>\n")
		html.add("        <h5 class='modal-title' id='vlanModeModalLabel'>Select VLAN-Mode: <b id='vlanModeModalPort'>-1</b></h5>\n")
		html.add("        <button type='button' class='close' data-dismiss='modal' aria-label='Close'><span aria-hidden='true'>&times;</span></button>\n")
		html.add("      </div>\n")
		html.add("      <div class='modal-footer'>\n")
		html.add("        <button onClick=\"location.href='?port=' + $('#vlanModeModalPort').html() + '&vmode=access';\" type='button' class='btn btn-primary' data-dismiss='modal'>Access</button>\n")
		html.add("        <button onClick=\"location.href='?port=' + $('#vlanModeModalPort').html() + '&vmode=dot1q-tunnel';\" type='button' class='btn btn-primary' data-dismiss='modal'>Dot1q-Tunnel</button>\n")
		html.add("        <button onClick=\"location.href='?port=' + $('#vlanModeModalPort').html() + '&vmode=native-tagged';\" type='button' class='btn btn-primary' data-dismiss='modal'>Native-Tagged</button>\n")
		html.add("        <button onClick=\"location.href='?port=' + $('#vlanModeModalPort').html() + '&vmode=native-untagged';\" type='button' class='btn btn-primary' data-dismiss='modal'>native-untagged</button>\n")
		html.add("        <button onClick=\"location.href='?port=' + $('#vlanModeModalPort').html() + '&vmode=trunk';\" type='button' class='btn btn-primary' data-dismiss='modal'>Trunk</button>\n")
		html.add("        <button onClick=\"location.href='?port=' + $('#vlanModeModalPort').html() + '&vmode=[]';\" type='button' class='btn btn-primary' data-dismiss='modal'>access/trunk</button>\n")
		html.add("      </div>\n")
		html.add("    </div>\n")
		html.add("  </div>\n")
		html.add("</div>\n")
		graph = VisGraph("visgraph", "800px")
		bridges, alltags = self.load_ovs()
		if setport != "" and (settag != "" or settrunk != "" or vmod != ""):
			if settag != "":
				for bridge in bridges:
					if setport in bridges[bridge]:
						if str(settag) == str(bridges[bridge][setport]["tag"]):
							os.system("ovs-vsctl remove port " + setport + " tag " + settag)
						else:
							os.system("ovs-vsctl set port " + setport + " tag=" + settag)
			elif settrunk != "":
				new_trunks = []
				for bridge in bridges:
					if setport in bridges[bridge]:
						if settrunk in bridges[bridge][setport]["trunks"]:
							os.system("ovs-vsctl remove port " + setport + " trunk " + settrunk)
						else:
							bridges[bridge][setport]["trunks"].append(settrunk)
							os.system("ovs-vsctl set port " + setport + " trunk=" + ",".join(bridges[bridge][setport]["trunks"]))
			elif vmod != "":
				os.system("ovs-vsctl set port " + setport + " vlan_mode=" + vmod)
			bridges, alltags = self.load_ovs()
		html.add(bs_row_begin())
		for bridge in bridges:
			html.add(bs_col_begin("12"))
			html.add(bs_card_begin("Bridge: " + bridge, "net"))
			html.add(bs_row_begin())
			html.add(bs_col_begin("12"))
			html.add("<table class='table-striped' width='100%' border='0'>\n")
			html.add("<tr>\n")
			html.add(" <th colspan='3'>Switch</th>\n")
			html.add(" <th colspan='5'>Target</th>\n")
			html.add(" <th colspan='" + str(len(alltags) + 2) + "'>VLANs</th>\n")
			html.add(" <th></th>\n")
			html.add(" </tr>\n")
			html.add("<tr>\n")
			html.add(" <th width='160px'>Port</th>\n")
			html.add(" <th width='120px'>VlanMode</th>\n")
			html.add(" <th width='70px'>Tag</th>\n")
			html.add(" <th width='90px'>Trunks</th>\n")
			html.add(" <th width='100px'>Type</th>\n")
			html.add(" <th width='120px'>Host</th>\n")
			html.add(" <th width='120px'>Login</th>\n")
			html.add(" <th width='70px'>Iface</th>\n")
			html.add(" <th width='160px'>MAC</th>\n")
			for tag in sorted(alltags):
				html.add(" <th width='50px'>&nbsp;&nbsp;" + str(tag) + "</th>\n")
			html.add(" <th width='50px'>&nbsp;&nbsp;NEW</th>\n")
			html.add(" <th></th>\n")
			html.add(" <th></th>\n")
			html.add(" </tr>\n")
			for port in bridges[bridge]:
				html.add("<tr>\n")
				html.add(" <td width='150px'>\n")
				html.add("<img src='assets/MaterialDesignIcons/port.svg' />")
				html.add(port)
				html.add(" </td>\n")
				html.add(" <td onClick=\"$('#vlanModeModalPort').html('" + str(port) + "')\" data-toggle='modal' data-target='#vlanModeModal'>" + bridges[bridge][port]["vlan_mode"] + "</td>")
				html.add(" <td>" + bridges[bridge][port]["tag"] + "</td>")
				html.add(" <td>" + ",".join(bridges[bridge][port]["trunks"]) + "</td>")
				html.add(" <td>\n")
				if "vm-id" in bridges[bridge][port] and "iface-id" in bridges[bridge][port]:
					html.add("<img src='assets/MaterialDesignIcons/monitor.svg' />&nbsp;libvirt")
				elif "container_id" in bridges[bridge][port] and "container_iface" in bridges[bridge][port]:
					html.add("<img src='assets/MaterialDesignIcons/docker.svg' />&nbsp;docker")
				elif "type" in bridges[bridge][port] and bridges[bridge][port]["type"] == "internal":
					html.add("<img src='assets/MaterialDesignIcons/desktop-tower-monitor.svg' />&nbsp;internal")
				html.add(" </td>\n")
				if "vm-id" in bridges[bridge][port] and "iface-id" in bridges[bridge][port]:
					if bridges[bridge][port]["vm-name"] in hosts:
						html.add(" <td><a href='/vhost?host=" + bridges[bridge][port]["vm-name"] + "'>" + bridges[bridge][port]["vm-name"] + "</a></td>")
					else:
						html.add(" <td>" + bridges[bridge][port]["vm-name"] + "</td>")
					spice_port = os.popen("virsh domdisplay " + bridges[bridge][port]["vm-id"] + "").read().strip()
					html.add(" <td><a href='/spice?host=" + bridges[bridge][port]["vm-id"] + "'>" + spice_port + "</a></td>")
					html.add(" <td></td>")
					html.add(" <td>" + bridges[bridge][port]["attached-mac"] + "</td>")
				elif "container_id" in bridges[bridge][port] and "container_iface" in bridges[bridge][port]:
					if bridges[bridge][port]["container_id"] in hosts:
						html.add(" <td><a href='/vhost?host=" + bridges[bridge][port]["container_id"] + "'>" + bridges[bridge][port]["container_id"] + "</a></td>")
					else:
						html.add(" <td>" + bridges[bridge][port]["container_id"] + "</td>")
					html.add(" <td></td>")
					html.add(" <td>" + bridges[bridge][port]["container_iface"] + "</td>")
					html.add(" <td></td>")
				elif "type" in bridges[bridge][port] and bridges[bridge][port]["type"] == "internal":
					html.add(" <td>LOCALHOST</td>")
					html.add(" <td></td>")
					html.add(" <td>" + bridges[bridge][port]["interface"] + "</td>")
					if "mac" in bridges[bridge][port]:
						html.add(" <td>" + bridges[bridge][port]["mac"] + "</td>")
					else:
						html.add(" <td></td>")
				else:
					html.add(" <td></td>")
					html.add(" <td></td>")
					html.add(" <td></td>")
					html.add(" <td></td>")
				for tag in sorted(alltags):
					html.add(" <td>\n")
					if str(tag) == bridges[bridge][port]["tag"] and str(tag) in bridges[bridge][port]["trunks"]:
						html.add("<img onClick=\"$('#vlanModalTag').val('" + str(tag) + "'); $('#vlanModalPort').html('" + str(port) + "')\" data-toggle='modal' data-target='#vlanModal' src='assets/MaterialDesignIcons/vline-con3.svg' />M")
					elif str(tag) in bridges[bridge][port]["trunks"]:
						html.add("<img onClick=\"$('#vlanModalTag').val('" + str(tag) + "'); $('#vlanModalPort').html('" + str(port) + "')\" data-toggle='modal' data-target='#vlanModal' src='assets/MaterialDesignIcons/vline-con2.svg' />T")
					elif str(tag) == bridges[bridge][port]["tag"]:
						html.add("<img onClick=\"$('#vlanModalTag').val('" + str(tag) + "'); $('#vlanModalPort').html('" + str(port) + "')\" data-toggle='modal' data-target='#vlanModal' src='assets/MaterialDesignIcons/vline-con1.svg' />U")
					else:
						html.add("<img onClick=\"$('#vlanModalTag').val('" + str(tag) + "'); $('#vlanModalPort').html('" + str(port) + "')\" data-toggle='modal' data-target='#vlanModal' src='assets/MaterialDesignIcons/vline.svg' />")
					html.add(" </td>\n")

				html.add(" <td>")
				html.add("<img onClick=\"$('#vlanModalTag').val(100); $('#vlanModalPort').html('" + str(port) + "')\" data-toggle='modal' data-target='#vlanModal' src='assets/MaterialDesignIcons/vline.svg' />")
				html.add(" <td>\n")

				html.add(" <td></td>")
				html.add(" </tr>\n")
			html.add("</table>\n")
			html.add(bs_col_end())
			html.add(bs_row_end())
			html.add(bs_card_end())
			html.add(bs_col_end())
		html.add(bs_col_begin("12"))
		html.add(bs_card_begin("vCables", "net"))
		html.add(bs_row_begin())
		html.add(bs_col_begin("12"))
		for bridge in bridges:
			graph.node_add("bridge_" + bridge, bridge, "net")
			for port in bridges[bridge]:
				if "vm-id" in bridges[bridge][port] and "iface-id" in bridges[bridge][port]:
					host = bridges[bridge][port]["vm-name"]
					graph.node_add("host_" + host, host, "monitor")
					graph.edge_add("host_" + host + "_port_" + port, "host_" + host)
				elif "container_id" in bridges[bridge][port] and "container_iface" in bridges[bridge][port]:
					host = bridges[bridge][port]["container_id"]
					iface = bridges[bridge][port]["container_iface"]
					graph.node_add("host_" + host, host, "docker")
					graph.edge_add("host_" + host + "_port_" + port, "host_" + host)
				elif "type" in bridges[bridge][port] and bridges[bridge][port]["type"] == "internal":
					host = "LOCALHOST"
					graph.node_add("host_" + host, host, "desktop-tower-monitor")
					graph.edge_add("host_" + host + "_port_" + port, "host_" + host)
				tag = bridges[bridge][port]["tag"]
				trunks = ",".join(bridges[bridge][port]["trunks"])
				graph.node_add("host_" + host + "_port_" + port, port + "\\n" + tag + "\\nTrunks:" + trunks, "port")
				graph.edge_add("bridge_" + bridge, "host_" + host + "_port_" + port)
		html.add(graph.end())
		html.add(bs_col_end())
		html.add(bs_row_end())
		html.add(bs_card_end())
		html.add(bs_col_end())
		html.add(bs_row_end())
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes(html.end(), "utf8"))
		return

	def show_spice(self, host):
		html = HtmlPage("vNetwork", "vHost-Spice-Login: " + host, "");
		Spice = spice.Spice(host)
		html.add(Spice.show())
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes(html.end(), "utf8"))
		return

	def show_hosts(self):
		html = HtmlPage("vNetwork", "Host-Configs");

		hosts = {}
		hostfiles = {}
		for hostfile in glob.glob("hosts/*.json"):
			with open(hostfile) as json_file:
				hostdata = json.load(json_file)
				hosts[hostdata["hostname"]] = hostdata
				hosts[hostdata["hostname"]]["state"] = "unknown"

				status = os.popen("python3 init.py -i " + hostfile).read()
				for line in status.split("\n"):
					if line.startswith("State:") or "Up" in line:
						hosts[hostdata["hostname"]]["state"] = line
					elif line.startswith("UUID") or line.startswith("OS Type") or line.startswith("CPU") or line.startswith("Used memory"):
						hosts[hostdata["hostname"]]["state"] = "running"

				hosts[hostdata["hostname"]]["file"] = hostfile
				hostfiles[hostdata["hostname"]] = hostfile

		html.add(bs_row_begin())

		html.add(bs_col_begin("12"))
		html.add(bs_card_begin("Host-Configs"))
		html.add(bs_row_begin())
		html.add(bs_col_begin("12"))
		html.add("<table class='table-striped' width='100%' border='0'>\n")
		html.add("<tr>\n")
		html.add(" <th width='160px'>Config</th>\n")
		for option in ["hostname", "domainname", "os", "target", "memory", "vcpu", "source", "state"]:
			html.add("<th>" + option.capitalize() + "</th>")
		html.add(" </tr>\n")

		for host in hosts:
			print(host)
			html.add("<tr>\n")
			html.add(" <td><a href='/vhost?host=" + host + "'>" + hosts[host]["file"].split("/")[-1] + "</a></td>")

			for option in ["hostname", "domainname", "os", "target", "memory", "vcpu", "source", "state"]:
				value = ""
				if option == "source":
					for source in ["iso", "dockerfile", "image"]:
						if source in hosts[host] and str(hosts[host][source]) != "":
							value = str(hosts[host][source])
				elif option in hosts[host]:
					value = str(hosts[host][option])
				html.add("<td>" + value + "</td>")
			html.add(" </tr>\n")

		html.add("</table>\n")
		html.add(bs_col_end())
		html.add(bs_row_end())
		html.add(bs_card_end())
		html.add(bs_col_end())


		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes(html.end(), "utf8"))
		return


	def show_inventory(self):
		data = ""
		oss = {}
		for hostfile in glob.glob("hosts/*.json"):
			with open(hostfile) as json_file:
				hostdata = json.load(json_file)
				oss[hostdata["os"]] = hostdata["os"]
		for os in oss:
			data += "[" + os + "]\n"
			for hostfile in glob.glob("hosts/*.json"):
				with open(hostfile) as json_file:
					hostdata = json.load(json_file)
					exist = False
					if hostdata["os"] == os:
						for dev in hostdata["network"]["interfaces"]:
							for ipv4 in hostdata["network"]["interfaces"][dev]["ipv4"]:
								if exist == False:
									if hostdata["os"] == "centos" or hostdata["os"] == "ubuntu" or hostdata["os"] == "debian" or hostdata["os"] == "opensuse":
										data += hostdata["hostname"] + " ansible_host=" + ipv4["address"] + " ansible_python_interpreter=/usr/bin/python3\n"
									elif hostdata["os"] == "windows":
										data += hostdata["hostname"] + " ansible_host=" + ipv4["address"] + " ansible_user=administrator ansible_password=admin ansible_port=5986 ansible_connection=winrm ansible_winrm_server_cert_validation=ignore\n"
									elif hostdata["os"] == "osx":
										data += hostdata["hostname"] + " ansible_host=" + ipv4["address"] + " ansible_python_interpreter=/usr/bin/python ansible_user=oliver\n"
									elif hostdata["os"] == "openbsd" or hostdata["os"] == "freebsd":
										data += hostdata["hostname"] + " ansible_host=" + ipv4["address"] + " ansible_python_interpreter=/usr/local/bin/python3\n"
									else:
										data += hostdata["hostname"] + " ansible_host=" + ipv4["address"] + "\n"
									exist = True
			data += "\n"

		self.send_response(200)
		self.send_header("Content-type", "text/plain")
		self.end_headers()
		self.wfile.write(bytes(data, "utf8"))
		return

	def show_checkmk(self):
		data = ""

		data += "hostname;ip address;agent\n"
		for hostfile in glob.glob("hosts/*.json"):
			with open(hostfile) as json_file:
				hostdata = json.load(json_file)
				exist = False
				for dev in hostdata["network"]["interfaces"]:
					for ipv4 in hostdata["network"]["interfaces"][dev]["ipv4"]:
						if exist == False:
							data += hostdata["hostname"] + ";" + ipv4["address"] + ";cmk-agent\n"
							exist = True



		self.send_response(200)
		self.send_header("Content-type", "text/plain")
		self.end_headers()
		self.wfile.write(bytes(data, "utf8"))
		return



	def show_vhost(self, host = ""):
		html = HtmlPage("vNetwork", "vHost-Setup: " + host, "");

		hosts = {}
		hostfiles = {}
		for hostfile in glob.glob("hosts/*.json"):
			with open(hostfile) as json_file:
				hostdata = json.load(json_file)
				hosts[hostdata["hostname"]] = hostdata
				hostfiles[hostdata["hostname"]] = hostfile

		html.add(bs_row_begin())

		if not host in hosts:
			html.add("<h2>No config file found for host: " + host + "</h2>")
			html.add(bs_row_end())
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(bytes(html.end(), "utf8"))
			return

		html.add(bs_col_begin("6"))
		html.add(bs_card_begin("Host: " + hosts[host]["hostname"] + "." + hosts[host]["domainname"] + ""))
		html.add(bs_row_begin())
		html.add(bs_col_begin("6"))
		html.add("<table>")
		for option in ["hostname", "domainname", "os", "target", "memory", "vcpu", "iso", "dockerfile", "image"]:
			value = ""
			if option in hosts[host]:
				value = str(hosts[host][option])
			html.add("<tr><td>" + option.capitalize() + ": </td><td><input id='inp_" + option + "' type='text' value='" + value + "'></td></tr>")
		html.add("</table>")
		html.add("<br />")
		html.add(bs_col_end())

		html.add(bs_col_begin("6"))
		html.add("<table>")
		html.add("<tr>")
		html.add(" <td>Nameservers: </td><td><input id='inp_nameservers' type='text' value='" + ", ".join(hosts[host]["network"]["nameservers"]) + "'></td>")
		html.add("</tr>")
		html.add("<tr>")
		html.add(" <td>Default-Gateway: </td><td><input id='inp_gateway' type='text' value='" + hosts[host]["network"]["gateway"] + "'></td>")
		html.add("</tr>")
		html.add("</table>")
		html.add("<br />")
		html.add(bs_col_end())

		html.add(bs_row_end())
		html.add(bs_card_end())
		html.add(bs_col_end())

		html.add(bs_col_begin("6"))
		html.add(bs_card_begin("Guest-Info"))
		html.add(bs_row_begin())
		html.add(bs_col_begin("6"))
		status = os.popen("python3 init.py -i " + hostfiles[host]).read()
		for line in status.split("\n"):
			if line.startswith("State:") or "Up" in line:
				html.add("<b>" + line + "</b><br />")
			elif line.startswith("UUID") or line.startswith("OS Type") or line.startswith("CPU") or line.startswith("Used memory"):
				html.add(line + "<br />")
		html.add(bs_col_end())
		html.add(bs_row_end())
		html.add(bs_card_end())
		html.add(bs_col_end())


		for interface in hosts[host]["network"]["interfaces"]:
			html.add(bs_col_begin("6"))
			html.add(bs_card_begin("Network-Interface: " + interface))
			html.add(bs_row_begin())
			html.add(bs_col_begin("6"))
			html.add(bs_add("<b>Interface:</b>"))
			html.add(bs_table_begin())
			html.add("<tr>")
			html.add(" <td>Bridge: </td><td><input id='inp_iface_" + interface + "_bridge' type='text' value='" + hosts[host]["network"]["interfaces"][interface]["bridge"] + "'></td>")
			html.add("</tr>")
			html.add("<tr>")
			if "hwaddr" in hosts[host]["network"]["interfaces"][interface]:
				html.add(" <td>HWaddress: </td><td><input id='inp_iface_" + interface + "_hwaddr' type='text' value='" + hosts[host]["network"]["interfaces"][interface]["hwaddr"] + "'></td>")
			else:
				html.add(" <td>HWaddress: </td><td><input id='inp_iface_" + interface + "_hwaddr' type='text' value=''></td>")
			html.add("</tr>")
			html.add(bs_table_end())
			html.add(bs_col_end())
			html.add(bs_col_begin("6"))
			ipv4_n = 0
			for ipv4 in hosts[host]["network"]["interfaces"][interface]["ipv4"]:
				html.add(bs_add("<b>IPv4:</b>"))
				html.add(bs_table_begin())
				html.add("<tr>")
				html.add(" <td>Address: </td><td><input id='inp_iface_" + interface + "_ipv4_" + str(ipv4_n) + "_address' type='text' value='" + ipv4["address"] + "'></td>")
				html.add("</tr>")
				html.add("<tr>")
				html.add(" <td>Netmask: </td><td><input id='inp_iface_" + interface + "_ipv4_" + str(ipv4_n) + "_netmask' type='text' value='" + ipv4["netmask"] + "'></td>")
				html.add("</tr>")
				html.add(bs_table_end())
				html.add("<br />")
				ipv4_n += 1
			html.add(bs_col_end())
			html.add(bs_row_end())
			html.add(bs_card_end())
			html.add(bs_col_end())




		for disk in hosts[host]["disks"]:
			html.add(bs_col_begin("6"))
			html.add(bs_card_begin("Disk: " + disk))
			html.add(bs_row_begin())
			html.add(bs_col_begin("6"))
			html.add(bs_add("<b>Disk:</b>"))
			html.add(bs_table_begin())
			if "image" not in hosts[host]["disks"][disk]:
				hosts[host]["disks"][disk]["image"] = ""
			html.add("<tr>")
			html.add(" <td>Size: </td><td><input id='inp_disk_" + disk + "_size' type='text' value='" + hosts[host]["disks"][disk]["size"] + "'></td>")
			html.add("</tr>")
			html.add("<tr>")
			html.add(" <td>Image: </td><td><input id='inp_disk_" + disk + "_image' type='text' value='" + hosts[host]["disks"][disk]["image"] + "'></td>")
			html.add("</tr>")
			html.add(bs_table_end())
			html.add(bs_col_end())
			html.add(bs_col_begin("6"))
#			for partition in hosts[host]["disks"][disk]["partitions"]:
#				html.add(bs_add("<b>IPv4:</b>"))
#				html.add(bs_table_begin())
#				html.add("<tr>")
#				html.add(" <td>Address: </td><td>" + ipv4["address"] + "</td>")
#				html.add("</tr>")
#				html.add("<tr>")
#				html.add(" <td>Netmask: </td><td>" + ipv4["netmask"] + "</td>")
#				html.add("</tr>")
#				html.add(bs_table_end())
#				html.add("<br />")
			html.add(bs_col_end())
			html.add(bs_row_end())
			html.add(bs_card_end())
			html.add(bs_col_end())


		for user in hosts[host]["users"]:
			html.add(bs_col_begin("6"))
			html.add(bs_card_begin("User: " + user))
			html.add(bs_row_begin())
			html.add(bs_col_begin("12"))
			html.add(bs_add("<b>User:</b>"))
			html.add(bs_table_begin())
			html.add("<tr>")
			if "password" not in hosts[host]["users"][user]:
				hosts[host]["users"][user]["password"] = ""
			if "sshpubkey" not in hosts[host]["users"][user]:
				hosts[host]["users"][user]["sshpubkey"] = ""
			html.add("<tr>")
			html.add(" <td>Password: </td><td><input id='inp_user_" + user + "_password' type='text' type='text' value='" + hosts[host]["users"][user]["password"] + "'></td>")
			html.add("</tr>")
			html.add("<tr>")
			html.add(" <td>SSH-Pubkey: </td><td><input id='inp_user_" + user + "_password' type='text' value='" + hosts[host]["users"][user]["sshpubkey"] + "'></td>")
			html.add("</tr>")
			html.add("</tr>")
			html.add(bs_table_end())
			html.add(bs_col_end())
			html.add(bs_row_end())
			html.add(bs_card_end())
			html.add(bs_col_end())
		html.add(bs_row_end())



		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes(html.end(), "utf8"))
		return


	def do_GET(self):
		print(self.path)
		opts = {}
		opts["stamp"] = "0"
		if "?" in self.path:
			for opt in self.path.split("?")[1].split("&"):
				name = opt.split("=")[0]
				value = opt.split("=")[1]
				opts[name] = value
		if self.path.startswith("/ovs"):
			if "port" not in opts:
				opts["port"] = ""
			if "tag" not in opts:
				opts["tag"] = ""
			if "trunk" not in opts:
				opts["trunk"] = ""
			if "vmode" not in opts:
				opts["vmode"] = ""
			self.show_ovs(opts["port"], opts["tag"], opts["trunk"], opts["vmode"])
			return
		elif self.path.startswith("/vhost"):
			if "host" not in opts:
				opts["host"] = ""
			self.show_vhost(opts["host"])
			return
		elif self.path.startswith("/spice"):
			if "host" not in opts:
				opts["host"] = ""
			self.show_spice(opts["host"])
			return
		elif self.path.startswith("/invertory"):
			self.show_inventory()
			return
		elif self.path.startswith("/checkmk"):
			self.show_checkmk()
			return
		elif self.path.startswith("/assets/"):
			if ".." in self.path:
				self.send_response(404)
				self.send_header("Content-type", "text/plain")
				self.end_headers()
				self.wfile.write(bytes("file NO SCANS FOUND: " + self.path, "utf8"))
			else:
				filepath = self.path.split("?")[0]
				if os.path.isfile("." + filepath):
					statinfo = os.stat("." + filepath)
					size = statinfo.st_size
					self.send_response(200)
					self.send_header("Content-length", size)
					if filepath.endswith(".js"):
						self.send_header("Content-type", "application/javascript")
					elif filepath.endswith(".html"):
						self.send_header("Content-type", "text/html")
					elif filepath.endswith(".css"):
						self.send_header("Content-type", "text/css")
					elif filepath.endswith(".png"):
						self.send_header("Content-type", "image/png")
					elif filepath.endswith(".svg"):
						self.send_header("Content-type", "image/svg+xml")
					else:
						self.send_header("Content-type", "text/plain")
					self.end_headers()
					data = open("." + filepath, "rb").read()
					self.wfile.write(data)
				else:
					self.send_response(404)
					self.send_header("Content-type", "text/plain")
					self.end_headers()
					self.wfile.write(bytes("file NO SCANS FOUND: " + self.path, "utf8"))
		else:
			self.show_hosts()
		return


	def show_element(self, element, prefix = ""):
		html = ""
		if type(element) is str:
			html += prefix + str(element) + "<br />\n"
		elif type(element) is int:
			html += prefix + str(element) + "<br />\n"
		elif type(element) is list:
			for part in element:
				bs_add("<br />")
				html += self.show_element(part, prefix + "&nbsp;&nbsp;&nbsp;")
		elif type(element) is dict:
			for part in element:
				bs_add("<br />")
				html += prefix + "<b>" + part + ":</b><br />\n"
				html += self.show_element(element[part], prefix + "&nbsp;&nbsp;&nbsp;")
		return html;


	def matchmark(self, text, old, color):
		index_l = text.lower().index(old.lower())
		return text[:index_l] + "<b style='color: " + color + ";'>" + text[index_l:][:len(old)] + "</b>" + text[index_l + len(old):] 


	def search_element(self, element, search, path = "", matches = {}):
		ret = False
		if type(element) is str:
			if search.lower() in str(element).lower():
				rank = 1
				if search == str(element):
					rank += 1
				if search.lower() == str(element).lower():
					rank += 1
				if str(element).startswith(search):
					rank += 1
				if str(element).lower().startswith(search.lower()):
					rank += 1
				if search in str(element):
					rank += 1
				matches[path] = [rank, str(element)]
				ret = True
		elif type(element) is int:
			if search.lower() in str(element).lower():
				matches[path] = str(element)
				ret = True
		elif type(element) is list:
			n = 0
			for part in element:
				res, matches = self.search_element(part, search, path + "/" + str(n), matches)
				if res == True:
					ret = True
				n += 1
		elif type(element) is dict:
			for part in element:
				res, matches = self.search_element(element[part], search, path + "/" + str(part).replace("ansible_", ""), matches)
				if res == True:
					ret = True
		return ret, matches


def run():
	print('starting server (http://127.0.0.1:8082)...')
	server_address = ('127.0.0.1', 8082)
	httpd = HTTPServer(server_address, HTTPServer_RequestHandler)
	print('running server...')
	httpd.serve_forever()


run()


