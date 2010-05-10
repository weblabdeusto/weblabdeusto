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
package es.deusto.weblab.client.lab.ui.widgets;

import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class WlVerticalPanel extends VerticalPanel implements IWlWidget {
	
	public WlVerticalPanel(){
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
	
	
//	public void add(IWlWidget widget) {
//		Widget wid = widget.getWidget();
//		add((Widget) wid);
//	}
}
