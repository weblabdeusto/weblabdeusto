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
* Author: FILLME
*
*/

package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.SimplePanel;

public class WlAHref extends SimplePanel {
	
	private final Element element;
	
    public WlAHref() {
        super(DOM.createAnchor());
        this.element = getElement();
    }

    public void setHref(String href) {
        this.element.setAttribute("href", href);
    }

    public String getHref() {
    	return this.element.getAttribute("href");
    }

    public void setTarget(String target) {
        this.element.setAttribute("target", target);
    }
    
    public String getTarget() {
        return this.element.getAttribute("target");
    }
}
