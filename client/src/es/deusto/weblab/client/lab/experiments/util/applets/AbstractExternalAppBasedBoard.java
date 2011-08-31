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
*         Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.lab.experiments.util.applets;

import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlTimer;

public abstract class AbstractExternalAppBasedBoard extends ExperimentBase {

	private static final int MAX_FACEBOOK_WIDTH = 710; // differs from WebClient.MAX_FACEBOOK_WIDTH taking into account the size of the whole page
	private static IConfigurationRetriever staticConfigurationRetriever;
	protected static IBoardBaseController staticBoardController;
	private final VerticalPanel panel;
	protected Label message;
	protected final HTML html;
	protected final int width;
	protected final int height;

	// To store the html footer which is optionally specified through the configuration
	// file and displayed on the bottom of the page.
	private final HTML pageFooter;
	private final VerticalPanel pageFooterPanel;
	
	// Whether to display the standard count-down timer or not.
	private final boolean displayStandardTimer;
	private final VerticalPanel standardTimerPanel;
	private final WlTimer standardTimer;
	
	public AbstractExternalAppBasedBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController, int width, int height) {
		super(configurationRetriever, boardController);
		
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
		
		AbstractExternalAppBasedBoard.staticBoardController      = boardController;
		AbstractExternalAppBasedBoard.staticConfigurationRetriever = configurationRetriever;
		AbstractExternalAppBasedBoard.exportStaticMethods();
		
		// If the following display flag is disabled, we will simply never show the panel with the timer.
		this.displayStandardTimer = configurationRetriever.getBoolProperty("page.timer", false);
		this.standardTimerPanel = new VerticalPanel();
		this.standardTimerPanel.setVisible(false);
		this.standardTimer = new WlTimer(false);
		this.standardTimerPanel.add(this.standardTimer);
		this.standardTimer.setStyleName("wl-time_remaining");
				
		this.pageFooterPanel = new VerticalPanel();
		this.pageFooter = new HTML(configurationRetriever.getProperty("page.footer", ""));
		this.pageFooterPanel.add(this.pageFooter);
		
		this.panel = new VerticalPanel();
		this.message = new Label();
		this.html = new HTML("<div/>");
		this.panel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.panel.add(this.standardTimerPanel);
		this.panel.add(this.html);
		this.panel.add(this.message);
		this.panel.add(this.pageFooterPanel);
	}
	
	
	/**
	 * This method is called automatically to set the time of an experiment. If enabled,
	 * we need to use that information to set up the timer. If this method is overriden,
	 * it will need to be called explicitly for the timer to work.
	 */
	@Override
	public void setTime(int time) {
		if(this.displayStandardTimer) {
			this.standardTimerPanel.setVisible(true);
			this.standardTimer.updateTime(time);
			this.standardTimer.start();
		}
	}
	
	/**
	 * Shows or hides the footer.
	 * @param show True to show, false to hide.
	 */
	public void showFooter(boolean show) {
		this.pageFooterPanel.setVisible(show);
	}

	@Override
	public Widget getWidget() {
		return this.panel;
	}
	
	static int getIntProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException{
		return AbstractExternalAppBasedBoard.staticConfigurationRetriever.getIntProperty(key);
	}

	static int getIntProperty(String key, int def) {
		return AbstractExternalAppBasedBoard.staticConfigurationRetriever.getIntProperty(key, def);
	}

	static String getProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException{
		return AbstractExternalAppBasedBoard.staticConfigurationRetriever.getProperty(key);
	}

	static String getProperty(String key, String def){
		return AbstractExternalAppBasedBoard.staticConfigurationRetriever.getProperty(key, def);
	}

	static void sendCommand(final String command, final int commandId){
		AbstractExternalAppBasedBoard.staticBoardController.sendCommand(new Command(){
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
		AbstractExternalAppBasedBoard.staticBoardController.clean();
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
