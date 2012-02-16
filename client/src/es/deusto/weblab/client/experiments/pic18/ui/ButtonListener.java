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
package es.deusto.weblab.client.experiments.pic18.ui;

import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.experiments.xilinx.commands.PulseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlButton.IWlButtonUsed;

class ButtonListener implements IWlButtonUsed {
	
	private final int n;
	private final IBoardBaseController commandSender;
	private final IResponseCommandCallback commandCallback;
	
	public ButtonListener(int n, IBoardBaseController commandSender, IResponseCommandCallback commandCallback){
		this.n = n;
		this.commandSender = commandSender;
		this.commandCallback = commandCallback;
	}

	@Override
	public void onPressed() {
		final Command command = new PulseCommand(this.n, true); 
		this.commandSender.sendCommand(command, this.commandCallback);
	}

	@Override
	public void onReleased() {
		final Command command = new PulseCommand(this.n, false); 
		this.commandSender.sendCommand(command, this.commandCallback);
	}
}
