def onBarcodeDataReceived(session, data, context):
		
	logger = system.util.getLogger('gatewaySessionEvent')
	logger.info('barcode scan data: %s, context: %s'%(data, context))
	system.perspective.sendMessage("barcodeScanned", {'data': data, 'context': context}, pageId=context['pageId'])
	return