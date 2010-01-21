/*
* Copyright (C) 2005-2009 University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.ui;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.controller.IWebLabController;
import es.deusto.weblab.client.exceptions.ui.themes.ThemeNotFoundException;
import es.deusto.weblab.client.exceptions.ui.themes.WlThemeException;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme.DefaultTheme;

public class ThemeFactory {
	public static ThemeBase themeFactory(IConfigurationManager configurationManager, IWebLabController controller, String themeName) throws WlThemeException{
		if(themeName.equals("deusto"))
			return new DefaultTheme(configurationManager, controller);
		else
			throw new ThemeNotFoundException("Theme " + themeName + " not found");
	}
}
