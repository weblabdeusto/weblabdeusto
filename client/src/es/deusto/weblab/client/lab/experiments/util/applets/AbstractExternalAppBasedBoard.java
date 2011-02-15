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

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.ui.BoardBase;

public abstract class AbstractExternalAppBasedBoard extends BoardBase {

	private static final int MAX_FACEBOOK_WIDTH = WebLabClient.MAX_FACEBOOK_WIDTH;
	private static IConfigurationRetriever configurationRetriever;
	protected static IBoardBaseController boardController;
	private final VerticalPanel panel;
	protected Label message;
	protected final HTML html;
	protected final int width;
	protected final int height;

	public AbstractExternalAppBasedBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController, int width, int height) {
		super(boardController);
		
		if(boardController.isFacebook()){
			if(width > MAX_FACEBOOK_WIDTH){
				this.width  = MAX_FACEBOOK_WIDTH;
				final float scale = 1.0f * MAX_FACEBOOK_WIDTH / width;
				this.height = Math.round(scale * height);
			}else{
				this.width  = width;
				this.height = height;
			}
		}else{
			this.width  = width;
			this.height = height;
		}
		
		AbstractExternalAppBasedBoard.boardController      = boardController;
		AbstractExternalAppBasedBoard.configurationRetriever = configurationRetriever;
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
		return AbstractExternalAppBasedBoard.configurationRetriever.getIntProperty(key);
	}

	static int getIntProperty(String key, int def) {
		return AbstractExternalAppBasedBoard.configurationRetriever.getIntProperty(key, def);
	}

	static String getProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException{
		return AbstractExternalAppBasedBoard.configurationRetriever.getProperty(key);
	}

	static String getProperty(String key, String def){
		return AbstractExternalAppBasedBoard.configurationRetriever.getProperty(key, def);
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
