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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.fpga;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.fpga.ui.WlDeustoFpgaBasedBoard;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class WebLabFpgaExperiment extends ExperimentBase {
	private final IConfigurationRetriever configurationRetriever;
	private final WlDeustoFpgaBasedBoard board;
	
	public WebLabFpgaExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		this.configurationRetriever = configurationRetriever;
		this.board = new WlDeustoFpgaBasedBoard(
					this.configurationRetriever,
					boardController
				);
	}

	@Override
	public BoardBase getUI() {
		return this.board;
	}
}
