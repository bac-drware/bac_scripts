#!/usr/bin/env python

import os, sys
cmd_folder = os.path.dirname(os.path.abspath('./src/gdata'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

cmd_folder = os.path.dirname(os.path.abspath('./src/atom'))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import pprint
import gdata.apps.emailsettings.client
import gdata.apps.emailsettings.data
import gdata.apps.service
import xml.dom.minidom
import atom.core
import atom.data
import gdata.acl.data
import gdata.data
import gdata.apps
import gdata.apps_property
import gdata.apps.groups.client

#Safety switch
#To get this to actually make changes, set this to True and un-comment-out the client.CreateSendAs lines and comment-out the "raise" lines
commit_changes_to_google=False 

#Admin Credentials
#TODO - read these from a file
admin_email_text_file = open("admin_email.text", "r")
admin_email = admin_email_text_file.read()
admin_email_text_file.close()

admin_password_text_file = open("admin_password.text", "r")
admin_password = admin_password_text_file.read()
admin_password_text_file.close()

#Name of the group of users to change
alumni_group='all-alumni-list@abbey.bac.edu'

client = gdata.apps.emailsettings.client.EmailSettingsClient(domain='abbey.bac.edu')
client.ClientLogin(email=admin_email, password=admin_password, source='AlumniGroupEmailScript')
groupClient = gdata.apps.groups.client.GroupsProvisioningClient(domain='abbey.bac.edu')
groupClient.ClientLogin(email=admin_email, password=admin_password, source='AlumniGroupEmailScript')
alumniGroup = groupClient.RetrieveAllMembers(alumni_group)
service = gdata.apps.service.AppsService(email=admin_email, password=admin_password, domain='abbey.bac.edu')
service.ProgrammaticLogin()

#print alumniGroup.ToString()
xmlGroupEntry = xml.dom.minidom.parseString(alumniGroup.ToString())

#print xmlEntry.toprettyxml()

for ourParentNode in xmlGroupEntry.childNodes[0].childNodes:
	for propNode in ourParentNode.childNodes:
		if (propNode.nodeName.find("property") > -1):
			#print node
			for (propPropertyName, propPropertyValue) in propNode.attributes.items():
				#print "User's name is -- %s %s" % (propPropertyName, propPropertyValue)
				if (propPropertyValue=="memberId"):
					for (propPropertyName2, propPropertyValue2) in propNode.attributes.items():
						if (propPropertyName2=="value"):
							print 'Checking User "%s"' % propPropertyValue2
							useremail=propPropertyValue2

							if len(useremail) > 0:
								user = useremail.replace('@abbey.bac.edu','')
								try:
									print "Getting addresses for user %s" % user
									userEmailAddresses=client.RetrieveSendAs(username=useremail)
									if (len(userEmailAddresses.entry) > 0):
										print "user '%s' has the following aliases:" % user
						
										ourEntry= userEmailAddresses.entry[0]
						
										xmlEntry = xml.dom.minidom.parseString(ourEntry.ToString())
						
										user_full_name=""
										isDefault=""

										for node in xmlEntry.childNodes[0].childNodes:
											aliasAddress=""

											if (node.nodeName.find("property") > -1):
												name=""
												value=""
												for (propertyName, propertyValue) in node.attributes.items():
													if (propertyName=="name"):
														name=propertyValue
													if (propertyName=="value"):
														value=propertyValue
														#print 'Attr -- %s="%s"' % (name, value)
														
														if ((name=="name") and (value != "")):
															print 'User full name is "%s"' % value
															user_full_name=value
														
														if ((name=="address") and (value != "")):
															print 'Alias address is "%s"' % value
															aliasAddress=value

														if ((name=="isDefault") and (value != "")):
															print 'Alias Default is "%s"' % value
															isDefault=value

										if (user_full_name==""):
											print "user '%s' has no full name set" % user
										elif useremail.endswith('@alumni.bac.edu'):
											print "user '%s' already has an alumni email address '%s'" % (user, useremail)
										else:
											if (isDefault=="true"):
												user_new_email=useremail.replace('@abbey.bac.edu','@alumni.bac.edu')
												if (commit_changes_to_google==True):
													print "Creating Alias for user %s full name '%s' address %s" % (user, user_full_name, user_new_email)
													raise "This is supposed to be a dry run"
													#client.CreateSendAs(username=user, name=user_full_name, address=user_new_email, make_default=True)
												else:
													print "Would be Creating Alias for user %s full name '%s' address %s" % (user, user_full_name, user_new_email)


						
									else:
										print "user '%s' has no alias set" % user
										user_entry=service.RetrieveUser(user)
										#user_entry=service.RetrieveAllUsers()
						
										#print user_entry.ToString()
						
										if (len(user_entry.ToString()) > 0):
											print "user '%s' has the following name:" % user
						
											xmlEntry = xml.dom.minidom.parseString(user_entry.ToString())
						
											#print xmlEntry.toprettyxml()
						
											for node in xmlEntry.childNodes[0].childNodes:
												#print "node is %s" % node
												if (node.nodeName.find("name") > -1):
													lastName=""
													firstName=""
													for (propertyName, propertyValue) in node.attributes.items():
														if (propertyName=="familyName"):
															lastName=propertyValue
														if (propertyName=="givenName"):
															firstName=propertyValue
													user_full_name="%s %s" % (firstName, lastName)
													user_new_email="%s@alumni.bac.edu" % user
													print "User's name is -- %s" % user_full_name

													if (commit_changes_to_google==True):
														print "Creating Alias for user %s full name '%s' address %s" % (user, user_full_name, user_new_email)
														raise "This is supposed to be a dry run"
														#client.CreateSendAs(username=user, name=user_full_name, address=user_new_email, make_default=True)
													else:
														print "Would be Creating Alias for user %s full name '%s' address %s" % (user, user_full_name, user_new_email)
								
								except gdata.client.RequestError:
									print "Could not retrieve info for user: %s" % user
								except:
									print "Unexpected error:", sys.exc_info()[0]
									raise
								print "##############################"
