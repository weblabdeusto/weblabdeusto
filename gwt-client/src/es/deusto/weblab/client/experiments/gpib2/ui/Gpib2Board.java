/*
* Copyright (C) 2005 onwards University of Deusto
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
package es.deusto.weblab.client.experiments.gpib2.ui;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.experiments.gpib.ui.GpibExperiment;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;

public class Gpib2Board extends GpibExperiment {
	
	public static final String DEFAULT_GPIB2_WEBCAM_IMAGE_URL       = "http://gpib2.weblab.deusto.es/cliente/camview.jpg";
	
	public Gpib2Board(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);		
	}
		
	@Override
	protected String getDefaultWebcamImageUrl(){
		return Gpib2Board.DEFAULT_GPIB2_WEBCAM_IMAGE_URL;
	}
}