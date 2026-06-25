def onPageStartup(page):
	
	log = system.util.getLogger('kanoaApp')

	pageId = page.props.pageId
	if '/' in pageId or pageId == 'session-props': pageId = 'designer'	#In the designer, the viewPath is passed in as the pageId. In the client, a uuid is passed in
	if not page.session.custom.has_key('kanoa'): page.session.custom['kanoa'] = {}
	if not page.session.custom.kanoa.has_key(pageId):
		log.info("Creating session properties for navigation, selectors")
		page.session.custom.kanoa[pageId] = {
												'navigation': 
													{'history': [{'path': page.props.path, 'name': 'Home', 'type': 'page', 'params': None}], 'currentIndex': 0},
												'selectors':
												{
												'assetPath':None,
												'dateRange': {'startDate': None, 'endDate': None, 'selectedRange':'Today'},
												'woInfo': {"product": None, "scheduleId": None, "woId": None}},
												'enterpriseView': {"expand": True, "openState": False, "selectedRange": "Today"}
											}
	else:
		navigation = page.session.custom.kanoa[pageId].navigation
		initialPage = navigation.history[navigation.currentIndex]
		params = system.util.jsonDecode(initialPage['params'])
		if initialPage['path'] == '/': system.perspective.navigate(page=initialPage['path'], params=params)
		else: system.perspective.navigate(view=initialPage['path'], params=params)
	
	return