#!@PYTHON@ -O
# Copyright 1999-2006 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id$

import os,sys
os.environ["FEATURES"]="mirror cvs"

# for an explanation on this logic, see pym/_emerge/__init__.py
import os
import sys
if os.environ.__contains__("PORTAGE_PYTHONPATH"):
	sys.path.insert(0, os.environ["PORTAGE_PYTHONPATH"])
else:
	sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pym"))
import portage

import portage.util

def cstrip(mystr,mychars):
	newstr = ""
	for x in mystr:
		if x not in mychars:
			newstr += x
	return newstr

md5_list = {}
bn_list  = []
col_list = []

hugelist = []
for mycp in portage.db["/"]["porttree"].dbapi.cp_all():
	hugelist += portage.db["/"]["porttree"].dbapi.cp_list(mycp)
hugelist.sort()

for mycpv in hugelist:
	pv = mycpv.split("/")[-1]

	newuri = portage.db["/"]["porttree"].dbapi.aux_get(mycpv,["SRC_URI"])[0]
	newuri = newuri.split()

	digestpath = portage.db["/"]["porttree"].dbapi.findname(mycpv)
	digestpath = os.path.dirname(digestpath)+"/files/digest-"+pv
	md5sums    = portage.digestParseFile(digestpath)
	
	if md5sums == None:
		portage.writemsg("Missing digest: %s\n" % mycpv)
		md5sums = {}

	for x in md5sums.keys():
		if x[0] == '/':
			del md5sums[x]

	#portage.writemsg("\n\ndigestpath: %s\n" % digestpath)
	#portage.writemsg("md5sums: %s\n" % md5sums)
	#portage.writemsg("newuri: %s\n" % newuri)

	bn_list = []
	for x in newuri:
		if not x:
			continue
		if (x in [")","(",":","||"]) or (x[-1] == "?"):
			# ignore it. :)
			continue
		x = cstrip(x,"()|?")
		if not x:
			continue

		mybn = os.path.basename(x)
		if mybn not in bn_list:
			bn_list += [mybn]
		else:
			continue
		
		if mybn not in md5sums:
			portage.util.writemsg("Missing md5sum: %s in %s\n" % (mybn, mycpv))
		else:
			if mybn in md5_list:
				if (md5_list[mybn]["MD5"]  != md5sums[mybn]["MD5"]) or \
				   (md5_list[mybn]["size"] != md5sums[mybn]["size"]):

					# This associates the md5 with each file. [md5/size]
					md5joins = md5_list[mybn][2].split(",")
					md5joins = (" ["+md5_list[mybn][0]+"/"+md5_list[mybn][1]+"],").join(md5joins)
					md5joins += " ["+md5_list[mybn][0]+"/"+md5_list[mybn][1]+"]"

					portage.writemsg("Colliding md5: %s of %s [%s/%s] and %s\n" % (mybn,mycpv,md5sums[mybn][0],md5sums[mybn][1],md5joins))
					col_list += [mybn]
				else:
					md5_list[mybn][2] += ","+mycpv
			else:
				md5_list[mybn] = md5sums[mybn]+[mycpv]
			del md5sums[mybn]
		
	#portage.writemsg(str(bn_list)+"\n")
	for x in md5sums:
		if x not in bn_list:
			portage.writemsg("Extra md5sum: %s in %s\n" % (x, mycpv))


print col_list
print
print str(len(md5_list))+" unique distfile md5s."
print str(len(bn_list))+" unique distfile names."
