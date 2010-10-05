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

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.vm;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.ui.WlDeustoLogicBasedBoard;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.vm.ui.VMBoard;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class VMExperiment extends ExperimentBase {
	
	private final IConfigurationManager configurationManager;
	private final VMBoard board;
	
	public VMExperiment(IConfigurationManager configurationManager, IBoardBaseController boardController){
		this.configurationManager = configurationManager;
		this.board = new VMBoard(
					this.configurationManager,
					boardController
				);
	}

	@Override
	public BoardBase getUI() {
		return this.board;
	}	
}


