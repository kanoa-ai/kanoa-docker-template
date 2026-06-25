##################################################################################
def getCalculators(value=None):

	calcList = [
				{
					'label': 'Parse QR Code', 
					'value': 'Parse QR Code', 
					'func': kanoaScripts.custom.quality.calculators.parseQRCode, 
					'description': 'Returns the string prior to # in the passed string'
				}
				,{
					'label': 'Left Four Chars', 
					'value': 'Left Four Chars', 
					'func': kanoaScripts.custom.quality.calculators.leftFourChars, 
					'description': 'Returns the left four characters'
				},
				{
					'label': 'Get Line', 
					'value': 'Get Line', 
					'func': kanoaScripts.custom.quality.calculators.getLine, 
					'description': 'Returns the line'
				},
				{
					'label': 'Get Cell', 
					'value': 'Get Cell', 
					'func': kanoaScripts.custom.quality.calculators.getCell, 
					'description': 'Returns the Cell'
				},					
				]				
			
	if value is not None: return [element for element in calcList if element['value'] == value]
	return calcList
################################################################################## 
def executeCalculator(func, *args):

	#This function is used to lookup the actual function from the passed function name

	calcList = getCalculators(value=func)
	if len(calcList) == 0: return False
	
	func_dict = {calcList[0]['value']: calcList[0]['func']}
	return func_dict.get(func)(*args)
##################################################################################
##################################################################################
#	PLACE CUSTOM SCRIPTS BELOW THIS LINE AND ADD AN ENTRY IN THE getCalculators() function
##################################################################################
##################################################################################
def parseQRCode(paramsDict):
	
	log = system.util.getLogger('kanoa_quality')
	
	log.info("parseQRCode() called with %s"%paramsDict)
	
	import java.lang
	try:
		value = str(paramsDict['measurements']['1'])
		return str(value[:value.find('#')]), None
	except java.lang.Exception, e:
		log.error("parseQRCode() called with %s returned %s"%(paramsDict, e.cause))
		return '', e.cause
	except:
		return '', 'parseQRCode() threw script error'
##################################################################################
def leftFourChars(paramsDict):
	
	log = system.util.getLogger('kanoa_quality')
	
	log.info("leftFourChars() called with %s"%paramsDict)
	
	import java.lang
	try:
		value = str(paramsDict['measurements']['1'])
		return str(value)[:4], None
	except java.lang.Exception, e:
		log.error("leftFourChars() called with %s returned %s"%(paramsDict, e.cause))
		return '', e.cause
	except:
		return '', 'leftFourChars() threw script error'
##################################################################################
def getLine(paramsDict):
	"""
		This is very much coded for a check on the cell of a line
		Args:
			paramsDict (dict)
			 - ckShtInfo (dict)
			  - assetPath (string)
			  - measurements (dict)
		Returns:
			value (string)
			message (string): None if success
		Updated:
			jfc - 11/13/24: Created
	"""
	
	log = system.util.getLogger('kanoa_quality')
	log.info("getLine() called with %s"%paramsDict)

	import java.lang
	
	try:
		assetId = paramsDict['chkShtInfo']['assetId']
		if assetId is None: return '', 'No asset associated with this check sheet'
		assetPath = system.kanoa.utilities.getFieldValue('assetPath', system.kanoa.asset.getAssets({'assetId': assetId}))
		s = str(assetPath).rstrip('\\') 	# Handle trailing "\" so you don't return '' as the last segment
		if not s: return '', 'assetPath is empty'	
		return s.split('\\')[-2], None	
	except KeyError as e:
		log.warn("getLine(): missing key: %r in paramsDict=%r" % (e, paramsDict))
		return '', 'missing key: %s' % e	
	except (TypeError, AttributeError) as e:
		log.warn("getLine(): bad structure/types paramsDict=%r err=%r" % (paramsDict, e))
		return '', 'bad params structure'	
	except IndexError as e:
		log.warn("getLine(): could not parse assetPath from paramsDict=%r err=%r" % (paramsDict, e))
		return '', 'assetPath parse error'	
	except java.lang.Exception as e:
		log.exception("getLine(): Java exception paramsDict=%r" % (paramsDict,))
		cause = e.getCause()
		return '', str(cause if cause is not None else e)	
	except Exception as e:
		log.exception("getLine(): Python exception paramsDict=%r" % (paramsDict,))
		return '', str(e)
##################################################################################
def getCell(paramsDict):
	"""
		This is very much coded for a check on the cell of a line
		Args:
			paramsDict (dict)
			 - ckShtInfo (dict)
			  - assetPath (string)
			  - measurements (dict)
		Returns:
			value (string)
			message (string): None if success
		Updated:
			jfc - 11/13/24: Created
	"""
	
	log = system.util.getLogger('kanoa_quality')
	log.info("getCell() called with %s"%paramsDict)

	import java.lang
	
	try:
		assetId = paramsDict['chkShtInfo']['assetId']
		if assetId is None: return '', 'No asset associated with this check sheet'
		assetPath = system.kanoa.utilities.getFieldValue('assetPath', system.kanoa.asset.getAssets({'assetId': assetId}))
		s = str(assetPath).rstrip('\\') 	# Handle trailing "\" so you don't return '' as the last segment
		if not s: return '', 'assetPath is empty'	
		return s.split('\\')[-1], None	
	except KeyError as e:
		log.warn("getCell(): missing key: %r in paramsDict=%r" % (e, paramsDict))
		return '', 'missing key: %s' % e	
	except (TypeError, AttributeError) as e:
		log.warn("getLine(): bad structure/types paramsDict=%r err=%r" % (paramsDict, e))
		return '', 'bad params structure'	
	except IndexError as e:
		log.warn("getCell(): could not parse assetPath from paramsDict=%r err=%r" % (paramsDict, e))
		return '', 'assetPath parse error'	
	except java.lang.Exception as e:
		log.exception("getCell(): Java exception paramsDict=%r" % (paramsDict,))
		cause = e.getCause()
		return '', str(cause if cause is not None else e)	
	except Exception as e:
		log.exception("getCell(): Python exception paramsDict=%r" % (paramsDict,))
		return '', str(e)
##################################################################################	
def getHistoricalTimeStamp(timeStamp, tagPath):
	"""
		Stub for custom implementation to grab the process timestamp for a tag based on the timeStamp and tagPath passed in
		Args:
			timestamp (datetime): i.e. 'codeTime'
			tagPath (string)
		Returns:
			assetTime (datetime)
		Updated:
			jfc - 11/13/24: Created
	"""
	
	log = system.util.getLogger("kanoa_quality")	
	tagProvider = system.kanoa.config.getTagProvider('kanoaCore')
	debug = system.tag.read(tagProvider + 'kanoa/debug/tags/debugQualityChecks').value
	if debug: log.info("getHistoricalTimeStamp() called with %s %s"%(timeStamp, tagPath))	
	
	column = ['codeTime']
	aggregationMode = 'LastValue' 
	startTime = system.date.addMinutes(timeStamp, -30)
	
	dataset = system.dataset.toPyDataSet(system.tag.queryTagHistory(paths=[tagPath], startDate=timeStamp, rangeMinutes=15, columnNames=column, returnFormat='Wide'))

	for row in dataset:
		assetTime = row[0] 
		histCodeTime = row[1]
		if codeTime <= histCodeTime: return assetTime
	
	return timeStamp