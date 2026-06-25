def sendEmailNotifications(body, subject, chkShtInfo):

#	body = "Hello, this is an email."
#	recipients = ["jason.coope@kanoa.ai"]
#	eSubject = "Here is the email!"

	efrom = "help@kanoa.ai"
	import java.lang
	
	retVal = 0
	msgs = []

	for row in system.kanoa.quality.sheet.getAlertGroups(chkShtInfo['chkShtId']):
		for alertGroup in system.kanoa.utilities.convertDatasetToJSON(system.kanoa.quality.config.getAlertGroups({'alertGroupName': row['alertGroupName']})):
			recipients = alertGroup['emailList'].split(",")
			try:
				system.net.sendEmail(smtpProfile='emailServer', fromAddr=efrom, subject=subject, body=body, to=recipients)
				retVal += 1
			except java.lang.Exception, e:
				msgs.append("%s - %s"%(recipients, e.cause))
	
	msg = None if len(msgs) == 0 else "\n".join(msgs)
	
	return retVal, msg