def importItems(inputFile, userId):

	import org.apache.poi.ss.usermodel.WorkbookFactory as WorkbookFactory
	import org.apache.poi.ss.usermodel.DateUtil as DateUtil
	from java.io import ByteArrayInputStream
	from java.util import Date
	
	"""
	   Function to create a dataset from an Excel spreadsheet. It will try to automatically detect the boundaries of the data,
	   but helper parameters are available:
	   params:
	   		fileName   - The path to the Excel spreadsheet. (required)
	   		hasHeaders - If true, uses the first row of the spreadsheet as column names.
	   		sheetNum   - select the sheet to process. defaults to the first sheet.
	   		firstRow   - select first row to process. 
	   		lastRow    - select last row to process.
	   		firstCol   - select first column to process
	   		lastCol    - select last column toprocess
	"""
	
	hasHeaders = True
	firstRow = None
	lastRow = None
	firstCol = None
	lastCol = None

	print("%s received"%inputFile.getString())

	fileStream = ByteArrayInputStream(inputFile.getBytes())
	wb = WorkbookFactory.create(fileStream)
	
	sheetNum = wb.getSheetIndex('USM4 X5000 MATERIALS')
	sheet = wb.getSheetAt(sheetNum)

	if firstRow is None: firstRow = sheet.getFirstRowNum()
	if lastRow is None: lastRow = sheet.getLastRowNum()
	
	data = []
	for i in range(firstRow , lastRow + 1):
		row = sheet.getRow(i)
		if row is None:
			system.perspective.print("row %s is None"%i)
			continue
		system.perspective.print("row %s - %s"%(i, list(row)))
		if i == firstRow:
			if firstCol is None: firstCol = row.getFirstCellNum()
			if lastCol is None: lastCol  = row.getLastCellNum()
			else: lastCol += 1	# if lastCol is specified add 1 to it.
			if hasHeaders: 	headers = list(row)[firstCol:lastCol]
			else: headers = ['Col'+str(cNum) for cNum in range(firstCol, lastCol)]
			system.perspective.print("headers - %s"%headers)
			
		rowOut = []
		for j in range(firstCol, lastCol):
			if i == firstRow and hasHeaders: pass
			else:
#				system.perspective.print('i %s j %s'%(i,j))
				cell = row.getCell(j)
				if cell is None: 
					system.perspective.print("cellType is None")
					value = None
				else:
					cellType = cell.getCellType().toString()
#					system.perspective.print("cellType is %s"%cellType)
					if cellType == 'NUMERIC':
						if DateUtil.isCellDateFormatted(cell):
							value = cell.dateCellValue
						else:
							value = cell.getNumericCellValue()
							if value == int(value):
								value = int(value)
					elif cellType == 'STRING': value = cell.getStringCellValue()
					elif cellType == 'BOOLEAN': value = cell.getBooleanCellValue()
					elif cellType == 'BLANK': value = None	
					elif cellType == 'FORMULA':
						formulatype=str(cell.getCachedFormulaResultType())
						if formulatype == 'NUMERIC':
							if DateUtil.isCellDateFormatted(cell): value =  cell.dateCellValue
							else:
								value = cell.getNumericCellValue()
								if value == int(value): value = int(value)
						elif formulatype == 'STRING': value = cell.getStringCellValue()
						elif formulatype == 'BOOLEAN': value = cell.getBooleanCellValue()
						elif formulatype == 'BLANK': value = None
					else: value = None	
				
				rowOut.append(str(value))
				
		if len(rowOut) > 0: data.append(rowOut)
		
