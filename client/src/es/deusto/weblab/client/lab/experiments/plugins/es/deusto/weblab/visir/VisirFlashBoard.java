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
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.visir;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.experiments.util.applets.flash.WebLabFlashAppBasedBoard;

public class VisirFlashBoard extends WebLabFlashAppBasedBoard {

	public VisirFlashBoard(IConfigurationManager configurationManager,
			IBoardBaseController boardController) {
		super(configurationManager, boardController, "visir/loader.swf", 800, 500,
				 "cookie=9b892c8784ea6119939a27b34102b1c14e37c156",
				 "Visir Flash Experiment", true);
	}
	
	@Override
	public void end() {
		super.end();
	}

	@Override
	public void initialize() {
		super.initialize();
	}

	@Override
	public void setTime(int time) {
		super.setTime(time);
	}

	@Override
	public void start() {
		super.start();
	}
}
