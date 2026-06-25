def parseExcelFile(inputFile, workSheetName):
	
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
	
	log = system.util.getLogger('kanoa_import')
	
	hasHeaders = True
	firstRow = None
	lastRow = None
	firstCol = None
	lastCol = None

#	log.info("%s received"%inputFile.getString())

	fileStream = ByteArrayInputStream(inputFile.getBytes())
	wb = WorkbookFactory.create(fileStream)
	
	sheetNum = wb.getSheetIndex(workSheetName)
	sheet = wb.getSheetAt(sheetNum)

	if firstRow is None: firstRow = sheet.getFirstRowNum()
	if lastRow is None: lastRow = sheet.getLastRowNum()
	
	data = []
	for i in range(firstRow , lastRow + 1):
		row = sheet.getRow(i)
		if row is None:
			log.info("row %s is None"%i)
			continue
#		log.info("row %s - %s"%(i, list(row)))
		if i == firstRow:
			if firstCol is None: firstCol = row.getFirstCellNum()
			if lastCol is None: lastCol  = row.getLastCellNum()
			else: lastCol += 1	# if lastCol is specified add 1 to it.
			if hasHeaders: 	headers = list(row)[firstCol:lastCol]
			else: headers = ['Col'+str(cNum) for cNum in range(firstCol, lastCol)]
			log.info("headers - %s"%headers)
			
		rowOut = []
		for j in range(firstCol, lastCol):
			if i == firstRow and hasHeaders: pass
			else:
#				log.info('i %s j %s'%(i,j))
				cell = row.getCell(j)
				if cell is None: 
					print("cellType is None")
					value = None
				else:
					cellType = cell.getCellType().toString()
#					log.info("cellType is %s"%cellType)
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
	
	return system.dataset.toPyDataSet(system.dataset.toDataSet(headers, data))
#######################################################
def importStates(inputFile, workSheetName, userId):

	log = system.util.getLogger('kanoa_import')

	stateTypes = system.kanoa.utilities.convertDatasetToDict(system.kanoa.asset.getStateType({}), 'stateTypeName', 'stateTypeId')
	stateCategories = system.kanoa.utilities.convertDatasetToDict(system.kanoa.asset.getStateCategory({}), 'stateCategoryName', 'stateCategoryId')

	data = kanoaScripts.custom.ops.import.parseExcelFile(inputFile, workSheetName)	
	counter = 0
	for row in data:
		
		stateName = row['stateName']
		stateTypeName = row['stateTypeName']
		stateCategoryName = row['stateCategoryName']
		
		log.info('Row %s %s %s %s'%(counter,stateName, stateTypeName, stateCategoryName))
		
		stateId = system.kanoa.utilities.getFieldValue('stateId', system.kanoa.asset.getStates({'stateName': stateName}))
		
		if stateId is None:
			log.info('This state has not yet been configured in MES. Adding state %s %s %s'%(stateName, stateTypeName, stateCategoryName))
			if stateTypes[stateTypeName] is None:
				log.error("Invalid stateType passed. Ignoring state %s %s %s"%(stateName, stateTypeName, stateCategoryName))
				continue

			if stateCategories[stateCategoryName] is None:
				log.info("Adding new state category %s"%(stateCategoryName))
				stateCategories[stateCategoryName] = system.kanoa.asset.addStateCategory(stateCategoryName, userId)

			system.kanoa.asset.addState({'stateName': stateName, 'stateCategoryId': stateCategories[stateCategoryName], 'stateTypeId': stateTypes[stateTypeName], 'assetGroupId': None, 'enabled':True, 'stateColor': None}, userId)
		
		counter += 1
		
	return counter
#######################################################
def importAssetStates(inputFile, workSheetName, userId):

	log = system.util.getLogger('kanoa_import')
	
	states = system.kanoa.utilities.convertDatasetToDict(system.kanoa.asset.getStates({}), 'stateName', 'stateId')
	assets = system.kanoa.utilities.convertDatasetToDict(system.kanoa.asset.getAssets({}), 'assetPath', 'assetId')

	data = kanoaScripts.custom.ops.import.parseExcelFile(inputFile, workSheetName)	
	counter = 0
	for row in data:
		counter += 1
		
		stateName = row['stateName']
		assetPath = row['assetPath']
		
		log.info('Row %s %s %s'%(counter,stateName, assetPath))
		stateId = states[stateName]
		if stateId is None:
			log.error("Invalid state passed. Ignoring state %s %s"%(stateName, assetPath))
			continue
			
		assetId = assets[assetPath]
		if assetId is None:
			log.error("Invalid assetPath passed. Ignoring state %s %s"%(stateName, assetPath))
			continue

		stateAssetLinkId = system.kanoa.utilities.getFieldValue('stateAssetLinkId', system.kanoa.asset.getAssetStates({'assetId': assetId, 'stateId': stateId}))
		if stateAssetLinkId is not None:
			log.warn("This asset %s is already linked to this state %s. Ignoring...."%(assetPath, stateName))
			continue
			
		stateCode = getNextCode(list(set([row['stateCode'] for row in system.kanoa.asset.getAssetStates({'assetId': assetId}) if row['stateCode']])))

		log.info("Linking asset %s to state %s with code %s"%(assetId, stateId, stateCode))
		system.kanoa.asset.linkAssetStates([assetId], [stateId], userId, [stateCode])
				
	return counter
#######################################################
def getNextCode(codeList):
	
	if len(codeList or []) == 0: return 1

	vals = list(set(range(codeList[len(codeList)-1])[1:]) - set(codeList))
	if len(vals) == 0: nextInt = max(codeList) + 1
	else: nextInt = vals[0]
	
#	log.info("getNextCode() returned %s"%nextInt)
	
	return nextInt
#######################################################
def importAssetStateEvents(inputFile, workSheetName, userId):

	log = system.util.getLogger('kanoa_import')
	
	data = kanoaScripts.custom.ops.import.parseExcelFile(inputFile, workSheetName)	
	counter = 0
	for row in data:
		t_stamp = system.date.parse(row['tStamp'])
		t_stamp = system.date.addMinutes(t_stamp, 480)
		stateInfo = {'assetId': int(row['assetId']), 'assetStateId': int(row['assetId']), 'stateCode': int(row['stateCode']), 'tStamp': t_stamp, 'note': None}
		stateEventId = system.kanoa.event.addStateEvent(stateInfo, userId)
		log.info("called addStateEvent() with %s. returned %s"%(stateInfo,stateEventId))

		counter += 1
		
	return counter
#######################################################