#		if i > 2: break	Just do a couple of rows for testing purposes
	
	data = system.dataset.toPyDataSet(system.dataset.toDataSet(headers, data))
		
	counter = 0
	
	assetAttributes = system.kanoa.utilities.convertDatasetToJSON(system.kanoa.asset.getAssetAttributes({}))
	attrInfo = {item['assetAttrValue']: item['assetId'] for item in assetAttributes if item['assetAttrName'] == 'erpName'}
	itemSourceId = system.kanoa.utilities.getFieldValue('itemSourceId', system.kanoa.item.getItemSource({'itemSourceName': 'output'}))
	
	for row in data:
		
		itemName = row['PHPRNO']
		system.perspective.print('Row %s item %s'%(counter,itemName))
		itemId = system.kanoa.utilities.getFieldValue('itemId', system.kanoa.item.getItems({'itemName': itemName}))
		if itemId is None:
			system.perspective.print('This item has not yet been configured in MES. Adding item....')
			itemClassId = system.kanoa.utilities.getFieldValue('itemClassId', system.kanoa.item.getItemClasses({'itemClassName': row['CLASSPATH']}))
			if itemClassId is None: itemClassId = kanoaScripts.custom.ops.erp.checkItemClassPath(row['CLASSPATH'])	
			itemId = system.kanoa.item.addItem({'itemName': itemName, 'itemDescription': row['MMITDS'], 'itemClassId': itemClassId, 'itemColor': None, 'enabled': True}, userId)		
		
		#Look to see if the unit of measure exists in MES
		uom = row['MMUNMS'].lower() if row['MMUNMS'] is not None else 'units'
		outfeedItemUnitId = system.kanoa.utilities.getFieldValue('itemUnitId', system.kanoa.item.getItemUnits({'itemUnitName': uom}))
		if outfeedItemUnitId is None: outfeedItemUnitId = system.kanoa.item.addItemUnit(uom, userId)
		
		#Look to see if the unit of measure exists in MES
		uom = row['Infeed Units'].lower() if row['Infeed Units'] is not None else 'units'
		infeedItemUnitId = system.kanoa.utilities.getFieldValue('itemUnitId', system.kanoa.item.getItemUnits({'itemUnitName': uom}))
		if infeedItemUnitId is None: infeedItemUnitId = system.kanoa.item.addItemUnit(uom, userId)
		
		#Look to see if the unit of measure exists in MES
		uom = row['Waste Units'].lower() if row['Waste Units'] is not None else 'units'
		wasteItemUnitId = system.kanoa.utilities.getFieldValue('itemUnitId', system.kanoa.item.getItemUnits({'itemUnitName': uom}))
		if wasteItemUnitId is None: wasteItemUnitId = system.kanoa.item.addItemUnit(uom, userId)
		
		#Look to see if the unit of measure exists in MES
		itemPeriod = row['Period'].lower() if row['Period'] is not None else 'No Period'
		itemPeriodId = system.kanoa.utilities.getFieldValue('itemPeriodId', system.kanoa.item.getItemPeriod({'itemPeriodName': itemPeriod}))
		if itemPeriodId is None: itemPeriodId = system.kanoa.item.addItemPeriod({'itemPeriodName': itemPeriod, 'enabled': True}, userId)
		
		#look to see if we can find the asset that this MO is referring to
		machineName = row['PHFACI'] + ' - ' + row['POPLGR'] 
		assetId = attrInfo[machineName] if attrInfo.has_key(machineName) else None
		if assetId: 
			system.perspective.print("Found assetId %s for %s"%(assetId, machineName))
			rateInfo = system.kanoa.utilities.convertDatasetRowToJSON( system.kanoa.item.getAssetItems({'assetId':assetId, 'itemId':itemId}), 0)
			rateInfo['itemSourceId'] = itemSourceId
			rateInfo['itemId'] = itemId
			rateInfo['enabled'] = True
			rateInfo['scheduleRate'] = row['Budget Rate']
			rateInfo['assetId'] = assetId
			rateInfo['infeedUnitId'] = infeedItemUnitId
			rateInfo['wasteUnitId'] = wasteItemUnitId
			rateInfo['outfeedUnitId'] = outfeedItemUnitId
			rateInfo['itemPeriodId'] = itemPeriodId
			rateInfo['packageCount'] = row['Package Count']
			rateInfo['standardRate'] = row['Design Rate']
			
			if rateInfo['itemAssetRateId']:
				system.perspective.print('updateItemAssetRate called with %s'%rateInfo)
				system.kanoa.item.updateItemAssetRate(rateInfo, userId)
			else:
				system.perspective.print('addItemAssetRate called with %s'%rateInfo)
				itemAssetRateId = system.kanoa.item.addItemAssetRate(rateInfo, userId)
		else: system.perspective.print("No assetId found for %s. No asset item rate will be set for this asset"%(machineName))

		counter += 1
		
	return counter