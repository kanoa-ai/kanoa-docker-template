def getProductionOrders(paramsDict):
	'''
		stub to place custom ERP implementation
	'''	
		
	return 0
#################################################################################
def checkItemClassPath(itemClassPath):
	
	log = system.util.getLogger('kanoa_ERP_IF')
	log.info("Checking itemClassPath %s"%itemClassPath)
	
	userId = system.kanoa.security.getIDPUserId({'userName': 'SYSTEM'})		
	itemClassId = system.kanoa.utilities.getFieldValue('itemClassId', system.kanoa.item.getItemClasses({'itemClassPath': itemClassPath}))

	if itemClassId is None:
		itemClassNameList = itemClassPath.split('\\')
		parentId = None

		for i, itemClassName in enumerate(itemClassNameList):
			parentClassPath = '\\'.join(itemClassNameList[:i])
			itemClassPath = '\\'.join(itemClassNameList[:i+1])
			log.info('looking for itemClassPath %s'%itemClassPath)
			parentId = system.kanoa.utilities.getFieldValue('itemClassId', system.kanoa.item.getItemClasses({'itemClassPath': parentClassPath}))
			itemClassId = system.kanoa.utilities.getFieldValue('itemClassId', system.kanoa.item.getItemClasses({'itemClassPath': itemClassPath}))
			if itemClassId is None:
				log.info('addItemClass() called with %s'%{'itemClassName': itemClassName, 'parentId': parentId, 'itemClassDescription': None, 'itemClassColor': None, 'enabled': True})
				parentId = system.kanoa.item.addItemClass({'itemClassName': itemClassName, 'parentId': parentId, 'itemClassDescription': None, 'itemClassColor': None, 'enabled': True}, userId)

	return system.kanoa.utilities.getFieldValue('itemClassId', system.kanoa.item.getItemClasses({'itemClassPath': itemClassPath}))
#################################################################################
def sendMO(req_body):
	
	log = system.util.getLogger('kanoa_ERP_IF')
	log.info('Received sendMO() POST with %s'%(req_body))
	
	import java.lang
	
	try:
		req_body = system.util.jsonDecode(req_body)
	except:
		pass

	userId = system.kanoa.security.getIDPUserId({'userName': 'SYSTEM'})
	
