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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pld.ui;

import com.google.gwt.core.client.GWT;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.ui.WlDeustoXilinxBasedBoard;

public class WlDeustoPldBasedBoard extends WlDeustoXilinxBasedBoard {

	public static final String PLD_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.pld.webcam.image.url";
	public static final String DEFAULT_PLD_WEBCAM_IMAGE_URL       = GWT.getModuleBaseURL() + "/waiting_url_image.jpg";
	
	public static final String PLD_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pld.webcam.refresh.millis";
	public static final int    DEFAULT_PLD_WEBCAM_REFRESH_TIME       = 400;
	
	public WlDeustoPldBasedBoard(IConfigurationRetriever configurationRetriever,
			IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
	}

	@Override
	protected String getWebcamImageUrl() {
		return this.configurationRetriever.getProperty(
				WlDeustoPldBasedBoard.PLD_WEBCAM_IMAGE_URL_PROPERTY, 
				WlDeustoPldBasedBoard.DEFAULT_PLD_WEBCAM_IMAGE_URL
			);
	}

	@Override
	protected int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
				WlDeustoPldBasedBoard.PLD_WEBCAM_REFRESH_TIME_PROPERTY, 
				WlDeustoPldBasedBoard.DEFAULT_PLD_WEBCAM_REFRESH_TIME
			);
	}
}
