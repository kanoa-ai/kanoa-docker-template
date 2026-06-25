import hashlib
import json
#################################################################################
def dict_hash(dictionary):
	
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()    
#################################################################################
def createChecksum(req_body):
	'''
		Creates a checksum out of specific item values in the req_body that are worthy of causing the produciton order to be updated. 
		Args:
			req_body Dictionary
			
		Returns:
			checksum str
		
		Updated:
			jfc - 10/10/24 3:46pm Created
	'''
	
	checksumDict = {
						'machineName': req_body['scheduleInfo']['assetName'], 
						'targetStart': str(req_body['scheduleInfo']['startDate']), 
						'targetEnd': str(req_body['scheduleInfo']['endDate']), 
						'dueDate': str(req_body['dueDate']), 
						'itemName': req_body['itemName'], 
						'qty': req_body['orderQty'], 
						'uom': req_body['uom']
					}
	return str(kanoaScripts.custom.ops.erp.dict_hash(checksumDict))
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
def sendPO(req_body, rawJSON):
	
	log = system.util.getLogger('kanoa_ERP_IF')
	log.info('sendPO() called with %s'%(req_body))
	
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
#					'productionOrder': '010001444539', 
#					'itemDescription': 'APPLE JUICE /128 OZ ', 
#					'status': 20 #20 = Released, anything 80 and above is 'Closed', 40 - 'checking for components', 50, 60 - 'Order Started'. Just ignore 40,50 and 60 
#				}

#	try:
	if 1:
		woName = req_body['productionOrder']
		reqdQty = req_body['orderQty']
		dueDate = req_body['dueDate']
		woStatus = req_body['status']
		woInfo = system.kanoa.utilities.convertDatasetRowToJSON(system.kanoa.order.getProductionOrders({'workOrderName': woName}),0)
				
		targetStart = req_body['scheduleInfo']['startDate']
		targetEnd = req_body['scheduleInfo']['endDate']
				
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
		workOrderSourceId = system.kanoa.utilities.getFieldValue('workOrderSourceId', system.kanoa.order.getProductionOrderSource({'workOrderSourceName': 'ERP'}))				
		modeId = system.kanoa.utilities.getFieldValue('modeId', system.kanoa.asset.getModes({'modeName': modeName}))
		if modeId is None: modeId = system.kanoa.utilities.getFieldValue('modeId', system.kanoa.getModes({'assetId': assetId, 'modeName': 'Production'}))
		
		woStates = system.kanoa.utilities.convertDatasetToDict(system.kanoa.order.getProductionOrderStates({}), 'workOrderStatusName', 'workOrderStatusId')
		
		#Check if product exists and if not, we will create it
		product = req_body['itemName']		
		itemInfo = system.kanoa.utilities.convertDatasetRowToJSON(system.kanoa.item.getItems({'itemName': product}),0)
		itemDescription = req_body['itemDescription'] if req_body.has_key('itemDescription') else 'created by ERP I/F'
		
		try:
			itemClassPath = req_body['itemClassPath']
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

		workOrderMetaDataId = system.kanoa.utilities.getFieldValue('workOrderMetaDataId', kanoaScripts.custom.ops.erp.getProductionOrderMetaData({'workOrderId': woInfo['workOrderId'], 'metaDataName': 'apiBody'}))
		if workOrderMetaDataId is None:
			system.kanoa.order.addProductionOrderMetaData({'workOrderId': woInfo['workOrderId'], 'metaDataName': 'apiBody', 'metaDataValue': system.util.jsonEncode(rawJSON)}, userId)
		else:
			system.kanoa.order.updateProductionOrderMetaData({'workOrderMetaDataId': workOrderMetaDataId, 'workOrderId': woInfo['workOrderId'], 'metaDataName': 'apiBody', 'metaDataValue': system.util.jsonEncode(rawJSON)}, userId)
	
		orderChecksum = kanoaScripts.custom.ops.erp.createChecksum(req_body)
		workOrderMetaDataId = system.kanoa.utilities.getFieldValue('workOrderMetaDataId', kanoaScripts.custom.ops.erp.getProductionOrderMetaData({'workOrderId': woInfo['workOrderId'], 'metaDataName': 'apiBodyChecksum'}))		
		if workOrderMetaDataId is None:
			system.kanoa.order.addProductionOrderMetaData({'workOrderId': woInfo['workOrderId'], 'metaDataName': 'apiBodyChecksum', 'metaDataValue': (orderChecksum)}, userId)
		else:
			system.kanoa.order.updateProductionOrderMetaData({'workOrderMetaDataId': workOrderMetaDataId, 'workOrderId': woInfo['workOrderId'], 'metaDataName': 'apiBodyChecksum', 'metaDataValue': (orderChecksum)}, userId)
		
		log.info('ERP order %s saved as %s'%(woName, woInfo['workOrderId']))
		success = True
		msg = None

