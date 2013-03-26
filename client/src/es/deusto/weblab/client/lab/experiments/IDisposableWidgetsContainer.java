/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.lab.experiments;

import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;

public interface IDisposableWidgetsContainer {
	public IWlDisposableWidget [] getDisposableWidgets();
	public Widget asGwtWidget(); // return this;
}
