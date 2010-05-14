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

package es.deusto.weblab.client.lab.experiments.util.applets.flash;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class FlashAppExperimentBase extends ExperimentBase {

	private final WebLabFlashAppBasedBoard board;

	/**
	 * Constructs a WeblabFlashAppBasedBoard. The flash applet is placed on the
	 * website immediately.
	 * 
	 * @param configurationManager Reference to the configuration manager.
	 * @param boardController Reference to the board controller.
	 * @param swfFile The path to the SWF file, including its name.
	 * @param width Width of the flash app.
	 * @param height Height of the flash app.
	 * @param flashvars String which will be passed to the flash app as its
	 * flashvars parameters.
	 * @param message Message to display.
	 */
	public FlashAppExperimentBase(IConfigurationManager configurationManager, IBoardBaseController boardController, int width, int height, String swfFile, String flashvars, String message){
		this.board = new WebLabFlashAppBasedBoard(
					configurationManager,
					boardController, swfFile,
					width, height, flashvars, message
				);
	}
	
	/**
	 * Constructs a FlashAppExperimentBase. If deferFlashApp is set to true,
	 * the flash applet is not placed on the website until the experiment is
	 * started and hence the start() method is called.
	 * 
	 * @param configurationManager Reference to the configuration manager.
	 * @param boardController Reference to the board controller.
	 * @param swfFile The path to the SWF file, including its name.
	 * @param width Width of the flash app.
	 * @param height Height of the flash app.
	 * @param flashvars String which will be passed to the flash app as its
	 * flashvars parameters.
	 * @param message Message to display.
	 * @param deferFlashApp If true, the flash applet won't be placed until
	 * the experiment starts.
	 */
	public FlashAppExperimentBase(IConfigurationManager configurationManager, 
			IBoardBaseController boardController, int width, int height, 
			String swfFile, String flashvars, String message, 
			boolean deferFlashApp){
		this.board = new WebLabFlashAppBasedBoard(
					configurationManager,
					boardController, swfFile,
					width, height, flashvars, message, deferFlashApp
				);
	}
	
	@Override
	public BoardBase getUI() {
		return this.board;
	}
}
