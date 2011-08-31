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
package es.deusto.weblab.client.experiments.pic.ui;

import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.commands.RequestWebcamCommand;
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.WlPotentiometer;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlTextBoxWithButton;
import es.deusto.weblab.client.ui.widgets.WlTimedButton;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class PicExperiment extends ExperimentBase{
	
	
	 /******************
	 * UIBINDER RELATED
	 ******************/
	
	interface PicBasedBoardUiBinder extends UiBinder<Widget, PicExperiment> {
	}

	private static final PicBasedBoardUiBinder uiBinder = GWT.create(PicBasedBoardUiBinder.class);
	
	protected static final boolean DEBUG_ENABLED = true;
	
	public static class Style{
		public static final String TIME_REMAINING = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL = "wl-clock_activation_panel"; 
	}
	
	public static final String DEFAULT_PIC_WEBCAM_IMAGE_URL = GWT.getModuleBaseURL() + "/waiting_url_image.jpg";
	
	public static final String PIC_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pic.webcam.refresh.millis";
	public static final int DEFAULT_PIC_WEBCAM_REFRESH_TIME = 400;
	
	@UiField VerticalPanel widget;
	@UiField VerticalPanel mainWidgetsPanel;
	private final List<Widget> interactiveWidgets = new Vector<Widget>();
	
	@UiField(provided = true)
	WlWebcam webcam;
	
	@UiField(provided = true)
	WlTimer timer;
	
	@UiField Label selectProgramLabel;
	
	@UiField HorizontalPanel inputWidgetsPanel;
	@UiField VerticalPanel firstCol;
	@UiField HorizontalPanel switchesPanel;
	@UiField HorizontalPanel potentiometersPanel;
	@UiField VerticalPanel secondCol;
	@UiField HorizontalPanel pulsesPanel;
	@UiField HorizontalPanel writeAndTriggerSwitchPanel;
	@UiField VerticalPanel writePanel;
	@UiField VerticalPanel triggerSwitchPanel;
	
	@UiField WlWaitingLabel messages;
	
	@UiField WlTextBoxWithButton serialPortText;
	@UiField WlSwitch triggerSwitch;
	private UploadStructure uploadStructure;
	
	
	public PicExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		super(configurationRetriever, boardController);
		
		this.createProvidedWidgets();
		PicExperiment.uiBinder.createAndBindUi(this);
		
		this.findInteractiveWidgets();
		this.disableInteractiveWidgets();
	}
	
	
	/**
	 * Will find those interactive widgets that are defined on UiBinder
	 * and add them to the interactive widgets list, so that they can
	 * be disabled. This isn't too convenient but currently there doesn't 
	 * seem to be any other way around. That may change in the future.
	 */
	public void findInteractiveWidgets() {
		
		this.addInteractiveWidget(this.timer);
		this.addInteractiveWidget(this.inputWidgetsPanel);
		
		// Find switches
		for(int i = 0; i < this.switchesPanel.getWidgetCount(); ++i){
			final Widget wid = this.switchesPanel.getWidget(i);
			if(wid instanceof WlSwitch) {
				final WlSwitch swi = (WlSwitch)wid;
				this.addInteractiveWidget(swi);
			}
		}
		
		// Find potentiometers
		for(int i = 0; i < this.potentiometersPanel.getWidgetCount(); ++i){
			final Widget wid = this.potentiometersPanel.getWidget(i);
			if(wid instanceof WlPotentiometer) {
				final WlPotentiometer pot = (WlPotentiometer)wid;
				this.addInteractiveWidget(pot);
			}
		}
		
		// Find timed buttons
		for(int i = 0; i < this.pulsesPanel.getWidgetCount(); ++i){
			final Widget wid = this.pulsesPanel.getWidget(i);
			if(wid instanceof WlTimedButton) {
				final WlTimedButton button = (WlTimedButton)wid;
				this.addInteractiveWidget(button);
			}
		}
	}
	
	public void createProvidedWidgets() {
		
		this.webcam = new WlWebcam(this.getWebcamRefreshingTime(), PicExperiment.DEFAULT_PIC_WEBCAM_IMAGE_URL);
		
		this.timer = new WlTimer(false);	
	}
	
	@Override
	public void initialize(){
		this.uploadStructure = new UploadStructure();
		this.uploadStructure.setFileInfo("program");
		this.widget.add(this.uploadStructure.getFormPanel());
	}
	
	@Override
	public void queued(){
	    this.widget.setVisible(false);
	}
	
	@Override
	public void start(int time, String initialConfiguration){
		
		this.setupWidgets();
		this.disableInteractiveWidgets();
		
		RequestWebcamCommand.createAndSend(this.boardController, this.webcam, 
				this.messages);
		
		this.boardController.sendFile(this.uploadStructure, new IResponseCommandCallback() {
		    
		    @Override
		    public void onSuccess(ResponseCommand response) {
		    	PicExperiment.this.enableInteractiveWidgets();
		    	PicExperiment.this.messages.setText("Device ready");
		    	PicExperiment.this.messages.stop();
		    }

		    @Override
		    public void onFailure(WlCommException e) {
		    	PicExperiment.this.messages.setText("Error sending file: " + e.getMessage());
		    
		    	if(PicExperiment.DEBUG_ENABLED) {
			    	PicExperiment.this.enableInteractiveWidgets();
			    	PicExperiment.this.messages.setText("Device not ready but debugging enabled");
			    	PicExperiment.this.messages.stop();
		    	}
		    
		    }
		});
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
		
		// Dispose of switches
		for(int i = 0; i < this.switchesPanel.getWidgetCount(); ++i){
			final Widget wid = this.switchesPanel.getWidget(i);
			if(wid instanceof WlSwitch) {
				final WlSwitch swi = (WlSwitch)wid;
				swi.dispose();
			}
		}
		
		// Dispose of potentiometers
		for(int i = 0; i < this.potentiometersPanel.getWidgetCount(); ++i){
			final Widget wid = this.potentiometersPanel.getWidget(i);
			if(wid instanceof WlPotentiometer) {
				final WlPotentiometer pot = (WlPotentiometer)wid;
				pot.dispose();
			}
		}
		
		// Dispose of timed buttons
		for(int i = 0; i < this.pulsesPanel.getWidgetCount(); ++i){
			final Widget wid = this.pulsesPanel.getWidget(i);
			if(wid instanceof WlTimedButton) {
				final WlTimedButton button = (WlTimedButton)wid;
				button.dispose();
			}
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
	
	private void setupWidgets() {
		
		// Previously invisible so as not to take space on the reserve screen.
	    this.widget.setVisible(true);
		this.inputWidgetsPanel.setVisible(true);
		this.selectProgramLabel.setVisible(false);
		this.uploadStructure.getFormPanel().setVisible(false);

		this.mainWidgetsPanel.setSpacing(10);
		
		// Webcam
		this.webcam.setVisible(true);
		this.webcam.start();
		
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    PicExperiment.this.boardController.clean();
			}
		});
		this.timer.start();
		
		// Prepares every UiBinder-defined control for usage, setting up their listeners.
		this.prepareSwitches();
		this.preparePotentiometers();
		this.prepareTimedButtons();
		
		// Write
		this.serialPortText.addActionListener(
			new WriteListener(
				0, // The only one by the moment :-)
				this.boardController
			)
		);					
		
		// "Trigger" Switch
		final IWlActionListener actionListener = new SwitchListener(4, this.boardController);
		this.triggerSwitch.addActionListener(actionListener);
		
		// Messages
		this.messages.setText("Programming device");
		this.messages.start();
	}
	
	/**
	 * Will prepare every timed button (pulse) setting up a listener for it using 
	 * its title as its integer identifier.
	 */
	private void prepareTimedButtons() {
		for(int i = 0; i < this.pulsesPanel.getWidgetCount(); ++i){
			final Widget wid = this.pulsesPanel.getWidget(i);
			if(wid instanceof WlTimedButton) {
				final WlTimedButton button = (WlTimedButton)wid;
				
				// Avoid trying to convert non-numerical titles (which serve
				// as identifiers). Not exactly an elegant way to do it.
				if(button.getTitle().length() != 1) 
					continue;
		
				final int id = this.pulsesPanel.getWidgetCount() - 
					Integer.parseInt(button.getTitle()) - 1;
				final ButtonListener buttonListener = new ButtonListener(id, button, this.boardController);
				button.addButtonListener(buttonListener);
			}
		}
	}


	/**
	 * Will prepare every potentiometer setting up a listener for it using 
	 * its title as its integer identifier.
	 */
	private void preparePotentiometers() {
		for(int i = 0; i < this.potentiometersPanel.getWidgetCount(); ++i){
			final Widget wid = this.potentiometersPanel.getWidget(i);
			if(wid instanceof WlPotentiometer) {
				final WlPotentiometer pot = (WlPotentiometer)wid;
				
				// Avoid trying to convert non-numerical titles (which serve
				// as identifiers). Not exactly an elegant way to do it.
				if(pot.getTitle().length() != 1) 
					continue;
				
				final int id = this.potentiometersPanel.getWidgetCount() - 
					Integer.parseInt(pot.getTitle()) - 1;
				final PotentiometerListener potentiometerListener = 
					new PotentiometerListener(id, this.boardController);
				pot.addActionListener(potentiometerListener);
			}
		}
	}


	/**
	 * Will prepare every switch setting up a listener for it using 
	 * its title as its integer identifier.
	 */
	private void prepareSwitches() {
		for(int i = 0; i < this.switchesPanel.getWidgetCount(); ++i){
			final Widget wid = this.switchesPanel.getWidget(i);
			if(wid instanceof WlSwitch) {
				final WlSwitch swi = (WlSwitch)wid;
				
				// Avoid trying to convert non-numerical titles (which serve
				// as identifiers). Not exactly an elegant way to do it.
				if(swi.getTitle().length() != 1) 
					continue;
				
				final int id = this.switchesPanel.getWidgetCount() - 
					Integer.parseInt(swi.getTitle()) - 1;
				final IWlActionListener actionListener = 
					new SwitchListener(id, this.boardController);
				swi.addActionListener(actionListener);
			}
		}
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

	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
			PicExperiment.PIC_WEBCAM_REFRESH_TIME_PROPERTY, 
			PicExperiment.DEFAULT_PIC_WEBCAM_REFRESH_TIME
			);
	}	
}
