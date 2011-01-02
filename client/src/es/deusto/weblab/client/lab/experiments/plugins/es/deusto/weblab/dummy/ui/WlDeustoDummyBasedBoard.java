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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.dummy.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.ui.WlDeustoXilinxBasedBoard;

public class WlDeustoDummyBasedBoard extends WlDeustoXilinxBasedBoard {

	public static final String DUMMY_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.dummy.webcam.image.url";
	public static final String DEFAULT_DUMMY_WEBCAM_IMAGE_URL       = "http://fpga.weblab.deusto.es/webcam/fpga0/image.jpg";
	
	public static final String DUMMY_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pld.webcam.refresh.millis";
	public static final int    DEFAULT_DUMMY_WEBCAM_REFRESH_TIME       = 400;
	
	private final Label messages;
	
	public WlDeustoDummyBasedBoard(IConfigurationRetriever configurationRetriever,
			IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
		this.messages = new Label("messages here");
	}
	
	@Override
	public void start(){
	    super.start();
	    this.verticalPanel.add(this.messages);
	}

	@Override
	protected IResponseCommandCallback getResponseCommandCallback(){
	    return new IResponseCommandCallback(){

		@Override
		public void onSuccess(ResponseCommand responseCommand) {
		    GWT.log("vuelta a onSuccess de ResponseCommandCallback", null);
		    WlDeustoDummyBasedBoard.this.processCommandSent(responseCommand);
		}

		@Override
		public void onFailure(WlCommException e) {
		}
	    };
	}
	
	private void processCommandSent(ResponseCommand responseCommand) {
		if(!responseCommand.isEmpty())
			this.messages.setText("Response command: " + responseCommand.getCommandString());
		else
			this.messages.setText("Response command: empty");
	}
}
