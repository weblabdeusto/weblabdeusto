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
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.pic.ui;

import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.pic.commands.PulseCommand;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlTimedButton;
import es.deusto.weblab.client.ui.widgets.WlButton.IWlButtonUsed;

class ButtonListener implements IWlButtonUsed{
	private final int n;
	private final WlTimedButton button;
	private final IBoardBaseController commandSender;
	
	public ButtonListener(int n, WlTimedButton button, IBoardBaseController commandSender){
		this.n = n;
		this.button = button;
		this.commandSender = commandSender;
	}

	public void onPressed() {
		final Command command = new PulseCommand(this.n, this.button.getTime());
		this.commandSender.sendCommand(command);
	}

	public void onReleased() {
		final Command command = new PulseCommand(this.n, this.button.getTime());
		this.commandSender.sendCommand(command);
	}
}
