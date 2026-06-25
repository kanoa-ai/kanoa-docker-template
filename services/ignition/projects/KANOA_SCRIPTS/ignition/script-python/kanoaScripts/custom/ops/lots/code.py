def importLots(inputFile, userId):

	import org.apache.poi.ss.usermodel.WorkbookFactory as WorkbookFactory
	import org.apache.poi.ss.usermodel.DateUtil as DateUtil
	from java.io import ByteArrayInputStream
	from java.util import Date
	
	"""
	   Function to create a dataset from an Excel spreadsheet. Use the fileUpload perspecitve component to seelct the file to open. inputFile is the fileUpload event.file property
	   It will try to automatically detect the boundaries of the data,
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
	
	sheetNum = wb.getSheetIndex('Sheet1')
	sheet = wb.getSheetAt(sheetNum)

	if firstRow is None: firstRow = sheet.getFirstRowNum()
	if lastRow is None: lastRow = sheet.getLastRowNum()
	
	data = []
	for i in range(firstRow , lastRow + 1):
		row = sheet.getRow(i)
#		system.perspective.print("row %s - %s"%(i, list(row)))
		if i == firstRow:
			if firstCol is None: firstCol = row.getFirstCellNum()
			if lastCol is None: lastCol  = row.getLastCellNum()
			else: lastCol += 1	# if lastCol is specified add 1 to it.
			if hasHeaders: 	headers = list(row)[firstCol:lastCol]
			else: headers = ['Col'+str(cNum) for cNum in range(firstCol, lastCol)]
#			system.perspective.print("headers - %s"%headers)
			
		rowOut = []
		for j in range(firstCol, lastCol):
			if i == firstRow and hasHeaders: pass
			else:
				cell = row.getCell(j)
				cellType = cell.getCellType().toString()
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
	
	data = system.dataset.toPyDataSet(system.dataset.toDataSet(headers, data))
		
	itemSourceId = system.kanoa.utilities.getFieldValue('itemSourceId', system.kanoa.item.getItemSource({'itemSourceName': 'input'}))
	lotStateId = system.kanoa.utilities.getFieldValue('lotStateId', system.kanoa.lot.getLotStates({'lotStateName': 'OK'}))
	itemClassId = system.kanoa.utilities.getFieldValue('itemClassId', system.kanoa.item.getItemClasses({'itemClassName': 'MFR'}))
	if itemClassId is None: itemClassId = system.kanoa.item.addItemClass({'itemClassName': 'MFR', 'parentId': None, 'itemClassDescription': None, 'itemClassColor': None, 'enabled': True}, userId)	
	
	counter = 0
	
	for row in data:
		try:
			qty = float(row['Quantity'])
		except:
			system.perspective.print('This row is not a valid quantity')
			continue
			
		if qty == 0: continue
		
		itemName = row['Item No']
		lotName = row['Lot No.']
		itemId = system.kanoa.utilities.getFieldValue('itemId', system.kanoa.item.getItems({'itemName': itemName}))
		if itemId is None:
#			system.perspective.print('This item has not yet been configured in MES. Adding item....')
			itemId = system.kanoa.item.addItem({'itemName': itemName, 'itemDescription': None, 'itemClassId': itemClassId, 'itemColor': None, 'enabled': True}, userId)		
			
		lotId = system.kanoa.utilities.getFieldValue('lotId', system.kanoa.lot.getLots({'lotName': lotName}))
		if lotId is None:
#			system.perspective.print('Adding Lot %s %s'%(row['Lot No.'], itemId))
			lotId = system.kanoa.lot.addLot({'lotName': row['Lot No.'], 'itemId': itemId}, userId)
		
		if system.kanoa.utilities.getFieldValue('lotEventId', system.kanoa.lot.getLotEvents({'lotId': lotId, 'lotQty': qty, 'inputSourceId': 'input'})):
			system.perspective.print('Already received lot %s'%(lotName))
			continue
		
		lotEventInfo = {'lotId': lotId, 'lotEventQty': float(qty), 'itemUnitId': None, 'workOrderId': None, 'assetId':None, 'itemSourceId': itemSourceId, 'lotStateId': lotStateId, 'lotStateReasonId': None, 'shiftId': None, 'tStamp': system.date.now(), 'comment':None}
		system.kanoa.lot.addLotEvent(lotEventInfo, userId)
		counter += 1
		
	return counter