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
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.xilinx.ui;

import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.UploadStructure;
import es.deusto.weblab.client.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.exceptions.comm.WlCommException;
import es.deusto.weblab.client.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.WlClockActivator;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlTimedButton;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlButton.IWlButtonUsed;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public abstract class WlDeustoXilinxBasedBoard extends BoardBase{

	
	 /******************
	 * UIBINDER RELATED
	 ******************/
	
	interface WlDeustoXilinxBasedBoardUiBinder extends UiBinder<Widget, WlDeustoXilinxBasedBoard> {
	}

	private static final WlDeustoXilinxBasedBoardUiBinder uiBinder = GWT.create(WlDeustoXilinxBasedBoardUiBinder.class);
	
	
	public static class Style{
		public static final String TIME_REMAINING         = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL = "wl-clock_activation_panel"; 
	}
	
	protected IConfigurationManager configurationManager;

	protected static final boolean DEBUG_ENABLED = false;
	
	@UiField public VerticalPanel verticalPanel;
	@UiField VerticalPanel widget;
	@UiField VerticalPanel innerVerticalPanel;
	@UiField HorizontalPanel uploadStructurePanel;
	
	@UiField Label selectProgram;
	
	@UiField WlWaitingLabel messages;
	@UiField WlClockActivator clockActivator;

	@UiField HorizontalPanel switchesRow;
	@UiField HorizontalPanel buttonsRow;
	
	//@UiField(provided=true)
	private UploadStructure uploadStructure;
	
	@UiField(provided = true) 
	WlWebcam webcam;
	
	@UiField(provided = true)
	WlTimer timer;

	private final Vector<Widget> interactiveWidgets;
	
	protected abstract int getWebcamRefreshingTime();
	protected abstract String getWebcamImageUrl();
	

	
	public WlDeustoXilinxBasedBoard(IConfigurationManager configurationManager, IBoardBaseController boardController){
		super(boardController);
		
		this.configurationManager = configurationManager;
		
		this.interactiveWidgets = new Vector<Widget>();
		
		this.createProvidedWidgets();
		
		uiBinder.createAndBindUi(this);

		this.findInteractiveWidgets();
		
		this.disableInteractiveWidgets();
	}
	
	/**
	 * Will find those interactive widgets that are defined on UiBinder
	 * and add them to the interactive widgets array, so that they can
	 * be disabled. This isn't too convenient but currently there doesn't 
	 * seem to be any other way around. That may change in the future.
	 */
	private void findInteractiveWidgets() {
		
		// Find switches
		for(int i = 0; i < this.switchesRow.getWidgetCount(); ++i){
			final Widget wid = this.switchesRow.getWidget(i);
			if(wid instanceof WlSwitch) {
				final WlSwitch swi = (WlSwitch)wid;
				this.addInteractiveWidget(swi);
			}
		}
		
		// Find timed buttons
		for(int i = 0; i < this.buttonsRow.getWidgetCount(); ++i) {
			final Widget wid = this.buttonsRow.getWidget(i);
			if(wid instanceof WlTimedButton) {
				final WlTimedButton swi = (WlTimedButton)wid;
				this.addInteractiveWidget(swi);
			}
		}
		
	}
	
	/**
	 * Creates those widgets that are specified in the UiBinder xml
	 * file but which are marked as provided because they can't be
	 * allocated using the default ctor.
	 */
	private void createProvidedWidgets() {
		this.webcam = new WlWebcam(
				this.getWebcamRefreshingTime(),
				this.getWebcamImageUrl()
			);
		
		this.timer = new WlTimer(false);
		
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			public void onFinished() {
				WlDeustoXilinxBasedBoard.this.boardController.onClean();
			}
		});
		
		this.uploadStructure = new UploadStructure();
		this.uploadStructure.setFileInfo("program");
	}
	
	@Override
	public void initialize(){
		
		// Doesn't seem to work from UiBinder.
		this.uploadStructurePanel.add(this.uploadStructure.getFormPanel());
	
		this.webcam.setVisible(false);
		
	}
	
	@Override
	public void queued(){
	    this.widget.setVisible(false);
	    this.selectProgram.setVisible(false);
	}

	@Override
	public void start(){
	    this.widget.setVisible(true);
	    this.selectProgram.setVisible(false);
	    
		this.loadWidgets();
		this.disableInteractiveWidgets();
		
		this.uploadStructure.getFormPanel().setVisible(false);
		
		this.boardController.sendFile(this.uploadStructure, new IResponseCommandCallback() {
		    
		    @Override
		    public void onSuccess(ResponseCommand response) {
				WlDeustoXilinxBasedBoard.this.enableInteractiveWidgets();
				WlDeustoXilinxBasedBoard.this.messages.setText("Device ready");
				WlDeustoXilinxBasedBoard.this.messages.stop();
		    }

		    @Override
		    public void onFailure(WlCommException e) {
		    	
			    if(DEBUG_ENABLED)
			    	WlDeustoXilinxBasedBoard.this.enableInteractiveWidgets();
			    
		    	WlDeustoXilinxBasedBoard.this.messages.stop();
					
				WlDeustoXilinxBasedBoard.this.messages.setText("Error sending file: " + e.getMessage());
			    
		    }
		});
	}
	
	private void loadWidgets() {
		
		this.webcam.setVisible(true);
		this.webcam.start();
		
		this.timer.start();
		
		this.messages.setText("Programming device");
		this.messages.start();
		
		final ClockActivationListener clockActivationListener = new ClockActivationListener(this.boardController, this.getResponseCommandCallback());
		this.clockActivator.addClockActivationListener(clockActivationListener);
		
		this.addInteractiveWidget(this.timer.getWidget());
		this.addInteractiveWidget(this.clockActivator);
		
		this.prepareSwitchesRow();
		this.prepareButtonsRow();
		
		this.innerVerticalPanel.setSpacing(20);
	}
	
	private void addInteractiveWidget(Widget widget){
		this.interactiveWidgets.add(widget);
	}
	
	private void enableInteractiveWidgets(){
		for(int i = 0; i < this.interactiveWidgets.size(); ++i)
			this.interactiveWidgets.get(i).setVisible(true);		
	}
	
	private void disableInteractiveWidgets(){
		for(int i = 0; i < this.interactiveWidgets.size(); ++i)
			this.interactiveWidgets.get(i).setVisible(false);
	}
	
	/* Iterates through every switch in the switchesRow panel,
	 * setting up a listener for each of them. Switches found on it
	 * are defined anonymously on UiBinder, along with their title.
	 * This title is currently used as an integral identifier.
	 */
	private HorizontalPanel prepareSwitchesRow() {
		
		for(int i = 0; i < this.switchesRow.getWidgetCount(); ++i){
			final Widget wid = this.switchesRow.getWidget(i);
			if(wid instanceof WlSwitch) {
				final WlSwitch swi = (WlSwitch)wid;
				
				// Avoid trying to convert non-numerical titles (which serve
				// as identifiers). Not exactly an elegant way to do it.
				if(swi.getTitle().length() != 1) 
					continue;
				
				final int id = Integer.parseInt(swi.getTitle());
				final IWlActionListener actionListener = new SwitchListener(id, this.boardController, this.getResponseCommandCallback());
				swi.addActionListener(actionListener);
				this.addInteractiveWidget(swi);
			}
		}
		
		return this.switchesRow;
	}

	/*
	 * Iterates through every timed button in the buttonsRow panel,
	 * setting up a listener for each of them. Buttons found on it
	 * are defined anonymously on UiBinder, along with their title.
	 * This title is currently used as an integral identifier.
	 */
	private HorizontalPanel prepareButtonsRow() {

		for(int i = 0; i < this.buttonsRow.getWidgetCount(); ++i) {
			final Widget wid = this.buttonsRow.getWidget(i);
			if(wid instanceof WlTimedButton) {
				final WlTimedButton timedButton = (WlTimedButton)wid;
				
				if(timedButton.getTitle().length() != 1)
					continue;
				
				final int id = Integer.parseInt(timedButton.getTitle());
				final IWlButtonUsed buttonUsed = 
					new ButtonListener(id, this.boardController, this.getResponseCommandCallback());
				timedButton.addButtonListener(buttonUsed);
				this.addInteractiveWidget(timedButton);
			}
		}
		
		return this.buttonsRow;
	}

	@Override
	public void end(){
		if(this.webcam != null){
			this.webcam.dispose();
			this.webcam = null;
		}
		
		if(this.timer != null){
			this.timer.dispose();
			this.timer = null;
		}
		
		if(this.clockActivator != null){
			this.clockActivator.dispose();
			this.clockActivator = null;
		}
		
		for(int i = 0; i < this.switchesRow.getWidgetCount(); ++i) {
			final Widget wid = this.switchesRow.getWidget(i);
			if(wid instanceof WlSwitch)
				((WlSwitch)wid).dispose();
		}
		
		for(int i = 0; i < this.buttonsRow.getWidgetCount(); ++i) {
			final Widget wid = this.buttonsRow.getWidget(i);
			if(wid instanceof WlTimedButton)
				((WlTimedButton)wid).dispose();
		}
		
		this.messages.stop();
	}
	
	@Override
	public void setTime(int time) {
		this.timer.updateTime(time);
	}
	
	@Override
	public Widget getWidget() {
		return this.widget;
	}
	
	protected IResponseCommandCallback getResponseCommandCallback(){
	    return new IResponseCommandCallback(){
		    public void onSuccess(ResponseCommand responseCommand) {
			GWT.log("responseCommand: success", null);
		    }

		    public void onFailure(WlCommException e) {
			GWT.log("responseCommand: failure", null);
		    }
		};	    
	}
}
