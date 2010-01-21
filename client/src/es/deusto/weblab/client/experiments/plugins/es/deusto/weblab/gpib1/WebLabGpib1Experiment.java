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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib1;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib.WebLabGpibExperiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib.ui.WlDeustoGpibBoard;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib1.ui.WlDeustoGpib1Board;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;

public class WebLabGpib1Experiment extends WebLabGpibExperiment {

	public WebLabGpib1Experiment(IConfigurationManager configurationManager, IBoardBaseController boardController) {
		super(configurationManager, boardController);
	}

	@Override
	protected WlDeustoGpibBoard createGpibBoard(IConfigurationManager configurationManager, IBoardBaseController boardController){
		return new WlDeustoGpib1Board(configurationManager, boardController);
	}
}
