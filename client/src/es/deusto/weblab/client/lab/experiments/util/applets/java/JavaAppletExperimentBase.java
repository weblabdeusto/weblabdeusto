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

package es.deusto.weblab.client.lab.experiments.util.applets.java;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class JavaAppletExperimentBase extends ExperimentBase {

	private final WebLabJavaAppletsBasedBoard board;
	
	public JavaAppletExperimentBase(IConfigurationManager configurationManager, IBoardBaseController boardController, int width, int height, String archive, String code, String message){
		this.board = new WebLabJavaAppletsBasedBoard(
					configurationManager,
					boardController,
					archive, code,
					width, height, message
				);
	}

	
	@Override
	public BoardBase getUI() {
		return this.board;
	}

}
