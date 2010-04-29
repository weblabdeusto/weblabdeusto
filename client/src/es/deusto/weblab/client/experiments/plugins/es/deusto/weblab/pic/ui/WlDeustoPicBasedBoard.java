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

import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
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
import es.deusto.weblab.client.ui.widgets.WlHorizontalPanel;
import es.deusto.weblab.client.ui.widgets.WlPotentiometer;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlTextBoxWithButton;
import es.deusto.weblab.client.ui.widgets.WlTimedButton;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class WlDeustoPicBasedBoard extends BoardBase{
	
	
	 /******************
	 * UIBINDER RELATED
	 ******************/
	
	interface PicBasedBoardUiBinder extends UiBinder<Widget, WlDeustoPicBasedBoard> {
	}

	private static final PicBasedBoardUiBinder uiBinder = GWT.create(PicBasedBoardUiBinder.class);
	
	protected static final boolean DEBUG_ENABLED = true;
	
	public static class Style{
		public static final String TIME_REMAINING = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL = "wl-clock_activation_panel"; 
	}
	
	public static final String PIC_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.pic.webcam.image.url";
	public static final String DEFAULT_PIC_WEBCAM_IMAGE_URL = "https://www.weblab.deusto.es/webcam/pic0/image.jpg";
	
	public static final String PIC_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pic.webcam.refresh.millis";
	public static final int DEFAULT_PIC_WEBCAM_REFRESH_TIME = 400;
	

	protected IConfigurationManager configurationManager;

	@UiField VerticalPanel widget;
	@UiField VerticalPanel mainWidgetsPanel;
	private final List<Widget> interactiveWidgets = new Vector<Widget>();
	
	@UiField(provided = true)
	WlWebcam webcam;
	
	@UiField(provided = true)
	WlTimer timer;
	
	@UiField Label selectProgramLabel;
	
	@UiField WlHorizontalPanel inputWidgetsPanel;
	@UiField WlVerticalPanel firstCol;
	@UiField WlHorizontalPanel switchesPanel;
	@UiField WlHorizontalPanel potentiometersPanel;
	@UiField WlVerticalPanel secondCol;
	@UiField WlHorizontalPanel pulsesPanel;
	@UiField WlHorizontalPanel writeAndTriggerSwitchPanel;
	@UiField WlVerticalPanel writePanel;
	@UiField WlVerticalPanel triggerSwitchPanel;
	
	@UiField WlWaitingLabel messages;
	
	private WlTextBoxWithButton serialPortText;
	@UiField WlSwitch triggerSwitch;
	private UploadStructure uploadStructure;
	
	public WlDeustoPicBasedBoard(IConfigurationManager configurationManager, IBoardBaseController boardController){
		super(boardController);
		
		this.configurationManager = configurationManager;
		
		this.createProvidedWidgets();
		WlDeustoPicBasedBoard.uiBinder.createAndBindUi(this);
		
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
		
		this.webcam = new WlWebcam(
				this.getWebcamRefreshingTime(),
				this.getWebcamImageUrl()
			);
		
		this.timer = new WlTimer(false);
		
	}
	
	@Override
	public void initialize(){
	    //this.widget.setWidth("100%");
	    //this.widget.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	    	
		//this.removableWidgetsPanel.setWidth("100%");
		//this.removableWidgetsPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		
		//this.removableWidgetsPanel.add(new Label("Select the program to send:"));
		this.uploadStructure = new UploadStructure();
		this.uploadStructure.setFileInfo("program");
		this.widget.add(this.uploadStructure.getFormPanel());
	}
	
	@Override
	public void queued(){
	    	this.widget.setVisible(false);
	}
	
	@Override
	public void start(){
	    this.widget.setVisible(true);
		this.loadWidgets();
		this.disableInteractiveWidgets();
		
		this.selectProgramLabel.setVisible(false);
    	
		this.uploadStructure.getFormPanel().setVisible(false);
		
		this.boardController.sendFile(this.uploadStructure, new IResponseCommandCallback() {
		    
		    @Override
		    public void onSuccess(ResponseCommand response) {
		    	WlDeustoPicBasedBoard.this.enableInteractiveWidgets();
		    	WlDeustoPicBasedBoard.this.messages.setText("Device ready");
		    	WlDeustoPicBasedBoard.this.messages.stop();
		    }

		    @Override
		    public void onFailure(WlCommException e) {
		    	WlDeustoPicBasedBoard.this.messages.setText("Error sending file: " + e.getMessage());
		    
		    	if(WlDeustoPicBasedBoard.DEBUG_ENABLED) {
			    	WlDeustoPicBasedBoard.this.enableInteractiveWidgets();
			    	WlDeustoPicBasedBoard.this.messages.setText("Device not ready but debugging enabled");
			    	WlDeustoPicBasedBoard.this.messages.stop();
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
		
		// TODO: Handle disposal of controls. As of writing this only switches seem to be disposed of.
		
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
	
	private void loadWidgets() {
		
		// Previously invisible so as not to take space on the reserve screen.
		this.inputWidgetsPanel.setVisible(true);

		this.mainWidgetsPanel.setSpacing(10);
		this.mainWidgetsPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		// Webcam
		this.webcam.setVisible(true);
		this.webcam.start();
		
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			public void onFinished() {
			    WlDeustoPicBasedBoard.this.boardController.onClean();
			}
		});
		this.timer.start();
		this.addInteractiveWidget(this.timer);
		
		this.addInteractiveWidget(this.inputWidgetsPanel);
		
		prepareSwitches();
		preparePotentiometers();
		prepareTimedButtons();
		
		// Write
		this.serialPortText = new WlTextBoxWithButton();
		this.serialPortText.addActionListener(
			new WriteListener(
				0, // The only one by the moment :-)
				this.boardController
			)
		);
		final WlVerticalPanel writePanel = new WlVerticalPanel();
		writePanel.setWidth("100%");
		writePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		writePanel.add(this.serialPortText.getWidget());
		writePanel.add(new Label("UART"));						
		
		// "Trigger" Switch
		final IWlActionListener actionListener = new SwitchListener(4, this.boardController);
		this.triggerSwitch.addActionListener(actionListener);
		
		// Messages
		this.messages.setText("Programming device");
		this.messages.start();
		this.mainWidgetsPanel.add(this.messages);
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

	private String getWebcamImageUrl() {
		return this.configurationManager.getProperty(
			WlDeustoPicBasedBoard.PIC_WEBCAM_IMAGE_URL_PROPERTY, 
			WlDeustoPicBasedBoard.DEFAULT_PIC_WEBCAM_IMAGE_URL
			);
	}

	private int getWebcamRefreshingTime() {
		return this.configurationManager.getIntProperty(
			WlDeustoPicBasedBoard.PIC_WEBCAM_REFRESH_TIME_PROPERTY, 
			WlDeustoPicBasedBoard.DEFAULT_PIC_WEBCAM_REFRESH_TIME
			);
	}	
}
