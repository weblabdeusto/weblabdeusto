/*
* Copyright (C) 2005 onwards University of Deusto
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

package es.deusto.weblab.client.lab.experiments.util.applets.java;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Element;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard;

public class JavaAppletsExperiment extends AbstractExternalAppBasedBoard{

    public JavaAppletsExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController,
    		String archive,
    		String code,
    		int width,
    		int height,
    		String message
    ) {
    	super(configurationRetriever, boardController, width, height);
    	
    	this.message.setText(message);

    	JavaAppletsExperiment.createJavaScriptCode(this.html.getElement(), GWT.getModuleBaseURL() + archive, code, this.width, this.height);
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
    	
    	// Call required for the standard timer to work properly, if it is enabled.
    	super.setTime(time);
    	
    	AbstractExternalAppBasedBoard.setTimeImpl(time);
    }

    @Override
    public void start(int time, String initialConfiguration) {
    	AbstractExternalAppBasedBoard.startInteractionImpl();
    }

    @Override
    public void end() {
    	AbstractExternalAppBasedBoard.endImpl();
    }
}
