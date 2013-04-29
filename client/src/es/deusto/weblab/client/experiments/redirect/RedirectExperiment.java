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

package es.deusto.weblab.client.experiments.redirect;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.Window.Location;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;

public class RedirectExperiment extends UIExperimentBase {
	
	public static final String LINK_PRESENTATION_PROPERTY_NAME = "link.presentation";
	public static final String EXTERNAL_WIDTH  = "external.width";
	public static final String EXTERNAL_HEIGHT = "external.height";
	
	public static enum LinkPresentation {
		popup, iframe, redirection
	}
	
	public static final String DEFAULT_PRESENTATION_PROPERTY = LinkPresentation.redirection.name();
	
	public RedirectExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
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
	public JSONValue getInitialData() {
		final JSONObject object = new JSONObject();
		object.put("back", new JSONString(Location.getHref()));
		return object;
	}

	@Override
	public void start(final int time, String initialConfiguration){
		final JSONObject value = JSONParser.parseStrict(initialConfiguration).isObject();
		final String baseURL = value.get("url").isString().stringValue();
		System.out.println("Control app URL=" + baseURL);
		
		final String width  = this.configurationRetriever.getProperty(EXTERNAL_WIDTH,  "" + Window.getClientWidth());
		final String height = this.configurationRetriever.getProperty(EXTERNAL_HEIGHT, "" + Window.getClientHeight());
		
		final long startTime = System.currentTimeMillis();
		
		switch(getLinkPresentation()) {
			case iframe:
				final String iframeUrl = baseURL.replace("TIME_REMAINING", "" + time);
				final HTML html = new HTML("<iframe src='" + iframeUrl + "' width='" + width + "' height='" + height + "px' frameborder='0'/>");
				putWidget(html);
				break;
			case popup:
				final VerticalPanel vp = new VerticalPanel();
				final Button popupButton = new Button(i18n.remoteSystem());
				popupButton.addClickHandler(new ClickHandler() {
					
					@Override
					public void onClick(ClickEvent event) {
						final long now = System.currentTimeMillis();
						final long elapsed = now - startTime;
						final long nowTime = 1000 * time - elapsed;
						final String popupUrl = baseURL.replace("TIME_REMAINING", "" + (nowTime / 1000));
						
						Window.open(popupUrl, "_blank", "resizable=yes,scrollbars=yes,dependent=yes,width=" + width + ",height=" + height + ",top=0");
					}
				});
				vp.add(popupButton);
				putWidget(vp);
				break;
			case redirection:
				String redirectionUrl = baseURL.replace("TIME_REMAINING", "" + time);
				this.boardController.disableFinishOnClose();
				final Anchor anch = new Anchor(i18n.remoteSystem(), redirectionUrl);
				putWidget(anch);
				Location.replace(redirectionUrl);
				break;
		}
	}
}
