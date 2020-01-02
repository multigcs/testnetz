#!/usr/bin/python3
#
#

import os
import json

def mkisofs(tempdir, iso, autoiso, vname, boot = "", catalog = "", options = "", files = {}, wimfiles = {}):
	## extract ISO ##
	if os.path.exists(tempdir + "/iso"):
		os.system("umount " + tempdir + "/iso")
	else:
		os.mkdir(tempdir + "/iso")
	if not os.path.exists(tempdir + "/newiso"):
		os.mkdir(tempdir + "/newiso")
	os.system("mount -r -o loop '" + iso + "' " + tempdir + "/iso")
	os.system("rsync -a '" + tempdir + "/iso/' '" + tempdir + "/newiso/'")
	os.system("umount " + tempdir + "/iso")
	os.rmdir(tempdir + "/iso")

	## copy files ##
	for cfile in files:
		os.system("mkdir -p '" + tempdir + "/newiso/" + "/".join(cfile.rstrip("/").split("/")[:-1]) + "'")
		os.system("cp -a '" + files[cfile][0] + "' '" + tempdir + "/newiso/" + cfile + "'")
		os.system("chmod " + files[cfile][1] + " '" + tempdir + "/newiso/" + cfile + "'")
		os.system("chown " + files[cfile][2] + " '" + tempdir + "/newiso/" + cfile + "'")

	## wimcopy files ##
	if wimfiles != {}:
		if not os.path.exists(tempdir + "/wimfiles"):
			os.mkdir(tempdir + "/wimfiles")
		os.system("wimunmount " + tempdir + "/wimfiles >/dev/null 2>&1")
		os.system("wimmountrw " + tempdir + "/newiso/sources/boot.wim " + tempdir + "/wimfiles")
		for cfile in wimfiles:
			os.system("mkdir -p '" + tempdir + "/wimfiles/" + "/".join(cfile.rstrip("/").split("/")[:-1]) + "'")
			os.system("cp -r '" + wimfiles[cfile][0] + "' '" + tempdir + "/wimfiles/" + cfile + "'")
		os.system("wimunmount --commit " + tempdir + "/wimfiles")

	## build new iso ##
	if boot != "":
		boot = "-b " + boot
	if catalog != "":
		catalog = "-c " + catalog
	os.system("mkisofs " + options + " -V '" + vname + "' -J " + boot + " " + catalog + " -no-emul-boot -cache-inodes -quiet -o '" + autoiso + "' '" + tempdir + "/newiso/'")

	## remove old files ##
	if os.path.exists(tempdir + "/newiso"):
		os.system("rm -rf '" + tempdir + "/newiso/'")

