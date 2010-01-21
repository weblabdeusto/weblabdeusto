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
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.experiments.ExperimentBase;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib.ui.WlDeustoGpibBoard;
import es.deusto.weblab.client.ui.BoardBase;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;

public class WebLabGpibExperiment extends ExperimentBase {

	private final IConfigurationManager configurationManager;
	private final WlDeustoGpibBoard board;
	
	public WebLabGpibExperiment(IConfigurationManager configurationManager, IBoardBaseController boardController) {
		this.configurationManager = configurationManager;
		this.board = this.createGpibBoard(
				this.configurationManager,
				boardController
			);
	}
	
	protected WlDeustoGpibBoard createGpibBoard(IConfigurationManager configurationManager, IBoardBaseController boardController){
		return new WlDeustoGpibBoard(configurationManager, boardController);
	}

	@Override
	public BoardBase getUI() {
		return this.board;
	}

}
