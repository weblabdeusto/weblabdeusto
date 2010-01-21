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
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.dummy;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.experiments.ExperimentBase;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.dummy.ui.WlDeustoDummyBasedBoard;
import es.deusto.weblab.client.ui.BoardBase;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;

public class WebLabDummyExperiment extends ExperimentBase {
	private final IConfigurationManager configurationManager;
	private final WlDeustoDummyBasedBoard board;
	
	public WebLabDummyExperiment(IConfigurationManager configurationManager, IBoardBaseController boardController){
		this.configurationManager = configurationManager;
		this.board = new WlDeustoDummyBasedBoard(
					this.configurationManager,
					boardController
				);
	}

	@Override
	public BoardBase getUI() {
		return this.board;
	}
}
