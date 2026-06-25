##########################################################################################
def getCSSColor(cssLabel, themeName = 'kanoa-light'):
	'''
		This is (hopefully) a temporary function to return the HEX color value for a CSS
		label since "--kcXYZ" arguments do not work for some Ignition components. There is a ticket in with IA identifying the components that do not honor css labels

		Args:
			cssLabel: the label of the CSS element you want the HEX string for
		returns:
			HEX string of the CSS value
			
		Updated:
			slr - 12/11/2023 6:04p Created
			slr - 01/02/2024 9:05a Updated to use theme instead of t/f designation for dark mode. defaults to Light
			jfc 6/5/26 6:26am: removed client references
	'''
	if themeName == 'kanoa-forest':
		if cssLabel == '--kcPrimary': return '#436914';
		elif cssLabel == '--kcOnPrimary': return '#ffffff';
		elif cssLabel == '--kcPrimaryContainer': return '#c3f18d';
		elif cssLabel == '--kcOnPrimaryContainer': return '#0f2000';
		elif cssLabel == '--kcSecondary': return '#586249';
		elif cssLabel == '--kcOnSecondary': return '#ffffff';
		elif cssLabel == '--kcSecondaryContainer': return '#dbe7c8';
		elif cssLabel == '--kcOnSecondaryContainer': return '#151e0b';
		elif cssLabel == '--kcTertiary': return '#386663';
		elif cssLabel == '--kcOnTertiary': return '#ffffff';
		elif cssLabel == '--kcTertiaryContainer': return '#bbece8';
		elif cssLabel == '--kcOnTertiaryContainer': return '#00201e';
		elif cssLabel == '--kcError': return '#ba1a1a';
		elif cssLabel == '--kcErrorContainer': return '#ffdad6';
		elif cssLabel == '--kcOnError': return '#ffffff';
		elif cssLabel == '--kcOnErrorContainer': return '#410002';
		elif cssLabel == '--kcBackground': return '#fdfcf5';
		elif cssLabel == '--kcOnBackground': return '#1b1c18';
		elif cssLabel == '--kcSurface': return '#fdfcf5';
		elif cssLabel == '--kcOnSurface': return '#1b1c18';
		elif cssLabel == '--kcSurfaceVariant': return '#e1e4d5';
		elif cssLabel == '--kcOnSurfaceVariant': return '#44483d';
		elif cssLabel == '--kcOutline': return '#75796c';
		elif cssLabel == '--kcInverseOnSurface': return '#f2f1e9';
		elif cssLabel == '--kcInverseSurface': return '#30312c';
		elif cssLabel == '--kcInversePrimary': return '#a8d474';
		elif cssLabel == '--kcShadow': return '#000000';
		elif cssLabel == '--kcSurfaceTint': return '#436914';
		elif cssLabel == '--kcOutlineVariant': return '#c5c8ba';
		elif cssLabel == '--kcScrim': return '#000000';
		elif cssLabel == '--kcGood': return '#436914';
		elif cssLabel == '--kcOK': return '#FFC95F';
		elif cssLabel == '--kcBad': return '#862B0D';
		elif cssLabel == '--kcGoodContainer': return '#c3f18d';
		elif cssLabel == '--kcOnGoodContainer': return '#0f2000';
		elif cssLabel == '--kcOKContainer': return '#f6bd48';
		elif cssLabel == '--kcOnOKContainer': return '#412d00';
		elif cssLabel == '--kcBadContainer': return '#a13f20';
		elif cssLabel == '--kcOnBadContainer': return '#ffffff';
	elif themeName == 'kanoa-dark':
		if cssLabel == '--kcPrimary': return '#95ccff';
		elif cssLabel == '--kcOnPrimary': return '#003352';
		elif cssLabel == '--kcPrimaryContainer': return '#004a75';
		elif cssLabel == '--kcOnPrimaryContainer': return '#cde5ff';
		elif cssLabel == '--kcSecondary': return '#b9c8da';
		elif cssLabel == '--kcOnSecondary': return '#233240';
		elif cssLabel == '--kcSecondaryContainer': return '#3a4857';
		elif cssLabel == '--kcOnSecondaryContainer': return '#d5e4f6';
		elif cssLabel == '--kcTertiary': return '#ffb693';
		elif cssLabel == '--kcOnTertiary': return '#561f00';
		elif cssLabel == '--kcTertiaryContainer': return '#7a3000';
		elif cssLabel == '--kcOnTertiaryContainer': return '#ffdbcc';
		elif cssLabel == '--kcError': return '#ffb4ab';
		elif cssLabel == '--kcErrorContainer': return '#93000a';
		elif cssLabel == '--kcOnError': return '#690005';
		elif cssLabel == '--kcOnErrorContainer': return '#ffdad6';
		elif cssLabel == '--kcBackground': return '#1a1c1e';
		elif cssLabel == '--kcOnBackground': return '#e2e2e5';
		elif cssLabel == '--kcSurface': return '#1a1c1e';
		elif cssLabel == '--kcOnSurface': return '#e2e2e5';
		elif cssLabel == '--kcSurfaceVariant': return '#42474e';
		elif cssLabel == '--kcOnSurfaceVariant': return '#c2c7cf';
		elif cssLabel == '--kcOutline': return '#8c9198';
		elif cssLabel == '--kcInverseOnSurface': return '#1a1c1e';
		elif cssLabel == '--kcInverseSurface': return '#e2e2e5';
		elif cssLabel == '--kcInversePrimary': return '#00639a';
		elif cssLabel == '--kcShadow': return '#000000';
		elif cssLabel == '--kcSurfaceTint': return '#95ccff';
		elif cssLabel == '--kcOutlineVariant': return '#42474e';
		elif cssLabel == '--kcScrim': return '#000000';
		elif cssLabel == '--kcGood': return '#96ccff';
		elif cssLabel == '--kcGoodContainer': return '#004a75';
		elif cssLabel == '--kcOnGoodContainer': return '#cee5ff';
		elif cssLabel == '--kcOK': return '#fbbd15';
		elif cssLabel == '--kcOKContainer': return '#5c4300';
		elif cssLabel == '--kcOnOKContainer': return '#ffdea0';
		elif cssLabel == '--kcBad': return '#ffb4ab';
		elif cssLabel == '--kcBadContainer': return '#930009';
		elif cssLabel == '--kcOnBadContainer': return '#ffdad5';
	elif themeName == 'kanoa-grape':
		if cssLabel == '--kcPrimary': return '#8a428c';
		elif cssLabel == '--kcOnPrimary': return '#ffffff';
		elif cssLabel == '--kcPrimaryContainer': return '#ffd6f9';
		elif cssLabel == '--kcOnPrimaryContainer': return '#37003c';
		elif cssLabel == '--kcSecondary': return '#6c586a';
		elif cssLabel == '--kcOnSecondary': return '#ffffff';
		elif cssLabel == '--kcSecondaryContainer': return '#f6dbf0';
		elif cssLabel == '--kcOnSecondaryContainer': return '#261625';
		elif cssLabel == '--kcTertiary': return '#825248';
		elif cssLabel == '--kcOnTertiary': return '#ffffff';
		elif cssLabel == '--kcTertiaryContainer': return '#ffdad3';
		elif cssLabel == '--kcOnTertiaryContainer': return '#33110a';
		elif cssLabel == '--kcError': return '#ba1a1a';
		elif cssLabel == '--kcErrorContainer': return '#ffdad6';
		elif cssLabel == '--kcOnError': return '#ffffff';
		elif cssLabel == '--kcOnErrorContainer': return '#410002';
		elif cssLabel == '--kcBackground': return '#fffbff';
		elif cssLabel == '--kcOnBackground': return '#1e1a1d';
		elif cssLabel == '--kcSurface': return '#fffbff';
		elif cssLabel == '--kcOnSurface': return '#1e1a1d';
		elif cssLabel == '--kcSurfaceVariant': return '#eddee8';
		elif cssLabel == '--kcOnSurfaceVariant': return '#4d444b';
		elif cssLabel == '--kcOutline': return '#7f747c';
		elif cssLabel == '--kcInverseOnSurface': return '#f8eef2';
		elif cssLabel == '--kcInverseSurface': return '#342f32';
		elif cssLabel == '--kcInversePrimary': return '#feaafc';
		elif cssLabel == '--kcShadow': return '#000000';
		elif cssLabel == '--kcSurfaceTint': return '#8a428c';
		elif cssLabel == '--kcOutlineVariant': return '#d0c3cc';
		elif cssLabel == '--kcScrim': return '#000000';
	elif themeName == 'kanoa-orange':
		if cssLabel == '--kcPrimary': return '#914c00';
		elif cssLabel == '--kcOnPrimary': return '#ffffff';
		elif cssLabel == '--kcPrimaryContainer': return '#ffdcc4';
		elif cssLabel == '--kcOnPrimaryContainer': return '#2f1500';
		elif cssLabel == '--kcSecondary': return '#745944';
		elif cssLabel == '--kcOnSecondary': return '#ffffff';
		elif cssLabel == '--kcSecondaryContainer': return '#ffdcc4';
		elif cssLabel == '--kcOnSecondaryContainer': return '#2a1707';
		elif cssLabel == '--kcTertiary': return '#5d6236';
		elif cssLabel == '--kcOnTertiary': return '#ffffff';
		elif cssLabel == '--kcTertiaryContainer': return '#e2e7b0';
		elif cssLabel == '--kcOnTertiaryContainer': return '#1a1e00';
		elif cssLabel == '--kcError': return '#ba1a1a';
		elif cssLabel == '--kcErrorContainer': return '#ffdad6';
		elif cssLabel == '--kcOnError': return '#ffffff';
		elif cssLabel == '--kcOnErrorContainer': return '#410002';
		elif cssLabel == '--kcBackground': return '#fffbff';
		elif cssLabel == '--kcOnBackground': return '#201a17';
		elif cssLabel == '--kcSurface': return '#fffbff';
		elif cssLabel == '--kcOnSurface': return '#201a17';
		elif cssLabel == '--kcSurfaceVariant': return '#f3dfd2';
		elif cssLabel == '--kcOnSurfaceVariant': return '#51443b';
		elif cssLabel == '--kcOutline': return '#847469';
		elif cssLabel == '--kcInverseOnSurface': return '#faeee8';
		elif cssLabel == '--kcInverseSurface': return '#352f2b';
		elif cssLabel == '--kcInversePrimary': return '#ffb77f';
		elif cssLabel == '--kcShadow': return '#000000';
		elif cssLabel == '--kcSurfaceTint': return '#914c00';
		elif cssLabel == '--kcOutlineVariant': return '#d6c3b7';
		elif cssLabel == '--kcScrim': return '#000000';
	elif themeName == 'kanoa-firetruck':
		if cssLabel == '--kcPrimary': return '#ba1a1a';
		elif cssLabel == '--kcOnPrimary': return '#ffffff';
		elif cssLabel == '--kcPrimaryContainer': return '#ffdad5';
		elif cssLabel == '--kcOnPrimaryContainer': return '#410002';
		elif cssLabel == '--kcSecondary': return '#775652';
		elif cssLabel == '--kcOnSecondary': return '#ffffff';
		elif cssLabel == '--kcSecondaryContainer': return '#ffdad5';
		elif cssLabel == '--kcOnSecondaryContainer': return '#2c1512';
		elif cssLabel == '--kcTertiary': return '#715b2e';
		elif cssLabel == '--kcOnTertiary': return '#ffffff';
		elif cssLabel == '--kcTertiaryContainer': return '#fddfa6';
		elif cssLabel == '--kcOnTertiaryContainer': return '#261a00';
		elif cssLabel == '--kcError': return '#ba1a1a';
		elif cssLabel == '--kcErrorContainer': return '#ffdad6';
		elif cssLabel == '--kcOnError': return '#ffffff';
		elif cssLabel == '--kcOnErrorContainer': return '#410002';
		elif cssLabel == '--kcBackground': return '#fffbff';
		elif cssLabel == '--kcOnBackground': return '#201a19';
		elif cssLabel == '--kcSurface': return '#fffbff';
		elif cssLabel == '--kcOnSurface': return '#201a19';
		elif cssLabel == '--kcSurfaceVariant': return '#f5ddda';
		elif cssLabel == '--kcOnSurfaceVariant': return '#534341';
		elif cssLabel == '--kcOutline': return '#857371';
		elif cssLabel == '--kcInverseOnSurface': return '#fbeeec';
		elif cssLabel == '--kcInverseSurface': return '#362f2e';
		elif cssLabel == '--kcInversePrimary': return '#ffb4ab';
		elif cssLabel == '--kcShadow': return '#000000';
		elif cssLabel == '--kcSurfaceTint': return '#ba1a1a';
		elif cssLabel == '--kcOutlineVariant': return '#d8c2bf';
		elif cssLabel == '--kcScrim': return '#000000';
	else: # kanoa-light
		if cssLabel == '--kcPrimary': return '#00639a';
		elif cssLabel == '--kcOnPrimary': return '#ffffff';
		elif cssLabel == '--kcPrimaryContainer': return '#cde5ff';
		elif cssLabel == '--kcOnPrimaryContainer': return '#001d32';
		elif cssLabel == '--kcSecondary': return '#51606f';
		elif cssLabel == '--kcOnSecondary': return '#ffffff';
		elif cssLabel == '--kcSecondaryContainer': return '#d5e4f6';
		elif cssLabel == '--kcOnSecondaryContainer': return '#0e1d2a';
		elif cssLabel == '--kcTertiary': return '#a04100';
		elif cssLabel == '--kcOnTertiary': return '#ffffff';
		elif cssLabel == '--kcTertiaryContainer': return '#ffdbcc';
		elif cssLabel == '--kcOnTertiaryContainer': return '#351000';
		elif cssLabel == '--kcError': return '#ba1a1a';
		elif cssLabel == '--kcErrorContainer': return '#ffdad6';
		elif cssLabel == '--kcOnError': return '#ffffff';
		elif cssLabel == '--kcOnErrorContainer': return '#410002';
		elif cssLabel == '--kcBackground': return '#fcfcff';
		elif cssLabel == '--kcOnBackground': return '#1a1c1e';
		elif cssLabel == '--kcSurface': return '#fcfcff';
		elif cssLabel == '--kcOnSurface': return '#1a1c1e';
		elif cssLabel == '--kcSurfaceVariant': return '#dee3eb';
		elif cssLabel == '--kcOnSurfaceVariant': return '#42474e';
		elif cssLabel == '--kcOutline': return '#72777f';
		elif cssLabel == '--kcInverseOnSurface': return '#f0f0f4';
		elif cssLabel == '--kcInverseSurface': return '#2f3033';
		elif cssLabel == '--kcInversePrimary': return '#95ccff';
		elif cssLabel == '--kcShadow': return '#000000';
		elif cssLabel == '--kcSurfaceTint': return '#00639a';
		elif cssLabel == '--kcOutlineVariant': return '#c2c7cf';
		elif cssLabel == '--kcScrim': return '#000000';
		elif cssLabel == '--kcGood': return '#00639a';
		elif cssLabel == '--kcGoodContainer': return '#cde5ff';
		elif cssLabel == '--kcOnGoodContainer': return '#001d32';
		elif cssLabel == '--kcOK': return '#f1b400';
		elif cssLabel == '--kcOKContainer': return '#ffdea0';
		elif cssLabel == '--kcOnOKContainer': return '#261a00';
		elif cssLabel == '--kcBad': return '#ba1a1a';
		elif cssLabel == '--kcBadContainer': return '#ffdad6';
		elif cssLabel == '--kcOnBadContainer': return '#410002';	
		
##########################################################################################
def getChartColors():
	'''
		Return a pre-defined array of colors

		Args:
			None
		returns:
			Array of color strings
			
		Updated:
			slr - 12/11/2023 6:41p Created
	'''
	#Found this one under kanoa.colors.getChartColors()
	#	return ["#117DBE", "#BF7611", "#BF11BF", "#4FBF11", "#2D536A", "#F16500", "#00DEF2", "#B5F200", "#A700F2", "#9D6034"]	
	#Found this one under kanoaScripts.custom.getChartColors()
	return ["#489fe2", "#0a369d", "#f96900", "#f7b801", "#a2aa8a", "#2b6088", "#06205e", "#fa8733", "#fad467", "#69714c"]