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

package es.deusto.weblab.client.experiments.util.applets.flash;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.experiments.ExperimentBase;
import es.deusto.weblab.client.ui.BoardBase;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;

public class FlashAppExperimentBase extends ExperimentBase {

	private final WebLabFlashAppBasedBoard board;

	public FlashAppExperimentBase(IConfigurationManager configurationManager, IBoardBaseController boardController, int width, int height, String swfFile, String message){
		this.board = new WebLabFlashAppBasedBoard(
					configurationManager,
					boardController, swfFile,
					width, height, message
				);
	}
	
	@Override
	public BoardBase getUI() {
		return this.board;
	}
}
