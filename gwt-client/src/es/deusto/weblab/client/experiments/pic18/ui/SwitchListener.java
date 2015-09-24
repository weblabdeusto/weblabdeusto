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
import es.deusto.weblab.client.experiments.xilinx.commands.SwitchCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.IWlWidget;
import es.deusto.weblab.client.ui.widgets.WlSwitch;

class SwitchListener implements IWlActionListener{

	private final int n;
	private final IBoardBaseController commandSender;
	private final IResponseCommandCallback commandCallback;
	
	public SwitchListener(int n, IBoardBaseController commandSender, IResponseCommandCallback commandCallback){
		this.n = n;
		this.commandSender = commandSender;
		this.commandCallback = commandCallback;
	}
	
	@Override
	public void onAction(IWlWidget widget) {
		final WlSwitch wlswitch = (WlSwitch)widget;
		final Command command = new SwitchCommand(this.n, wlswitch.isSwitched());
		this.commandSender.sendCommand(command, this.commandCallback);
	}
}
