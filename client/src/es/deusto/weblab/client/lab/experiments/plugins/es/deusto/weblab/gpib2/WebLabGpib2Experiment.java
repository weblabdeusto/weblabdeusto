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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib2;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib.WebLabGpibExperiment;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib.ui.WlDeustoGpibBoard;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib2.ui.WlDeustoGpib2Board;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class WebLabGpib2Experiment extends WebLabGpibExperiment {

	public WebLabGpib2Experiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
	}

	@Override
	protected WlDeustoGpibBoard createGpibBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		return new WlDeustoGpib2Board(configurationRetriever, boardController);
	}
}
