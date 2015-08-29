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

package es.deusto.weblab.client.experiments.purejs;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Window.Location;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;

public class PureJSExperiment extends UIExperimentBase {
	
	private final String htmlFile;
	
	public PureJSExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
		
		String htmlFile;
		try {
			htmlFile = configurationRetriever.getProperty(PureJSCreatorFactory.HTML_FILE);
		} catch (Exception e) {
			putWidget(new Label("Experiment misconfigured. Add client parameter: " + PureJSCreatorFactory.HTML_FILE.getName()));
			htmlFile = null;
		}
		this.htmlFile = htmlFile;
	}
	
	@Override
	public void initialize() {
//		final SessionID sessionId = this.boardController.getSessionId();
//		redirectToHtml("session_id=" + sessionId.getRealId());
	}
	
	private void redirectToHtml(String hashInfo) {
		if (this.htmlFile == null) {
			putWidget(new Label("Experiment misconfigured. Add client parameter: " + PureJSCreatorFactory.HTML_FILE.getName()));
			return;
		}
		
		final String baseUrl = this.configurationRetriever.getProperty(PureJSCreatorFactory.BASE_URL);
		final String redirectionUrl = baseUrl + this.htmlFile + "#" + hashInfo; // TODO
		
		this.boardController.disableFinishOnClose();
		final Anchor anch = new Anchor(i18n.remoteSystem(), redirectionUrl);
		putWidget(anch);
		Location.replace(redirectionUrl);
	}
	
	@Override
	public JSONValue getInitialData() {
		final JSONObject object = new JSONObject();
		object.put("back", new JSONString(Location.getHref()));
		return object;
	}

	@Override
	public void start(final int time, String initialConfiguration){
//		final SessionID sessionId = this.boardController.getReservationId();
//		redirectToHtml("reservation_id=" + sessionId.getRealId());
	}
}
