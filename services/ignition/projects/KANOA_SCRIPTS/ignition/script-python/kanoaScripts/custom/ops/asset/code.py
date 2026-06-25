def stateChange(paramsDict, userId):
	'''
		This function can be called whenever an assets state changes and can be customized however needed. In this example
		we are assumng a cell on a line has changed state and the cells under the line drive the line state
		Args:
			paramsDict (dict)
			 - assetInfo (dict)
		Returns:
			None
		Updated:
			jfc - 2/5/25 7:30am Created
	'''

	log = system.util.getLogger("kanoaScripts")
	debug = system.tag.read("[Kanoa]kanoa/debug/tags/debugStates").value
	if debug: log.info("stateChange() called by %s with %s"%(userId, paramsDict))	
	assetInfo = paramsDict['assetInfo'] if paramsDict.has_key('assetInfo') else None
	assetPath = assetInfo['assetPath'] if assetInfo.has_key('assetPath') else None
	
	if assetPath:
		#Now we'll check if we need to update the line
		parentPath = "\\".join(assetPath.split("\\")[:-1])
		assets = system.kanoa.utilities.convertDatasetToJSON(system.kanoa.asset.getAssets({'assetPath': parentPath + '\\%'}))
		tagPathList = [asset['tagPath'] + '/Line/OEE/StateTypeName' for asset in assets]
		tagPathValues = system.tag.readBlocking(tagPathList)
		assetStateTypeList = list(set([tagValue.value for tagValue in tagPathValues]))
	
		tagPathList = [asset['tagPath'] + '/Line/OEE/StateName' for asset in assets]
		tagPathValues = system.tag.readBlocking(tagPathList)
		assetStateList = list(set([tagValue.value for tagValue in tagPathValues]))
	
		if 'Running' in assetStateTypeList: parentState = 'Running'
		elif 'Unplanned Downtime' in assetStateTypeList:
			if 'Idle' in assetStateList: assetStateList.pop(assetStateList.index('Idle'))
			if 'Off Line' in assetStateList: assetStateList.pop(assetStateList.index('Off Line'))
			parentState = 'Idle' if len(assetStateList) == 0 else 'Down'
		elif 'Planned Downtime' in assetStateTypeList: parentState = 'Planned Down'
		else: parentState = 'Idle'
	
		parentTagPath = system.kanoa.asset.getAssetTagPath({'assetPath': parentPath})
		currentStateName = system.tag.read(parentTagPath + '/Line/OEE/stateName').value
		
		if currentStateName != parentState:
			log.info("Setting %s to state %s"%(parentPath, parentState))
			
			assetStateInfo = system.kanoa.utilities.convertDatasetRowToJSON(system.kanoa.asset.getAssetStates({'assetId': assetInfo['parentId'], 'stateName': parentState}),0)
			if assetStateInfo['stateCode']:
				stateInfo = {'assetId': assetInfo['parentId'], 'assetStateId': assetInfo['parentId'], 'stateCode': assetStateInfo['stateCode'], 'tStamp': system.date.now(), 'note': None}
				log.info("addStateEvent() called with %s"%stateInfo)
				stateEventId = system.kanoa.event.addStateEvent(stateInfo, userId)
				
				#We'll update the OEE state values for display purposes
				tagPath = '%s%s'%(parentTagPath, '/Line/OEE/')		
				tagPathList = [tagPath+'stateName', tagPath+'stateTypeName', tagPath+'stateTypeColor', tagPath+'stateColor', tagPath+'stateIconPath']
				tagPathValues = [assetStateInfo['stateName'], assetStateInfo['stateTypeName'] or '', assetStateInfo['stateTypeColor'] or '', assetStateInfo['stateColor'] or assetStateInfo['stateTypeColor'] or '', assetStateInfo['iconPath'] or '']
				system.tag.writeBlocking(tagPathList, tagPathValues)
			else:
				log.warn("Couldn't find a stateCode for assetId %s %s"%(values['parentId'], parentState))
	
	return