#	except java.lang.Exception, e:
#		msg = e.cause
#		success = False
#		log.error('Java Exception: Failed to add ERP order %s %s'%(woName, msg))
#	except:
#		msg = 'Unknown error'
#		success = False
#		log.error('Exception: Failed to add ERP order %s %s'%(woName, msg))
	
	return success, msg
##################################################################
def processPOFileEntries(fileData):
	"""
	Processes the fileData returned by readPOFile()
	
	Args:
		fileData (list of dictionaries)
	
	Returns:
		None
	
	Updated:
		jfc 10/8/24 5:14pm Created
	"""
	
	log = system.util.getLogger('kanoa_ERP_IF')
	
	itemClassPath = None
	createdBy = 'ERP'
	status = 'Released'
	
	orderMetaData = kanoaScripts.custom.ops.erp.getProductionOrderMetaData({'metaDataName': 'apiBodyChecksum', 'workOrderStatusList': ['Released', 'Scheduled', 'In Progress']})
	orderMetaDataInfo = system.kanoa.utilities.convertDatasetToDict(orderMetaData, 'workOrderName', 'metaDataValue')
	mesOrders = orderMetaDataInfo.keys()	#returns a list of active orders in MES
	poAddNum = 0
	poChangeNum = 0
	poCloseNum = 0
	activeERPOrders = []

	for entry in fileData:
#		for k,v in entry.items(): print '%s : %s'%(k,v)

		if entry['Sched.'] in ['2BT']: continue		#This is the X5000 line. Only import PO's for X5000 at this time jfc 10/9/24
		activeERPOrders.append(entry['Order Numb'])	#The file should contain all active orders. If an order is active (not cosed) in MES and not in the file, then we shall close it

		req_body = {
						'orderType': 'PRODUCTION', 
						'notes': '',
						'updatedBy': '', 
						'scheduleInfo': {
											'rateInfo': {
															'period': 'hour', 
															'equipmentRate': 0, 
															'budgetRate': 0.0
														}, 
											'assetName': entry['Prod. Line'], 
											'startDate': system.date.parse(entry['Sched. Sta'], "MM/dd/yyyy") if entry['Sched. Sta'] else None,
											'endDate': system.date.parse(entry['Sched. Fin'], "MM/dd/yyyy") if entry['Sched. Fin'] else None,
										}, 
						'dueDate': system.date.parse(entry['Basic Fini'], "MM/dd/yyyy") if entry['Basic Fini'] else None, 
						'itemName': entry['Material'], 
						'uom': entry['Order unit'], 
						'itemClassPath': '', 
						'createdBy': 'ERP', 
						'orderQty': entry['Tot Order'],
						'productionOrder': entry['Order Numb'], 
						'itemDescription': entry['Description'], 
						'status': 'Released'
					}		

		if entry['Order Numb'] in mesOrders:
			orderChecksum = kanoaScripts.custom.ops.erp.createChecksum(req_body)
			if orderMetaDataInfo[entry['Order Numb']] == orderChecksum: continue	#log.info("No changes to %s checksum"%entry['Order Numb'])			
			log.info("Order %s has updated values"%entry['Order Numb'])
			poChangeNum += 1			
		else:	
			log.info("found new order %s"%entry['Order Numb'])
			poAddNum += 1
	
		kanoaScripts.custom.ops.erp.sendPO(req_body, entry)
	
#		return	#Just test with first entry.

	missingOrders = [x for x in mesOrders if x not in activeERPOrders]
	if len(missingOrders):
		log.info("Found missing orders %s"%missingOrders)
		userId = system.kanoa.security.getIDPUserId({'userName': 'SYSTEM'})
		workOrderStatusId = system.kanoa.utilities.getFieldValue('workOrderStatusId', system.kanoa.order.getProductionOrderStates({'workOrderStatusName': 'Closed'}))
		for order in missingOrders:
			workOrderId = system.kanoa.utilities.getFieldValue('workOrderId', system.kanoa.order.getProductionOrders({'workOrderName': order}))
#			log.info("Setting %s status to %s"%(workOrderId, workOrderStatusId))
			poCloseNum += system.kanoa.order.updateProductionOrderField(workOrderId, 'workOrderStatusId', workOrderStatusId, userId)
	
	if poAddNum or poChangeNum or poCloseNum: log.info("processPOFileEntries() called. %s orders added %s changed %s closed"%(poAddNum, poChangeNum, poCloseNum))
	
	return