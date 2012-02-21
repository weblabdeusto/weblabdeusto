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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
* 		  
*/ 
package es.deusto.weblab.client.experiments.ilab_batch.ui;

import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationException;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;

public class ILabBatchExperiment extends ExperimentBase {

	// Root panel.
	private final VerticalPanel widget;
	private final HTML html;
		
	public ILabBatchExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		this.widget = new VerticalPanel();
		this.widget.setWidth("100%");
		this.html = new HTML("<div width=\"100%\"/>");
		this.widget.add(this.html);
	}

	/**
	 * The initialize function gets called on the "reserve" stage,
	 * before the experiment starts.
	 */
	@Override
	public void initialize(){
		try{
			final String archive       = this.configurationRetriever.getProperty("archive");
			final String code          = this.configurationRetriever.getProperty("code");
			final String labServerId   = this.configurationRetriever.getProperty("lab_server_id");
			final String serviceBroker = this.configurationRetriever.getProperty("service_broker", "/weblab/web/ilab/");
			
			createJavaScriptCode(this.html.getElement(), archive, code, 1, 1, serviceBroker, labServerId);
		}catch(ConfigurationException ce){
			this.html.setHTML("Error in configuration: " + ce.getMessage());
		}
	}	
	
    private static native void createJavaScriptCode(Element element, String archive, String code, int width, int height, String serviceBroker, String labServerId) /*-{
		element.innerHTML = "<div width=\"100%\"><center>This laboratory is managed by a Java applet that will pop up.</center></div><br/>" +
	    	"<applet archive='" + archive + "' " + 
	    		"code='" + code + "' " + 
	    		"width='" + width + "' " +  
	    		"MAYSCRIPT " + 
	    		"height='" + height + "' " +
	    		"> " +
	    		"<PARAM NAME=\"serviceURL\" VALUE=\"" + serviceBroker + "\">" +
	    		"<PARAM NAME=\"labServerID\" VALUE=\"" + labServerId + "\">" +
	    		"<PARAM NAME=\"initial_focus\" VALUE=\"false\">" +
	    		"<noapplet><b>Your web browser does not support Java applets</b></noapplet>" +
	    	"</applet>" +
	    	"";
	}-*/;
	
	@Override
	public Widget getWidget(){
		return this.widget;
	}
}
