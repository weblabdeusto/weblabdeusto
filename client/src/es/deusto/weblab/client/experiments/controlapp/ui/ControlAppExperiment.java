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

package es.deusto.weblab.client.experiments.controlapp.ui;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.Window.Location;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;

public class ControlAppExperiment extends UIExperimentBase {
	
	public static final String LINK_PRESENTATION_PROPERTY_NAME = "link.presentation";
	public static final String EXTERNAL_WIDTH  = "external.width";
	public static final String EXTERNAL_HEIGHT = "external.height";
	
	public static final String DEFAULT_EXTERNAL_WIDTH  = "800";
	public static final String DEFAULT_EXTERNAL_HEIGHT = "1000";
	
	public static enum LinkPresentation {
		popup, iframe, redirection
	}
	
	public static final String DEFAULT_PRESENTATION_PROPERTY = LinkPresentation.popup.name();
	
	public ControlAppExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
	}
	
	public LinkPresentation getLinkPresentation() {
		final String linkPresentationStr = this.configurationRetriever.getProperty(LINK_PRESENTATION_PROPERTY_NAME, DEFAULT_PRESENTATION_PROPERTY);
		try{
			return LinkPresentation.valueOf(linkPresentationStr);
		} catch (IllegalArgumentException iae) {
			return LinkPresentation.valueOf(DEFAULT_PRESENTATION_PROPERTY);
		}
	}

	@Override
	public void start(int time, String initialConfiguration){
		final JSONObject value = JSONParser.parseStrict(initialConfiguration).isObject();
		final String url = value.get("url").isString().stringValue();
		System.out.println("Control app URL=" + url);
		
		final String width  = this.configurationRetriever.getProperty(EXTERNAL_WIDTH,  DEFAULT_EXTERNAL_WIDTH);
		final String height = this.configurationRetriever.getProperty(EXTERNAL_HEIGHT, DEFAULT_EXTERNAL_HEIGHT);
		
		switch(getLinkPresentation()) {
			case iframe:
				final HTML html = new HTML("<iframe src='" + url + "' width='" + width + "' height='" + height + "px' frameborder='0'/>");
				putWidget(html);
				break;
			case popup:
				final VerticalPanel vp = new VerticalPanel();
				final Button popupButton = new Button(i18n.remoteSystem());
				popupButton.addClickHandler(new ClickHandler() {
					
					@Override
					public void onClick(ClickEvent event) {
						Window.open(url, "_blank", "resizable=yes,scrollbars=yes,dependent=yes,width=" + width + ",height=" + height + ",top=0");
					}
				});
				vp.add(popupButton);
				putWidget(vp);
				break;
			case redirection:
				this.boardController.disableFinishOnClose();
				final Anchor anch = new Anchor(i18n.remoteSystem(), url);
				putWidget(anch);
				Location.replace(url);
				break;
		}
	}
}
