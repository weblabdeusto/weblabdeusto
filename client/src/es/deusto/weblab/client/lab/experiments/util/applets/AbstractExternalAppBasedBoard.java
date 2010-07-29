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

package es.deusto.weblab.client.lab.experiments.util.applets;

import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.ui.BoardBase;

public abstract class AbstractExternalAppBasedBoard extends BoardBase {

	private static IConfigurationManager configurationManager;
	protected static IBoardBaseController boardController;
	private final VerticalPanel panel;
	protected Label message;
	protected final HTML html;

	public AbstractExternalAppBasedBoard(IConfigurationManager configurationManager, IBoardBaseController boardController) {
		super(boardController);
		
		AbstractExternalAppBasedBoard.boardController      = boardController;
		AbstractExternalAppBasedBoard.configurationManager = configurationManager;
		AbstractExternalAppBasedBoard.exportStaticMethods();
		
		this.panel = new VerticalPanel();
		this.message = new Label();
		this.html = new HTML("<div/>");
		this.panel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.panel.add(this.html);
		this.panel.add(this.message);
	}

	@Override
	public Widget getWidget() {
		return this.panel;
	}
	
	static int getIntProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException{
		return AbstractExternalAppBasedBoard.configurationManager.getIntProperty(key);
	}

	static int getIntProperty(String key, int def) {
		return AbstractExternalAppBasedBoard.configurationManager.getIntProperty(key, def);
	}

	static String getProperty(String key) throws ConfigurationKeyNotFoundException{
		return AbstractExternalAppBasedBoard.configurationManager.getProperty(key);
	}

	static String getProperty(String key, String def){
		return AbstractExternalAppBasedBoard.configurationManager.getProperty(key, def);
	}

	static void sendCommand(final String command, final int commandId){
		AbstractExternalAppBasedBoard.boardController.sendCommand(new Command(){
			@Override
			public String getCommandString() {
				return command;
			}
		}, new IResponseCommandCallback(){
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				AbstractExternalAppBasedBoard.handleCommandResponse(responseCommand.getCommandString(), commandId);
			}
			@Override
			public void onFailure(WlCommException e) {
				AbstractExternalAppBasedBoard.handleCommandError(e.getMessage(), commandId);
			}
		});
	}
	
	private static native void exportStaticMethods() /*-{
		$wnd.wl_getIntProperty    = @es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard::getIntProperty(Ljava/lang/String;);
		$wnd.wl_getIntPropertyDef = @es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard::getIntProperty(Ljava/lang/String;I);
		$wnd.wl_getProperty       = @es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard::getProperty(Ljava/lang/String;);
		$wnd.wl_getPropertyDef    = @es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard::getProperty(Ljava/lang/String;Ljava/lang/String;);
	
		$wnd.wl_sendCommand       = @es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard::sendCommand(Ljava/lang/String;I);
		$wnd.wl_onClean           = @es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard::onClean();
	}-*/;	

	static void onClean(){
		AbstractExternalAppBasedBoard.boardController.onClean();
	}
	
	protected static native void handleCommandResponse(String msg, int commandId) /*-{
		$wnd.wl_inst.handleCommandResponse(msg, commandId);
	}-*/;
	
	protected static native void handleCommandError(String msg, int commandId) /*-{
		$wnd.wl_inst.handleCommandError(msg, commandId);
	}-*/;
	
	protected static native void setTimeImpl(int time) /*-{
		$wnd.wl_inst.setTime(time);
	}-*/;
	
	protected static native void startInteractionImpl() /*-{
		$wnd.wl_inst.startInteraction();
	}-*/;
	
	protected static native void endImpl() /*-{
		$wnd.wl_inst.end();
	}-*/;
}