#	req_body = {
#					'orderType': 'PRODUCTION', 
#					'notes': '',
#					'updatedBy': '', 
#					'scheduleInfo': {
#										'rateInfo': {
#														'period': 'hour', 
#														'equipmentRate': 0, 
#														'budgetRate': 0.0
#													}, 
#										'assetName': '601 - LINE2 ', 
#										'startDate': 20250419
#									}, 
#					'dueDate': 20250419, 
#					'lotNumber': '209110047 ', 
#					'itemName': '104439', 
#					'uom': 'CAS', 
#					'itemClassPath': '', 
#					'createdBy': 'LOGISTICS ', 
#					'orderQty': 720.0, 
#					'manufacturingOrder': '0100013419', 
#					'itemDescription': 'APPLE JUICE KS NFC TAI 3/2/128 OZ ', 
#					'status': 20 #20 = Released, anything 80 and above is 'Closed', 40 - 'checking for components', 50, 60 - 'Order Started'. Just ignore 40,50 and 60 
#				}

	try:
		woName = req_body['manufacturingOrder']
		reqdQty = req_body['orderQty']
		dueDate = system.date.parse(req_body['dueDate'], 'yyyyMMdd') if req_body['dueDate'] else None
		woStatus = req_body['status']
		woInfo = system.kanoa.utilities.convertDatasetRowToJSON(system.kanoa.order.getProductionOrders({'workOrderName': woName}),0)
		
		if woStatus >= 80: #anything 80 and above is 'Closed'
			if woInfo['workOrderId']:
				workOrderStatusId = system.kanoa.utilities.getFieldValue('workOrderStatusId', system.kanoa.order.getProductionOrderStates({'workOrderStatusName':'Closed'}))
				system.kanoa.order.updateProductionOrderField( woInfo['workOrderId'], 'workOrderStatusId', workOrderStatusId, userId)
				log.warn('Production order has been closed')
				scheduleEvents = system.kanoa.utilities.convertDatasetToJSON(system.kanoa.schedule.getScheduleBlocks({'workOrderId': woInfo['workOrderId']}))
				for scheduleEvent in scheduleEvents:
					if scheduleEvent['startDate'] >= system.date.now():
						log.warn("Deleting scheduled event %s"%scheduleEvent)
						system.kanoa.schedule.deleteScheduleBlock(scheduleEvent['scheduleBlockId'], userId)
				
				return True, 'Order closed'
			else:
				log.warn('No production order found to close')
				return False, 'No Order found to close'
		elif woStatus != 20: 
			log.info('Production order status is %s. Ignoring'%(woStatus))
			return True, 'Order ignored due to status'
		
		try:
			targetStart = system.date.parse(req_body['scheduleInfo']['startDate'], 'yyyyMMdd')		
			targetStartTime = req_body['scheduleInfo']['startTime']	#This is an int value in military time i.e 859
			hr = targetStartTime / 100
			minute = targetStartTime - (hr * 100)
			targetStart = system.date.setTime(targetStart, hr, minute, 0)
		except java.lang.Exception, e:
			log.warn("Error creating targetStartDate. %s"%e.cause)
		
		budgetRate = req_body['scheduleInfo']['rateInfo']['budgetRate']
		ratePeriod = req_body['scheduleInfo']['rateInfo']['period'].title()	#will always be in hours

		try:
			scheduleRateMins = budgetRate / 60.0 if ratePeriod == 'Hour' else budgetRate
			durationMins = int(reqdQty / (scheduleRateMins or 1.0))	#Need to calculate endDate based on budget Rate			
			targetEnd = system.date.addMinutes(targetStart, durationMins)
			log.info("Setting targetEnd to %s based on budgetRate"%targetEnd)
		except:
			targetEnd = system.date.addHours(targetStart, 6)
			log.warn("Setting targetEnd to default 6 hours %s"%targetEnd)
		
		notes = req_body['notes'] if req_body.has_key('notes') else None
	
		#look to see if we can find the asset that this MO is referring to
		machineName = req_body['scheduleInfo']['assetName'].strip()		
		assetAttributes = system.kanoa.utilities.convertDatasetToJSON(system.kanoa.asset.getAssetAttributes({}))
		attrInfo = {item['assetAttrValue']: item['assetId'] for item in assetAttributes if item['assetAttrName'] == 'erpName'}
		assetId = attrInfo[machineName] if attrInfo.has_key(machineName) else None
		if assetId: log.info("Found assetId %s for %s"%(assetId, machineName))
		else: log.warn("No assetId found for %s. This workOrder will not be scheduled"%(machineName))

		#Look to see if the unit of measure exists in MES
		uom = req_body['uom'].lower() if req_body.has_key('uom') and req_body['uom'] is not None else 'units'
		itemUnitId = system.kanoa.utilities.getFieldValue('itemUnitId', system.kanoa.item.getItemUnits({'itemUnitName': uom}))
		if itemUnitId is None: itemUnitId = system.kanoa.item.addItemUnit(uom, userId)
	
		#Check to see what type of Order this is. Generally we would expect it to be 'Production', but it is posible to create 'EXPERIMENT' or other type of orders
		modeName = req_body['orderType']	
		workOrderSourceId = system.kanoa.utilities.getFieldValue('workOrderSourceId', system.kanoa.order.getProductionOrderSource({'workOrderSourceName': 'M3'}))				
		modeId = system.kanoa.utilities.getFieldValue('modeId', system.kanoa.asset.getModes({'modeName': modeName}))
		if modeId is None: modeId = system.kanoa.utilities.getFieldValue('modeId', system.kanoa.getModes({'assetId': assetId, 'modeName': 'Production'}))
		
		woStates = system.kanoa.utilities.convertDatasetToDict(system.kanoa.order.getProductionOrderStates({}), 'workOrderStatusName', 'workOrderStatusId')
		
		#Check if product exists and if not, we will create it
		product = req_body['itemName']		
		itemInfo = system.kanoa.utilities.convertDatasetRowToJSON(system.kanoa.item.getItems({'itemName': product}),0)
		itemDescription = req_body['itemDescription'] if req_body.has_key('itemDescription') else 'created by ERP I/F'
		
		try:
			itemType = req_body['itemType']
			itemGroup = req_body['itemGroup']
			itemClass = req_body['itemClass']
			itemClassPath = "%s\%s\%s"%(itemType['description'] or itemType['name'], itemGroup['description'] or itemGroup['name'], itemClass['description'] or itemClass['name'])
			itemClassId = checkItemClassPath(itemClassPath) if itemClassPath else None
		except java.lang.Exception, e:
			log.warn("Error checking itemClassPath. %s"%e.cause)
			itemClassId = None
			itemClassPath = ''
	
		if itemInfo['itemId'] is None:
			log.info("This item wasn't found. Adding new product %s to %s"%(product, itemClassPath))
			paramsDict = {'itemName': product, 'itemDescription': itemDescription, 'itemClassId': itemClassId, 'itemColor': None, 'enabled': True}
			itemInfo['itemId'] = system.kanoa.item.addItem(paramsDict, userId)
		else:
			if itemDescription != itemInfo['itemDescription']:
				log.info("Updating %s description %s"%(product, itemDescription))
				system.kanoa.item.updateItemField(itemInfo['itemId'], 'itemDescription', itemDescription, userId)

			if itemClassId != itemInfo['itemClassId']:
				log.info("Updating itemClassId %s"%(itemClassId))
				system.kanoa.item.updateItemField(itemInfo['itemId'], 'itemClassId', itemClassId, userId)
	
		#Check if Manufacturng Order exists and update it or create it
		workOrderStatusId = woStates['Released']	#If we made it this far, order must be in a 'released' state
		
		if woInfo['workOrderId']:
			woInfo['reqdQty'] = reqdQty
			woInfo['dueDate'] = dueDate
			woInfo['assetId'] = assetId
			woInfo['itemId'] = itemInfo['itemId']
			woInfo['note'] = notes
			woInfo['itemUnitId'] = itemUnitId
			woInfo['workOrderStatusId'] = workOrderStatusId
			retVal = system.kanoa.order.updateProductionOrder(woInfo, userId)
			log.info("updateProductionOrder() returned %s"%retVal)			
		else:
			woInfo = {'workOrderName': woName, 'modeId': modeId, 'itemId': itemInfo['itemId'], 'itemUnitId': itemUnitId, 'assetId': assetId, 'workOrderSourceId':workOrderSourceId, 'reqdQty': reqdQty, 'dueDate': dueDate, 'workOrderStatusId': woStates['Released'], 'note': notes}
			woInfo['workOrderId'] = system.kanoa.order.addProductionOrder(woInfo, userId)
			log.info("addProductionOrder() returned %s"%woInfo['workOrderId'])
			
		if assetId:	#Only schedule if this is new and we have an assetId for it
			itemAssetRateId = system.kanoa.item.getAssetItems({'assetId': assetId, 'itemId': itemInfo['itemId']})
			if itemAssetRateId is None:
				itemSourceId = system.kanoa.utilities.getFieldValue('itemSourceId', system.kanoa.item.getItemSource({'itemSourceName': 'output'}))
				itemPeriodId = system.kanoa.utilities.getFieldValue('itemPeriodId', system.kanoa.item.getItemPeriod({'itemPeriodName': ratePeriod}))
				itemAssetRateInfo = {'itemId': itemId, 'assetId': assetId, 'standardRate': standardRate, 'scheduleRate': budgetRate, 'itemPeriodId': itemPeriodId, 'infeedUnitId': itemUnitId, 'outfeedUnitId': itemUnitId, 'wasteUnitId': itemUnitId, 'packageCount': 1.0, 'itemSourceId': itemSourceId, 'enabled': True}
				log.info("addItemAssetRate() called with  %s"%itemAssetRateInfo)
				itemAssetRateId = system.kanoa.item.addItemAssetRate(itemAssetRateInfo, userId)
		
			#ERP only sends us production orders, so we will check to see if this production order has already been scheduled. If it has we will update it
			scheduleBlockInfo = {'scheduleBlockName': 'M3 Manufacturing Order', 'assetId': assetId, 'itemId': itemInfo['itemId'], 'workOrderId': woInfo['workOrderId'], 'scheduledQty': reqdQty, 'modeId': modeId, 'startDate': targetStart, 'endDate': targetEnd, 'notes': None, 'rruleStr': None, 'color': None}		
			scheduleBlockInfo['scheduleBlockId'] = system.kanoa.utilities.getFieldValue('scheduleBlockId', system.kanoa.schedule.getScheduleBlocks({'workOrderId': woInfo['workOrderId']}))
	
			if scheduleBlockInfo['scheduleBlockId'] is None:
				log.info("addScheduleBlock() called with  %s"%scheduleBlockInfo)			
				scheduleBlockId = system.kanoa.schedule.addScheduleBlock(scheduleBlockInfo, userId)
				log.info("addScheduleBlock() returned %s"%scheduleBlockId)
			else:
				log.info("updateScheduleBlock() called with  %s"%scheduleBlockInfo)			
				retVal = system.kanoa.schedule.updateScheduleBlock(scheduleBlockInfo, userId)
				log.info("updateScheduleBlock() returned %s"%retVal)
				
			assetPath = system.kanoa.utilities.getFieldValue('assetPath', system.kanoa.asset.getAssets({'assetId': assetId}))
			log.info('updateClientsScheduleChange() called for %s'%assetPath)
			system.kanoa.schedule.updateClientsScheduleChange(assetPath)
	
		system.kanoa.order.addProductionOrderMetaData({'workOrderId': woInfo['workOrderId'], 'metaDataName': 'apiBody', 'metaDataValue': system.util.jsonEncode(req_body)}, userId)
		
		log.info('ERP Manufacturing order %s saved as %s'%(woName, woInfo['workOrderId']))
		success = True
		msg = None

	except java.lang.Exception, e:
		msg = e.cause
		success = False
		log.error('Java Exception: Failed to add ERP order %s %s'%(woName, msg))
	except:
		msg = 'Unknown error'
		success = False
		log.error('Exception: Failed to add ERP order %s %s'%(woName, msg))
		
	
	return success, msg