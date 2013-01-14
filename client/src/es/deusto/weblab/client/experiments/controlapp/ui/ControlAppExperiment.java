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

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.user.client.ui.HTML;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;

public class ControlAppExperiment extends UIExperimentBase {
	
	public ControlAppExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
	}

	@Override
	public void start(int time, String initialConfiguration){
		final JSONObject value = JSONParser.parseStrict(initialConfiguration).isObject();
		final String url = value.get("url").isString().stringValue();
		System.out.println("Control app URL=" + url);
		final HTML html = new HTML("<iframe src='" + url + "' width='100%' height='800px' frameborder='0'/>");
		putWidget(html);
	}
}
