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

package es.deusto.weblab.client.experiments.util.applets.java;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Element;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.experiments.util.applets.AbstractExternalAppBasedBoard;

public class WebLabJavaAppletsBasedBoard extends AbstractExternalAppBasedBoard{

    public WebLabJavaAppletsBasedBoard(IConfigurationManager configurationManager, IBoardBaseController boardController,
    		String archive,
    		String code,
    		int appletWidth,
    		int appletHeight,
    		String message
    ) {
    	super(configurationManager, boardController);
    	
    	this.message.setText(message);

    	WebLabJavaAppletsBasedBoard.createJavaScriptCode(this.html.getElement(), GWT.getModuleBaseURL() + archive, code, appletWidth, appletHeight);
    }

    private static native void createJavaScriptCode(Element element, String archive, String code, int width, int height) /*-{
    	element.innerHTML = "" +
        	"<applet archive='" + archive + "' " + 
        		"code='" + code + "' " + 
        		"width='" + width + "' " +  
        		"MAYSCRIPT " + 
        		"height='" + height + "' " +
        		"> " +
        	"</applet>" +
        	"";
		$wnd.wl_inst = element.getElementsByTagName('applet')[0];
    }-*/;

    @Override
    public void setTime(int time) {
    	AbstractExternalAppBasedBoard.setTimeImpl(time);
    }

    @Override
    public void start() {
    	AbstractExternalAppBasedBoard.startInteractionImpl();
    }

    @Override
    public void end() {
    	AbstractExternalAppBasedBoard.endImpl();
    }
}
