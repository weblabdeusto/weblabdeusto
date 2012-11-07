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
package es.deusto.weblab.client.experiments.binary.ui;

import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;

public class BinaryExperiment extends ExperimentBase {

	public BinaryExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		super(configurationRetriever, boardController);
	}
	@Override
	public void initialize(){	    	
	}
	
	@Override
	public void queued(){
	}

    @Override
    public void start(int time, String initialConfiguration) {

    }
	
	@Override
	public void end(){
	}
	
	@Override
	public void setTime(int time) {
	}
	
	@Override
	public Widget getWidget() {
		return null;
	}
}
