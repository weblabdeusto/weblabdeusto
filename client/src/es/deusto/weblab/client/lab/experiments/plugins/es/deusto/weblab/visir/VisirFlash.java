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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.visir;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class VisirFlash extends ExperimentBase {

	private final VisirFlashBoard board;
	
	public VisirFlash(IConfigurationManager configurationManager,
			IBoardBaseController boardController)
	{
		this.board = new VisirFlashBoard(configurationManager, boardController);
	}

	@Override
	public BoardBase getUI() {
		return this.board;
	}

}
