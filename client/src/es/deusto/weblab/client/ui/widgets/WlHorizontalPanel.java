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
package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Widget;

public class WlHorizontalPanel extends HorizontalPanel implements IWlWidget {
	
	public WlHorizontalPanel(){
		super();
		this.setBorderWidth(0); // set a border with when designing layout
	}
	
	@Override
	public Widget getWidget(){
		return this;
	}

	@Override
	public void dispose() {	    
	}
}
