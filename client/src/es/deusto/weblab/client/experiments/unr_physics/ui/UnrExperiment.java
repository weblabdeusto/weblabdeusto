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

package es.deusto.weblab.client.experiments.unr_physics.ui;

import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;

public class UnrExperiment extends UIExperimentBase {

	public UnrExperiment(IConfigurationRetriever configurationRetriever,
			IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
	}

	@Override
	public boolean expectsPostEnd(){
		return true;
	}
	
	@Override
	public void postEnd(String initialData, String endData){
		this.boardController.stopPolling();
		putWidget(new Label("Redirecting to..." + initialData));
		Window.Location.replace(initialData);
	}
	
}
