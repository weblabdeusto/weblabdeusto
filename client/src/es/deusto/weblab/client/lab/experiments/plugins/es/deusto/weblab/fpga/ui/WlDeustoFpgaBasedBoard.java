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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.fpga.ui;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.ui.WlDeustoXilinxBasedBoard;

public class WlDeustoFpgaBasedBoard extends WlDeustoXilinxBasedBoard {

	public static final String FPGA_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.fpga.webcam.image.url";
	public static final String DEFAULT_FPGA_WEBCAM_IMAGE_URL       = "https://www.weblab.deusto.es/webcam/fpga0/image.jpg";
	
	public static final String FPGA_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pld.webcam.refresh.millis";
	public static final int    DEFAULT_FPGA_WEBCAM_REFRESH_TIME       = 400;
	
	public WlDeustoFpgaBasedBoard(IConfigurationRetriever configurationRetriever,
			IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
	}

	@Override
	protected String getWebcamImageUrl() {
		return this.configurationRetriever.getProperty(
				WlDeustoFpgaBasedBoard.FPGA_WEBCAM_IMAGE_URL_PROPERTY, 
				WlDeustoFpgaBasedBoard.DEFAULT_FPGA_WEBCAM_IMAGE_URL
			);
	}

	@Override
	protected int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
				WlDeustoFpgaBasedBoard.FPGA_WEBCAM_REFRESH_TIME_PROPERTY, 
				WlDeustoFpgaBasedBoard.DEFAULT_FPGA_WEBCAM_REFRESH_TIME
			);
	}
}
