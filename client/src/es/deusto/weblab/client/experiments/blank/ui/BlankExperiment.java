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
* Author: FILLME
*
*/

package es.deusto.weblab.client.experiments.blank.ui;

import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;

public class BlankExperiment extends ExperimentBase {

	private VerticalPanel vpanel = new VerticalPanel();
	
	public BlankExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		super(configurationRetriever, boardController);
		
	}
	
	@Override
	public void initialize() {
		final String html = this.configurationRetriever.getProperty("html", "");
		this.vpanel.add(new HTML(html));
	}
	
	
	@Override
	public Widget getWidget() {
		return this.vpanel;
	}

}
