#!/usr/bin/python3
#
#

import os
import json
import setuptools


def setup(hostdata, tempdir):
    for service, config in hostdata["services"].items():
        if service == "ldapserver":
            if (hostdata["os"] == "debian"):

                #hostdata["services"]["ldapserver"]["serverid"]

                setup = "#!/bin/bash\n"
                setup += setuptools.packages("net-tools vim less gnutls-bin slapd ldap-utils wget rsyslog")
                setup += setuptools.certificate("slapd")


                setup += f"""

## cleanup ##
/etc/init.d/slapd stop
killall -9 slapd 2>/dev/null
killall -9 /usr/sbin/slapd 2>/dev/null
mkdir -p /var/lib/ldap
rm -rf /etc/ldap/slapd.d/*
rm -rf /var/lib/ldap/*
cp /usr/share/doc/slapd/examples/DB_CONFIG /var/lib/ldap/

"""

                setup += f"""

BACKEND="mdb"

SERVER="{hostdata["hostname"]}"
LDAP_ADMIN_PASSWD_HASH="`slappasswd -s "{config["adminpass"]}"`"
LDAP_REPLICA_PASSWD_HASH="`slappasswd -s "{config["replicapass"]}"`"
SCHEMA_ADDONS="openssh-lpk ldapns mailinggroup mozillaOrgPerson samba sudo calentry calendar"

## generate some global Variables ##
SID="S-1-5-21-3994274829-143363983-1533393011"; #SID="`net getlocalsid`"
DESCR="`echo "{config["basedn"]}" | sed "s|,dc=|.|g" | sed "s|^dc=||g"`"
DESCR2="`echo "$DESCR" | cut -d"." -f1`"

"""

                for schema, data in config["schemas"].items():
                    setup += setuptools.file(f"/etc/ldap/schema/{schema}.schema", data)
                    setup += f"SCHEMA_ADDONS+=\" {schema}\"\n"


                sudo_schema = """
attributetype ( 1.3.6.1.4.1.15953.9.1.1
   NAME 'sudoUser'
   DESC 'User(s) who may  run sudo'
   EQUALITY caseExactIA5Match
   SUBSTR caseExactIA5SubstringsMatch
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.4.1.15953.9.1.2
   NAME 'sudoHost'
   DESC 'Host(s) who may run sudo'
   EQUALITY caseExactIA5Match
   SUBSTR caseExactIA5SubstringsMatch
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.4.1.15953.9.1.3
   NAME 'sudoCommand'
   DESC 'Command(s) to be executed by sudo'
   EQUALITY caseExactIA5Match
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.4.1.15953.9.1.4
   NAME 'sudoRunAs'
   DESC 'User(s) impersonated by sudo'
   EQUALITY caseExactIA5Match
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.4.1.15953.9.1.5
   NAME 'sudoOption'
   DESC 'Options(s) followed by sudo'
   EQUALITY caseExactIA5Match
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.4.1.15953.9.1.6
   NAME 'sudoRunAsUser'
   DESC 'User(s) impersonated by sudo'
   EQUALITY caseExactIA5Match
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.4.1.15953.9.1.7
   NAME 'sudoRunAsGroup'
   DESC 'Group(s) impersonated by sudo'
   EQUALITY caseExactIA5Match
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.4.1.15953.9.1.8
   NAME 'sudoNotBefore'
   DESC 'Start of time interval for which the entry is valid'
   EQUALITY generalizedTimeMatch
   ORDERING generalizedTimeOrderingMatch
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.24 )

attributetype ( 1.3.6.1.4.1.15953.9.1.9
   NAME 'sudoNotAfter'
   DESC 'End of time interval for which the entry is valid'
   EQUALITY generalizedTimeMatch
   ORDERING generalizedTimeOrderingMatch
   SYNTAX 1.3.6.1.4.1.1466.115.121.1.24 )

objectclass ( 1.3.6.1.4.1.15953.9.2.1 NAME 'sudoRole' SUP top STRUCTURAL
   DESC 'Sudoer Entries'
   MUST ( cn )
   MAY ( sudoUser $ sudoHost $ sudoCommand $ sudoRunAs $ sudoRunAsUser $
	 sudoRunAsGroup $ sudoOption $ sudoNotBefore $ sudoNotAfter $
	 description )
   )

"""
                setup += setuptools.file("/etc/ldap/schema/sudo.schema", sudo_schema)

                calendar_schema = """
# $Id: calresource.schema,v 1.2 2011/04/29 10:54:03 martin$
#
# DRAFT only at the time of writing this schema!
# See: http://tools.ietf.org/html/draft-cal-resource-schema-03
#
### 
#
# This specification defines a schema for representing resources to
# ease the discovery and scheduling of resources between any calendar
# client and server. 
# LDAP and vCard mappings of the schema are described in this
# document. The Object model chosen is the lowest common denominator
# to adapt for LDAP. 
#
# This schema depends on:
#       - calentry.schema
#
# New LDAP objectclasses and attributes defined in this document need
# to be registered by the Internet Assigned Numbers Authority (IANA) as
# requested in the following template.  Once the assignment is done,
# this document needs to be updated with the right OID numbers for all
# the newly defined objectclasses and attributes. 
#
# Temporary we replace "x" in OIDs with unused "5"
# Example: 1.3.6.1.1.x.1.1   with   1.3.6.1.1.5.1.1  


# Attribute Type Definitions

#
# ERROR in draft!
# Same OID for 2 attributetypes so I changed 'Kind'
# to ...0.0 instead of ...0.1
#

attributetype ( 1.3.6.1.1.5.0.0 NAME 'Kind'
	      DESC 'Kind of Object'
	      EQUALITY caseIgnoreMatch
	      SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
	      SINGLE-VALUE )

attributetype ( 1.3.6.1.1.5.0.1
               NAME 'VcardUid'
               DESC 'VCard UniqueID'
               EQUALITY caseExactMatch
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
               SINGLE-VALUE )

attributetype ( 1.3.6.1.1.5.0.2 NAME 'NickName'
               DESC 'Nick Name'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.3 NAME 'Categories'
               DESC 'Categories'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.4 NAME 'Restricted'
               DESC 'Access Restricted'
               EQUALITY booleanMatch
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.7 )

attributetype ( 1.3.6.1.1.5.0.5 NAME 'AdmittanceURL'
               DESC 'Cal Resource Admittance Info URL'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.6 NAME 'accessibilityURL'
               DESC 'Cal Resource accessibility Info URL'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.7 NAME 'Capacity'
               DESC 'Cal Resource Capacity'
               EQUALITY integerMatch
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 )

attributetype ( 1.3.6.1.1.5.0.8 NAME 'InventoryList'
               DESC 'Inventory List'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.9 NAME 'InventoryURL'
               DESC 'Cal Resource Inventory Info URL'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.10 NAME 'ResourceManager'
               DESC 'Cal Resource Manager Info'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.11 NAME 'TimeZoneID'
               DESC 'Cal Time Zone ID'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.12 NAME 'Multiplebookings'
               DESC 'Cal Num Bookings Allowed'
               EQUALITY integerMatch
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 )

attributetype ( 1.3.6.1.1.5.0.13 NAME 'MaxInstances'
               DESC 'Cal Maximum Instances allowed'
               EQUALITY integerMatch
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 )

attributetype ( 1.3.6.1.1.5.0.14 NAME 'BookingWindowStart'
               DESC 'Cal Booking Window Start'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.15 NAME 'BookingWindowEnd'
               DESC 'Cal Booking Window End'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.16 NAME 'Autoschedule'
               DESC 'Cal Scheduling no approval required'
               EQUALITY booleanMatch
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.7 )

attributetype ( 1.3.6.1.1.5.0.17 NAME 'ApprovalInfoURL'
               DESC 'Cal Sched Approval Info'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.18 NAME 'SchedAdmin'
               DESC 'Cal Sched Admin Info'
               EQUALITY caseIgnoreIA5Match
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.1.5.0.19 NAME 'Nocost'
               DESC 'Free or Priced resource'
               EQUALITY booleanMatch
               SYNTAX 1.3.6.1.4.1.1466.115.121.1.7 )

attributetype ( 1.3.6.1.1.5.0.20 NAME 'CostURL'
                 DESC 'Cal Resource Cost Info'
                 EQUALITY caseIgnoreIA5Match
                 SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

# Object Class Definitions


objectclass ( 1.3.6.1.1.5.1.1 NAME 'CalendarResource'
	    DESC 'Calendar Resource Object Class'   
            SUP calEntry  
            AUXILIARY   
            MUST (cn)   
            MAY ( kind $ nickname $ description $ ou $ categories $ 
                 member $ uniquemember $ accessibilityurl $ capacity $
                 owner $ resourcemanager $ timezoneid $ 
                 multiplebookings $ maxinstances $
                 bookingwindowstart $ bookingwindowend $ vcarduid ) )


objectclass ( 1.3.6.1.1.5.1.2 NAME 'AdmittanceInfo'
	    DESC 'Calendar Resource Admittance Info Class'
	    SUP CalendarResource
	    AUXILIARY
	    MAY ( admittanceurl ) )

objectclass ( 1.3.6.1.1.5.1.3 NAME 'InventoryInfo'
	    DESC 'Calendar Resource Inventory Info Class'
	    SUP CalendarResource
	    AUXILIARY
	    MAY ( inventorylist $ inventoryurl ) )

objectclass ( 1.3.6.1.1.5.1.4 NAME 'SchedApprovalInfo'
	    DESC 'Calendar Sched Approval Class'
	    SUP CalendarResource
	    AUXILIARY
	    MAY ( autoschedule $ approvalinfourl $ schedadmin ) )

objectclass ( 1.3.6.1.1.5.1.5 NAME 'CalendarResourceCost'
	    DESC 'Calendar Resource Cost Object Class'
	    SUP CalendarResource
	    AUXILIARY
	    MAY ( nocost $ costurl ) )
"""
                setup += setuptools.file("/etc/ldap/schema/calendar.schema", calendar_schema)

                calentry_schema = """
# RFC2739 calEntry schema for OpenLDAP 2.x 

# Version of RFC 2739 schema translated by Terrelle Shaw (xytek@xytek.org)
# Nov. 7, 2002
# Modifications by Peter Marschall <peter.marschall@adpm.de>
# Nov. 9, 2002
# 20060322 changes as in  http://www.openldap.org/lists/openldap-software/200211/msg00242.html

# Notes:
# * RFC2739 seems to be a bit sloppy about attribute type and
#   objectclass definitions syntax and also about attribute syntax
#   and matching rules.
#   (It even counts the attributes in the calEntry objectclass wrong ;-)
# * The following changes have been applied to correct the schema
#   - added description to each attributetype definition
#   - changed SYNTAX from 'String' to corresponding OID
#     to make matching rules and syntax consistent
#   - replaced illegal keyword SUBSTRING by SUBSTR
#   - changed SUBSTR from caseIgnoreMatch to caseIgnoreSubstringsMatch
#   - removed illegal keyword MULTI-VALUE
#   - added keyword SINGLE-VALUE where appropriate
#   - removed USAGE since cwuserApplications is the default 
#   - added description to the objectclass defintion
#   - corrected typo in objectclass definition
#   - added the attributetypes defined but not used to the objectclass


# 2.4.4.1 calCalURI
attributetype ( 1.2.840.113556.1.4.478 
        NAME 'calCalURI' 
        DESC 'URI to a snapshot of the users entire default calendar'
        EQUALITY caseIgnoreMatch 
        SUBSTR caseIgnoreSubstringsMatch 
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
        SINGLE-VALUE )

# 2.4.4.2 calFBURL
attributetype ( 1.2.840.113556.1.4.479
        NAME 'calFBURL'
        DESC 'URI to the users default free/busy time data'
        EQUALITY caseIgnoreMatch
        SUBSTR caseIgnoreSubstringsMatch
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
        SINGLE-VALUE )

# 2.4.4.3 calCAPURI
attributetype ( 1.2.840.113556.1.4.480
        NAME 'calCAPURI'
        DESC 'URI used to communicate with the users calendar'
        EQUALITY caseIgnoreMatch
        SUBSTR caseIgnoreSubstringsMatch
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
        SINGLE-VALUE )

# 2.4.4.4 calCalAdrURI
attributetype ( 1.2.840.113556.1.4.481
        NAME 'calCalAdrURI'
        DESC 'URI to which event requests should be sent for the user'
        EQUALITY caseIgnoreMatch
        SUBSTR caseIgnoreSubstringsMatch
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15
        SINGLE-VALUE )

# 2.4.4.5 calOtherCalURIs
attributetype ( 1.2.840.113556.1.4.482
        NAME 'calOtherCalURIs'
        DESC 'URIs to snapshots of non-default calendars belonging to the user'
        EQUALITY caseIgnoreMatch
        SUBSTR caseIgnoreSubstringsMatch
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 )

# 2.4.4.6 calOtherFBURLs
attributetype ( 1.2.840.113556.1.4.483
        NAME 'calOtherFBURLs'
        DESC 'URIs to non-default free/busy data belonging to the user'
        EQUALITY caseIgnoreMatch
        SUBSTR caseIgnoreSubstringsMatch
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 )

# 2.4.4.7 calOtherCAPURIs
attributetype ( 1.2.840.113556.1.4.484
        NAME 'calOtherCAPURIs'
        DESC 'URIs to non-default calendars belonging to the user'
        EQUALITY caseIgnoreMatch
        SUBSTR caseIgnoreSubstringsMatch
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 )

# 2.4.4.8 calOtherCalAdrURIs
attributetype ( 1.2.840.113556.1.4.485
        NAME 'calOtherCalAdrURIs'
        DESC 'URIs of destinations for event requests to non-default calendars'
        EQUALITY caseIgnoreMatch
        SUBSTR caseIgnoreSubstringsMatch
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 )

# 2.4.3.1 calEntry
objectclass ( 1.2.840.113556.1.5.87
        NAME 'calEntry'
        DESC 'Calendering and free/busy information'
        SUP top AUXILIARY
        MAY ( calCalURI $ calFBURL $ calCAPURI $ calCalAdrURI $
                calOtherCAPURIs $ calOtherCalURIs $ calOtherFBURLs $ 
                calOtherCalAdrURIs ) )

# EOF
"""
                setup += setuptools.file("/etc/ldap/schema/calentry.schema", calentry_schema)


                """
 echo "include: file:///etc/ldap/schema/$SCHEMA.ldif" >> /tmp/config.ldif
 echo "dn: cn=$SCHEMA,cn=schema,cn=config" > /etc/ldap/schema/$SCHEMA.ldif
 echo "objectClass: olcSchemaConfig" >> /etc/ldap/schema/$SCHEMA.ldif
 echo "cn: $SCHEMA" >> /etc/ldap/schema/$SCHEMA.ldif
 cat /etc/ldap/schema/$SCHEMA.schema | \\
  grep -v "^#" | sed "s|^\\([a-zA-Z]\\)|#\\1|g" | tr "\\t" " " |sed "s|^  *| |g" | tr -d "\\n" | tr "#" "\\n" | \\
  sed "s|^attributetype |olcAttributeTypes: |g" | \\
  sed "s|^objectclass |olcObjectClasses: |g" | \\
  grep -v "^$" \\
 >> /etc/ldap/schema/$SCHEMA.ldif
                """

                mailinggroup_schema = """
#
# LDAP Mailing-Group schema
# Author: Oliver Dippel <o.dippel@gmx.de>
# 

attributetype ( 1.3.6.1.4.1.12528.1.193 NAME 'mailingGroup'
	DESC 'mailingGroup'
        EQUALITY caseIgnoreMatch
        SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{32768} )

objectclass ( 1.3.6.1.4.1.12528.2.29 NAME 'mailingGroup'
	DESC 'mailingGroup'
        SUP top
        AUXILIARY
	MAY  mailingGroup  )

"""
                setup += setuptools.file("/etc/ldap/schema/mailinggroup.schema", mailinggroup_schema)


                openssh_lpk_schema = """
#
# LDAP Public Key Patch schema for use with openssh-ldappubkey
# Author: Eric AUGE <eau@phear.org>
#
# Based on the proposal of : Mark Ruijter
#

# octetString SYNTAX
attributetype ( 1.3.6.1.4.1.24552.500.1.1.1.13 NAME 'sshPublicKey'
	DESC 'OpenSSH Public key'
	EQUALITY octetStringMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.40 )

# printableString SYNTAX yes|no
objectclass ( 1.3.6.1.4.1.24552.500.1.1.2.0 NAME 'ldapPublicKey' SUP top AUXILIARY
	DESC 'OpenSSH LPK objectclass'
	MUST uid
	MAY sshPublicKey
	)

"""
                setup += setuptools.file("/etc/ldap/schema/openssh-lpk.schema", openssh_lpk_schema)


                ldapns_schema = """
# \$Id: ldapns.schema,v 1.3 2003/05/29 12:57:29 lukeh Exp \$

# LDAP Name Service Additional Schema

# http://www.iana.org/assignments/gssapi-service-names

attributetype ( 1.3.6.1.4.1.5322.17.2.1 NAME 'authorizedService'
	DESC 'IANA GSS-API authorized service name'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{256} )

objectclass ( 1.3.6.1.4.1.5322.17.1.1 NAME 'authorizedServiceObject'
	DESC 'Auxiliary object class for adding authorizedService attribute'
	SUP top
	AUXILIARY
	MAY authorizedService )

objectclass ( 1.3.6.1.4.1.5322.17.1.2 NAME 'hostObject'
	DESC 'Auxiliary object class for adding host attribute'
	SUP top
	AUXILIARY
	MAY host )

"""
                setup += setuptools.file("/etc/ldap/schema/ldapns.schema", ldapns_schema )


                samba_schema = """

attributetype ( 1.3.6.1.4.1.7165.2.1.24 NAME 'sambaLMPassword'
	DESC 'LanManager Password'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{32} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.25 NAME 'sambaNTPassword'
	DESC 'MD4 hash of the unicode password'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{32} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.26 NAME 'sambaAcctFlags'
	DESC 'Account Flags'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{16} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.27 NAME 'sambaPwdLastSet'
	DESC 'Timestamp of the last password update'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.28 NAME 'sambaPwdCanChange'
	DESC 'Timestamp of when the user is allowed to update the password'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.29 NAME 'sambaPwdMustChange'
	DESC 'Timestamp of when the password will expire'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.30 NAME 'sambaLogonTime'
	DESC 'Timestamp of last logon'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.31 NAME 'sambaLogoffTime'
	DESC 'Timestamp of last logoff'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.32 NAME 'sambaKickoffTime'
	DESC 'Timestamp of when the user will be logged off automatically'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.48 NAME 'sambaBadPasswordCount'
	DESC 'Bad password attempt count'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.49 NAME 'sambaBadPasswordTime'
	DESC 'Time of the last bad password attempt'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.55 NAME 'sambaLogonHours'
	DESC 'Logon Hours'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{42} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.33 NAME 'sambaHomeDrive'
	DESC 'Driver letter of home directory mapping'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{4} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.34 NAME 'sambaLogonScript'
	DESC 'Logon script path'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{255} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.35 NAME 'sambaProfilePath'
	DESC 'Roaming profile path'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{255} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.36 NAME 'sambaUserWorkstations'
	DESC 'List of user workstations the user is allowed to logon to'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{255} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.37 NAME 'sambaHomePath'
	DESC 'Home directory UNC path'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{128} )

attributetype ( 1.3.6.1.4.1.7165.2.1.38 NAME 'sambaDomainName'
	DESC 'Windows NT domain to which the user belongs'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{128} )

attributetype ( 1.3.6.1.4.1.7165.2.1.47 NAME 'sambaMungedDial'
	DESC 'Base64 encoded user parameter string'
	EQUALITY caseExactMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{1050} )

attributetype ( 1.3.6.1.4.1.7165.2.1.54 NAME 'sambaPasswordHistory'
	DESC 'Concatenated MD5 hashes of the salted NT passwords used on this account'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{32} )

attributetype ( 1.3.6.1.4.1.7165.2.1.20 NAME 'sambaSID'
	DESC 'Security ID'
	EQUALITY caseIgnoreIA5Match
	SUBSTR caseExactIA5SubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{64} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.23 NAME 'sambaPrimaryGroupSID'
	DESC 'Primary Group Security ID'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{64} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.51 NAME 'sambaSIDList'
	DESC 'Security ID List'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{64} )

attributetype ( 1.3.6.1.4.1.7165.2.1.19 NAME 'sambaGroupType'
	DESC 'NT Group Type'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.21 NAME 'sambaNextUserRid'
	DESC 'Next NT rid to give our for users'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.22 NAME 'sambaNextGroupRid'
	DESC 'Next NT rid to give out for groups'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.39 NAME 'sambaNextRid'
	DESC 'Next NT rid to give out for anything'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.40 NAME 'sambaAlgorithmicRidBase'
	DESC 'Base at which the samba RID generation algorithm should operate'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.41 NAME 'sambaShareName'
	DESC 'Share Name'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.42 NAME 'sambaOptionName'
	DESC 'Option Name'
	EQUALITY caseIgnoreMatch
	SUBSTR caseIgnoreSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{256} )

attributetype ( 1.3.6.1.4.1.7165.2.1.43 NAME 'sambaBoolOption'
	DESC 'A boolean option'
	EQUALITY booleanMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.7 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.44 NAME 'sambaIntegerOption'
	DESC 'An integer option'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.45 NAME 'sambaStringOption'
	DESC 'A string option'
	EQUALITY caseExactIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.46 NAME 'sambaStringListOption'
	DESC 'A string list option'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 )

attributetype ( 1.3.6.1.4.1.7165.2.1.53 NAME 'sambaTrustFlags'
	DESC 'Trust Password Flags'
	EQUALITY caseIgnoreIA5Match
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 )

attributetype ( 1.3.6.1.4.1.7165.2.1.58 NAME 'sambaMinPwdLength'
	DESC 'Minimal password length (default: 5)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.59 NAME 'sambaPwdHistoryLength'
	DESC 'Length of Password History Entries (default: 0 => off)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.60 NAME 'sambaLogonToChgPwd'
	DESC 'Force Users to logon for password change (default: 0 => off, 2 => on)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.61 NAME 'sambaMaxPwdAge'
	DESC 'Maximum password age, in seconds (default: -1 => never expire passwords)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.62 NAME 'sambaMinPwdAge'
	DESC 'Minimum password age, in seconds (default: 0 => allow immediate password change)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.63 NAME 'sambaLockoutDuration'
	DESC 'Lockout duration in minutes (default: 30, -1 => forever)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.64 NAME 'sambaLockoutObservationWindow'
	DESC 'Reset time after lockout in minutes (default: 30)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.65 NAME 'sambaLockoutThreshold'
	DESC 'Lockout users after bad logon attempts (default: 0 => off)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.66 NAME 'sambaForceLogoff'
	DESC 'Disconnect Users outside logon hours (default: -1 => off, 0 => on)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.67 NAME 'sambaRefuseMachinePwdChange'
	DESC 'Allow Machine Password changes (default: 0 => off)'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.68 NAME 'sambaClearTextPassword'
	DESC 'Clear text password (used for trusted domain passwords)'
	EQUALITY octetStringMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.40 )

attributetype ( 1.3.6.1.4.1.7165.2.1.69 NAME 'sambaPreviousClearTextPassword'
	DESC 'Previous clear text password (used for trusted domain passwords)'
	EQUALITY octetStringMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.40 )

attributetype ( 1.3.6.1.4.1.7165.2.1.70 NAME 'sambaTrustType'
	DESC 'Type of trust'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.71 NAME 'sambaTrustAttributes'
	DESC 'Trust attributes for a trusted domain'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.72 NAME 'sambaTrustDirection'
	DESC 'Direction of a trust'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.73 NAME 'sambaTrustPartner'
	DESC 'Fully qualified name of the domain with which a trust exists'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{128} )

attributetype ( 1.3.6.1.4.1.7165.2.1.74 NAME 'sambaFlatName'
	DESC 'NetBIOS name of a domain'
	EQUALITY caseIgnoreMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{128} )

attributetype ( 1.3.6.1.4.1.7165.2.1.75 NAME 'sambaTrustAuthOutgoing'
	DESC 'Authentication information for the outgoing portion of a trust'
	EQUALITY caseExactMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{1050} )

attributetype ( 1.3.6.1.4.1.7165.2.1.76 NAME 'sambaTrustAuthIncoming'
	DESC 'Authentication information for the incoming portion of a trust'
	EQUALITY caseExactMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{1050} )

attributetype ( 1.3.6.1.4.1.7165.2.1.77 NAME 'sambaSecurityIdentifier'
	DESC 'SID of a trusted domain'
	EQUALITY caseIgnoreIA5Match SUBSTR caseExactIA5SubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{64} SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.78 NAME 'sambaTrustForestTrustInfo'
	DESC 'Forest trust information for a trusted domain object'
	EQUALITY caseExactMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{1050} )

attributetype ( 1.3.6.1.4.1.7165.2.1.79 NAME 'sambaTrustPosixOffset'
	DESC 'POSIX offset of a trust'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.7165.2.1.80 NAME 'sambaSupportedEncryptionTypes'
	DESC 'Supported encryption types of a trust'
	EQUALITY integerMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.27 SINGLE-VALUE )

objectclass ( 1.3.6.1.4.1.7165.2.2.6 NAME 'sambaSamAccount' SUP top AUXILIARY
	DESC 'Samba 3.0 Auxilary SAM Account'
	MUST ( uid $ sambaSID )
	MAY  ( cn $ sambaLMPassword $ sambaNTPassword $ sambaPwdLastSet $
	       sambaLogonTime $ sambaLogoffTime $ sambaKickoffTime $
	       sambaPwdCanChange $ sambaPwdMustChange $ sambaAcctFlags $
               displayName $ sambaHomePath $ sambaHomeDrive $ sambaLogonScript $
	       sambaProfilePath $ description $ sambaUserWorkstations $
	       sambaPrimaryGroupSID $ sambaDomainName $ sambaMungedDial $
	       sambaBadPasswordCount $ sambaBadPasswordTime $
	       sambaPasswordHistory $ sambaLogonHours))

objectclass ( 1.3.6.1.4.1.7165.2.2.4 NAME 'sambaGroupMapping' SUP top AUXILIARY
	DESC 'Samba Group Mapping'
	MUST ( gidNumber $ sambaSID $ sambaGroupType )
	MAY  ( displayName $ description $ sambaSIDList ))

objectclass ( 1.3.6.1.4.1.7165.2.2.14 NAME 'sambaTrustPassword' SUP top STRUCTURAL
	DESC 'Samba Trust Password'
	MUST ( sambaDomainName $ sambaNTPassword $ sambaTrustFlags )
	MAY ( sambaSID $ sambaPwdLastSet ))

objectclass ( 1.3.6.1.4.1.7165.2.2.15 NAME 'sambaTrustedDomainPassword' SUP top STRUCTURAL
	DESC 'Samba Trusted Domain Password'
	MUST ( sambaDomainName $ sambaSID $
	       sambaClearTextPassword $ sambaPwdLastSet )
	MAY  ( sambaPreviousClearTextPassword ))

objectclass ( 1.3.6.1.4.1.7165.2.2.5 NAME 'sambaDomain' SUP top STRUCTURAL
	DESC 'Samba Domain Information'
	MUST ( sambaDomainName $ 
	       sambaSID ) 
	MAY ( sambaNextRid $ sambaNextGroupRid $ sambaNextUserRid $
	      sambaAlgorithmicRidBase $ 
	      sambaMinPwdLength $ sambaPwdHistoryLength $ sambaLogonToChgPwd $
	      sambaMaxPwdAge $ sambaMinPwdAge $
	      sambaLockoutDuration $ sambaLockoutObservationWindow $ sambaLockoutThreshold $
	      sambaForceLogoff $ sambaRefuseMachinePwdChange ))

objectclass ( 1.3.6.1.4.1.7165.2.2.7 NAME 'sambaUnixIdPool' SUP top AUXILIARY
        DESC 'Pool for allocating UNIX uids/gids'
        MUST ( uidNumber $ gidNumber ) )

objectclass ( 1.3.6.1.4.1.7165.2.2.8 NAME 'sambaIdmapEntry' SUP top AUXILIARY
        DESC 'Mapping from a SID to an ID'
        MUST ( sambaSID )
	MAY ( uidNumber $ gidNumber ) )

objectclass ( 1.3.6.1.4.1.7165.2.2.9 NAME 'sambaSidEntry' SUP top STRUCTURAL
	DESC 'Structural Class for a SID'
	MUST ( sambaSID ) )

objectclass ( 1.3.6.1.4.1.7165.2.2.10 NAME 'sambaConfig' SUP top AUXILIARY
	DESC 'Samba Configuration Section'
	MAY ( description ) )

objectclass ( 1.3.6.1.4.1.7165.2.2.11 NAME 'sambaShare' SUP top STRUCTURAL
	DESC 'Samba Share Section'
	MUST ( sambaShareName )
	MAY ( description ) )

objectclass ( 1.3.6.1.4.1.7165.2.2.12 NAME 'sambaConfigOption' SUP top STRUCTURAL
	DESC 'Samba Configuration Option'
	MUST ( sambaOptionName )
	MAY ( sambaBoolOption $ sambaIntegerOption $ sambaStringOption $ 
	      sambaStringListoption $ description ) )

objectclass ( 1.3.6.1.4.1.7165.2.2.16 NAME 'sambaTrustedDomain' SUP top STRUCTURAL
	DESC 'Samba Trusted Domain Object'
	MUST ( cn )
	MAY ( sambaTrustType $ sambaTrustAttributes $ sambaTrustDirection $
	      sambaTrustPartner $ sambaFlatName $ sambaTrustAuthOutgoing $
	      sambaTrustAuthIncoming $ sambaSecurityIdentifier $
	      sambaTrustForestTrustInfo $ sambaTrustPosixOffset $
	      sambaSupportedEncryptionTypes) )

"""
                setup += setuptools.file("/etc/ldap/schema/samba.schema", samba_schema )



                mozillaOrgPerson_schema = """
#
# mozillaOrgPerson schema v. 0.6
#

# req. core
# req. cosine
# req. inetorgperson

# attribute defs

attributetype ( 1.3.6.1.4.1.13769.2.1.1 
	NAME ( 'mozillaNickname' ) 
	SUP name )

attributetype ( 1.3.6.1.4.1.13769.2.1.2 
	NAME ( 'mozillaUseHtmlMail' ) 
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.7 
	SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.13769.2.1.3
	NAME 'mozillaSecondEmail' 
	EQUALITY caseIgnoreIA5Match
	SUBSTR caseIgnoreIA5SubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{256} )

attributetype ( 1.3.6.1.4.1.13769.2.1.4
	NAME 'mozillaHomeLocalityName' 
	EQUALITY caseIgnoreMatch
	SUBSTR caseIgnoreSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{128} )

attributetype ( 1.3.6.1.4.1.13769.2.1.5 
	NAME 'mozillaPostalAddress2'
	EQUALITY caseIgnoreListMatch
	SUBSTR caseIgnoreListSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.41 )

attributetype ( 1.3.6.1.4.1.13769.2.1.6 
	NAME 'mozillaHomePostalAddress2'
	EQUALITY caseIgnoreListMatch
	SUBSTR caseIgnoreListSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.41 )

attributetype ( 1.3.6.1.4.1.13769.2.1.7 
	NAME ( 'mozillaHomeState' ) SUP name )

attributetype ( 1.3.6.1.4.1.13769.2.1.8 
	NAME 'mozillaHomePostalCode'
	EQUALITY caseIgnoreMatch
	SUBSTR caseIgnoreSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15{40} )

attributetype ( 1.3.6.1.4.1.13769.2.1.9 
	NAME ( 'mozillaHomeCountryName' ) 
	SUP name SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.13769.2.1.10
	NAME ( 'mozillaHomeFriendlyCountryName' )
	EQUALITY caseIgnoreMatch
	SUBSTR caseIgnoreSubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 )

attributetype ( 1.3.6.1.4.1.13769.2.1.11
	NAME ( 'mozillaHomeUrl' )
	EQUALITY caseIgnoreIA5Match
	SUBSTR caseIgnoreIA5SubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{256} )

attributetype ( 1.3.6.1.4.1.13769.2.1.12
	NAME ( 'mozillaWorkUrl' )
	EQUALITY caseIgnoreIA5Match
	SUBSTR caseIgnoreIA5SubstringsMatch
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26{256} )

# un-comment for all LDAP server NOT supporting SYNTAX 2.16.840.1.113730.3.7.1
# attributetype ( 1.3.6.1.4.1.13769.2.1.13
#	NAME ( 'nsAIMid' )
#	DESC 'AOL Instant Messenger (AIM) Identity'
#	EQUALITY telephoneNumberMatch
#	SUBSTR telephoneNumberSubstringsMatch
#	SYNTAX 1.3.6.1.4.1.1466.115.121.1.50 )

# un-comment for Netscape 6.x and all other LDAP server supporting SYNTAX 2.16.840.1.113730.3.7.1
# attributeTypes ( 2.16.840.1.113730.3.1.2013
#	NAME ( 'nsAIMid' )
#	DESC 'AOL Instant Messenger (AIM) Identity'
#	SYNTAX 2.16.840.1.113730.3.7.1 )

attributetype ( 1.3.6.1.4.1.13769.2.1.96
	NAME ( 'mozillaCustom1' )
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26
	SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.13769.2.1.97
	NAME ( 'mozillaCustom2' )
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26
	SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.13769.2.1.98
	NAME ( 'mozillaCustom3' )
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26
	SINGLE-VALUE )

attributetype ( 1.3.6.1.4.1.13769.2.1.99
	NAME ( 'mozillaCustom4' )
	SYNTAX 1.3.6.1.4.1.1466.115.121.1.26
	SINGLE-VALUE )
 
# objectClass defs 

objectclass ( 1.3.6.1.4.1.13769.2.2.1 
	NAME 'mozillaOrgPerson' 
	SUP top 
	AUXILIARY 
	MAY ( 
	mozillaNickname $ 
	mozillaUseHtmlMail $ 
	mozillaSecondEmail $ 
	mozillaPostalAddress2 $ 
	mozillaHomePostalAddress2 $ 
	mozillaHomeLocalityName $ 
	mozillaHomeState $ 
	mozillaHomePostalCode $ 
	mozillaHomeCountryName $ 
	mozillaHomeFriendlyCountryName $ 
	mozillaHomeUrl $ 
	mozillaWorkUrl $ 
	mozillaCustom1 $ 
	mozillaCustom2 $ 
	mozillaCustom3 $ 
	mozillaCustom4 $ 
	c $ 
	co ) ) 
"""
                setup += setuptools.file("/etc/ldap/schema/mozillaOrgPerson.schema", mozillaOrgPerson_schema)


                syncRepls = ""
                peers = ""
                peer_n = 1
                for ip, peer in config["peers"].items():
                    setup += f"echo 'echo \"{ip} {peer[0]}\" >> /etc/hosts' >> /inits/01_hostsfile\n"
                    peers += f"olcServerID: {peer_n} {peer[1]}\n"
                    syncRepls += f"""olcSyncRepl: rid=00{peer_n}
  provider={peer[1]}
  bindmethod=simple
  binddn="cn=replica,{config["basedn"]}" credentials={config["replicapass"]}
  searchbase="{config["basedn"]}"
  logbase="{config["basedn"]}"
  logfilter="(&(objectClass=auditWriteObject)(reqResult=0))"
  schemachecking=on
  type=refreshAndPersist retry="60 +"
  syncdata=default
"""
                    peer_n += 1



                setup += f"""
## generate new LDAP-Config ##

cat <<EOF > /tmp/config.ldif
# Global config:
dn: cn=config
objectClass: olcGlobal
cn: config
{peers.strip()}
olcPidFile: /var/run/slapd/slapd.pid
olcArgsFile: /var/run/slapd/slapd.args
#olcLogLevel: 256
olcLogLevel: 127
olcToolThreads: 1
olcPasswordHash: {{CRYPT}}
olcPasswordCryptSaltFormat: \\$1$%.8s
olcTLSCACertificateFile: /etc/ssl/cacert.pem
olcTLSCertificateKeyFile: /etc/ssl/slapd_key.pem
olcTLSCertificateFile: /etc/ssl/slapd_cert.pem
#olcTLSCipherSuite: TLSv1+RSA:!EXPORT:!NULL
olcTLSVerifyClient: never
olcAllows: bind_v2

# Frontend settings
dn: olcDatabase={{-1}}frontend,cn=config
objectClass: olcDatabaseConfig
objectClass: olcFrontendConfig
olcDatabase: {{-1}}frontend
olcSizeLimit: 500
olcAccess: {{0}}to *
  by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage
  by * break
olcAccess: {{1}}to dn.exact=""
  by * read
olcAccess: {{2}}to dn.base="cn=Subschema"
  by * read

# Config db settings
dn: olcDatabase=config,cn=config
objectClass: olcDatabaseConfig
olcDatabase: config
olcAccess: to *
  by dn.exact=gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth manage
  by * break
olcRootDN: cn=admin,cn=config
olcRootPW: $LDAP_ADMIN_PASSWD_HASH

# Load schemas
dn: cn=schema,cn=config
objectClass: olcSchemaConfig
cn: schema

include: file:///etc/ldap/schema/core.ldif
include: file:///etc/ldap/schema/cosine.ldif
include: file:///etc/ldap/schema/nis.ldif
include: file:///etc/ldap/schema/inetorgperson.ldif

EOF


## convert schema-format to ldif-format and add it to the ldap-config ##

for SCHEMA in $SCHEMA_ADDONS
do
 echo "include: file:///etc/ldap/schema/$SCHEMA.ldif" >> /tmp/config.ldif
 echo "dn: cn=$SCHEMA,cn=schema,cn=config" > /etc/ldap/schema/$SCHEMA.ldif
 echo "objectClass: olcSchemaConfig" >> /etc/ldap/schema/$SCHEMA.ldif
 echo "cn: $SCHEMA" >> /etc/ldap/schema/$SCHEMA.ldif
 cat /etc/ldap/schema/$SCHEMA.schema | \\
  grep -v "^#" | sed "s|^\\([a-zA-Z]\\)|#\\1|g" | tr "\\t" " " |sed "s|^  *| |g" | tr -d "\\n" | tr "#" "\\n" | \\
  sed "s|^attributetype |olcAttributeTypes: |g" | \\
  sed "s|^objectclass |olcObjectClasses: |g" | \\
  grep -v "^$" \\
 >> /etc/ldap/schema/$SCHEMA.ldif
done

cat <<EOF >> /tmp/config.ldif
# Load module
dn: cn=module{0},cn=config
objectClass: olcModuleList
cn: module{0}
olcModulePath: /usr/lib/ldap
olcModuleLoad: back_$BACKEND
olcModuleLoad: syncprov

# Set defaults for the backend
dn: olcBackend=$BACKEND,cn=config
objectClass: olcBackendConfig
olcBackend: $BACKEND

# The database definition.
dn: olcDatabase=$BACKEND,cn=config
objectClass: olcDatabaseConfig
objectClass: olc${{BACKEND^}}Config
olcDatabase: $BACKEND
olcDbCheckpoint: 512 30
#olcDbConfig: set_cachesize 0 2097152 0
#olcDbConfig: set_lk_max_objects 1500
#olcDbConfig: set_lk_max_locks 1500
#olcDbConfig: set_lk_max_lockers 1500
olcLastMod: TRUE
olcSuffix: {config["basedn"]}
olcDbDirectory: /var/lib/ldap
olcRootDN: cn=admin,{config["basedn"]}
olcRootPW: $LDAP_ADMIN_PASSWD_HASH
olcDbIndex: objectClass eq
olcDbIndex: entryUUID eq
olcDbIndex: entryCSN eq
olcAccess: to attrs=userPassword,shadowLastChange
  by self write
  by anonymous auth
  by dn="cn=admin,{config["basedn"]}" write
  by dn="cn=replica,{config["basedn"]}" read
  by * none
olcAccess: to dn.base=""
  by * read
olcAccess: to *
  by self write
  by dn="cn=admin,{config["basedn"]}" write
  by dn="cn=replica,{config["basedn"]}" read
  by * read
olcMirrorMode: TRUE
{syncRepls}

dn: olcOverlay=syncprov,olcDatabase={{1}}$BACKEND,cn=config
objectClass: olcSyncProvConfig
objectClass: olcOverlayConfig
olcOverlay: syncprov

EOF
"""

                setup += """
echo "## import the new LDAP-Config ... ##"
rm -rf /etc/ldap/slapd.d/*
slapadd -F /etc/ldap/slapd.d/ -b "cn=config" -l /tmp/config.ldif
echo "## import the new LDAP-Config .....done ##"

"""

                basedata = f"""
dn: {config["basedn"]}
objectClass: top
objectClass: dcObject
objectClass: organization
o: $DESCR
dc: $DESCR2

dn: cn=admin,{config["basedn"]}
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: admin
description: LDAP administrator
userPassword: $LDAP_ADMIN_PASSWD_HASH

dn: cn=replica,{config["basedn"]}
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: replica
description: LDAP replicator
userPassword: $LDAP_REPLICA_PASSWD_HASH

"""
                setup += setuptools.file("/tmp/basedata.ldif", basedata)
                setup += "echo \"## import the Basedata ... ##\"\n"
                setup += "slapadd < /tmp/basedata.ldif\n"
                setup += "echo \"## import the Basedata .....done ##\"\n"

                userdata = config.get("userdata")
                if userdata:
                    setup += setuptools.file("/tmp/ldap-data.ldif", userdata)
                    #setup += """cat /tmp/ldap-data.ldif | grep -v "^KIND:\\|^MULTIPLEBOOKINGS:\\|^objectClass: CalendarResource$\\|^objectClass: calEntry$\\|^mail: projects-\\|^mail: jobs-\\|^mail: departments-\\|^mail: roles-\\|^mail: all-" > /tmp/ldapdata.ldif\n"""
                    setup += "echo \"## import the Userdata ... ##\"\n"
                    setup += "slapadd < /tmp/ldap-data.ldif\n"
                    setup += "echo \"## import the Userdata .....done ##\"\n"


                slapd = f"""
SLAPD_CONF=
SLAPD_USER="openldap"
SLAPD_GROUP="openldap"
SLAPD_PIDFILE=
SLAPD_SERVICES="ldap:/// ldapi:/// ldaps:///"
SLAPD_SENTINEL_FILE=/etc/ldap/noslapd
SLAPD_OPTIONS=""
"""

                setup += "chown openldap:openldap -R /etc/ldap/slapd.d/\n"
                setup += "chown openldap:openldap -R /var/lib/ldap/\n"

                setuptools.file("/etc/default/slapd", slapd)
                setup += "mkdir -p /etc/ldap\n"
                setup += setuptools.autostart("rsyslog", "/etc/init.d/rsyslog start", "10")
                setup += setuptools.autostart("slapd", "/etc/init.d/slapd start", "60")


                with open(tempdir + "/ldapserver.sh", "w") as ofile:
                    ofile.write(setup)
                return tempdir + "/ldapserver.sh"
    return ""


