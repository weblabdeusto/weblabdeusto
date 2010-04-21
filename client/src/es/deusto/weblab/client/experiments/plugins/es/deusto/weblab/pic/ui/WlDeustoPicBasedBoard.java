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
	
	private static final int TIMED_BUTTON_NUMBER = 4;
	private static final int SWITCH_NUMBER = 4;
	private static final int POTENTIOMETER_NUMBER = 4;

	protected IConfigurationManager configurationManager;

	@UiField VerticalPanel widget;
	@UiField VerticalPanel removableWidgetsPanel;
	private final List<Widget> interactiveWidgets;
	
	@UiField(provided = true)
	WlWebcam webcam;
	
	@UiField(provided = true)
	WlTimer timer;
	
	@UiField WlHorizontalPanel inputWidgetsPanel;
	@UiField WlVerticalPanel firstCol;
	@UiField WlHorizontalPanel switchesPanel;
	@UiField WlHorizontalPanel potentiometersPanel;
	@UiField WlVerticalPanel secondCol;
	@UiField WlHorizontalPanel pulsesPanel;
	@UiField WlHorizontalPanel writeAndTriggerSwitchPanel;
	@UiField WlVerticalPanel writePanel;
	@UiField WlVerticalPanel triggerSwitchPanel;
	
	private WlWaitingLabel messages;
	
	private WlSwitch [] switches;	
	private WlTimedButton [] buttons;	
	private WlPotentiometer[] potentiometers;
	private WlTextBoxWithButton serialPortText;
	private WlSwitch triggerSwitch;
	private UploadStructure uploadStructure;
	
	public WlDeustoPicBasedBoard(IConfigurationManager configurationManager, IBoardBaseController boardController){
		super(boardController);
		
		this.configurationManager = configurationManager;

		this.interactiveWidgets = new Vector<Widget>();
		
		this.createProvidedWidgets();
		
		WlDeustoPicBasedBoard.uiBinder.createAndBindUi(this);
		
		//this.removableWidgetsPanel = new VerticalPanel();
		
		//this.widget = new VerticalPanel();
		//this.widget.add(this.removableWidgetsPanel);
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
		if(this.switches != null){
			for(int i = 0; i < this.switches.length; ++i)
				this.switches[i].dispose();
			this.switches = null;
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
	
	private void loadWidgets() {

		this.removableWidgetsPanel.setSpacing(10);
		this.removableWidgetsPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		while(this.removableWidgetsPanel.getWidgetCount() > 0)
		    this.removableWidgetsPanel.remove(0);
		
		// Webcam
		this.webcam.setVisible(true);
		this.webcam.start();
		
		// We gotta re-add it because it's been removed before.
		this.removableWidgetsPanel.add(this.webcam.getWidget());
		
		// Timer
		//this.timer = new WlTimer();
		//this.timer.setStyleName(WlDeustoPicBasedBoard.Style.TIME_REMAINING);
		//this.timer.getWidget().setWidth("30%");
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			public void onFinished() {
			    WlDeustoPicBasedBoard.this.boardController.onClean();
			}
		});
		this.timer.start();
		this.removableWidgetsPanel.add(this.timer);	
		this.addInteractiveWidget(this.timer);
		
		// Input Widgets
		//WlHorizontalPanel inputWidgetsPanel = new WlHorizontalPanel();
		//inputWidgetsPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.removableWidgetsPanel.add(this.inputWidgetsPanel);		
		this.addInteractiveWidget(this.inputWidgetsPanel);
		
		// 1st column: Switches and Potentiometers
		//final WlVerticalPanel firstCol = new WlVerticalPanel();
		//this.firstCol.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		//this.firstCol.setWidth("100%");
		this.inputWidgetsPanel.add(this.firstCol);
		
		// Switches
		//final WlHorizontalPanel switchesPanel = new WlHorizontalPanel();
		//switchesPanel.setWidth("100%");
		//switchesPanel.setSpacing(20);
		this.switches = new WlSwitch[WlDeustoPicBasedBoard.SWITCH_NUMBER];
		for(int i = 0; i < WlDeustoPicBasedBoard.SWITCH_NUMBER; ++i){
			this.switches[i] = new WlSwitch();
			final IWlActionListener actionListener = new SwitchListener(i, this.boardController);
			this.switches[i].addActionListener(actionListener);
			final WlVerticalPanel switchPanel = new WlVerticalPanel();
			switchPanel.setWidth("100%");
			switchPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			switchPanel.add(this.switches[i].getWidget());
			switchPanel.add(new Label("" + (WlDeustoPicBasedBoard.SWITCH_NUMBER - i - 1)));			
			this.switchesPanel.add(switchPanel);
		}
		this.firstCol.add(this.switchesPanel);

		// Potentiometers
		//final WlHorizontalPanel potentiometersPanel = new WlHorizontalPanel();
		//potentiometersPanel.setSpacing(20);
		this.potentiometers = new WlPotentiometer[WlDeustoPicBasedBoard.POTENTIOMETER_NUMBER];
		for(int i = 0; i < WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER; ++i){
			this.potentiometers[i] = new WlPotentiometer();
			final PotentiometerListener potentiometerListener = new PotentiometerListener(i, this.boardController);
			this.potentiometers[i].addActionListener(potentiometerListener);
			final WlVerticalPanel potentiometerPanel = new WlVerticalPanel();
			potentiometerPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			potentiometerPanel.add(this.potentiometers[i].getWidget());
			potentiometerPanel.add(new Label("" + (WlDeustoPicBasedBoard.POTENTIOMETER_NUMBER - i + 1)));			
			this.potentiometersPanel.add(potentiometerPanel);
		}	
		this.firstCol.add(this.potentiometersPanel);	
		
		// 2nd column: Pulses and Write
		//final WlVerticalPanel secondCol = new WlVerticalPanel();
		//secondCol.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		//secondCol.setWidth("100%");
		this.inputWidgetsPanel.add(this.secondCol);
		
		// Pulses
		//final WlHorizontalPanel pulsesPanel = new WlHorizontalPanel();
		//pulsesPanel.setSpacing(20);
		this.buttons = new WlTimedButton[WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER];
		for(int i = 0; i < WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER; ++i){
			this.buttons[i] = new WlTimedButton();
			final ButtonListener buttonListener = new ButtonListener(i, this.buttons[i], this.boardController);
			this.buttons[i].addButtonListener(buttonListener);
			final WlVerticalPanel pulsePanel = new WlVerticalPanel();
			pulsePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			pulsePanel.add(this.buttons[i].getWidget());
			pulsePanel.add(new Label("" + (WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER - i + 3)));			
			this.pulsesPanel.add(pulsePanel);
		}	
		this.secondCol.add(this.pulsesPanel);	
		
		// Write and "Trigger" Switch Panel
//		final WlHorizontalPanel writeAndTriggerSwitchPanel = new WlHorizontalPanel();
//		writeAndTriggerSwitchPanel.setSpacing(20);
//		writeAndTriggerSwitchPanel.setWidth("100%");
		this.secondCol.add(this.writeAndTriggerSwitchPanel);
		
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
		this.writeAndTriggerSwitchPanel.add(writePanel);	
		
		// "Trigger" Switch
		this.triggerSwitch = new WlSwitch();
		final IWlActionListener actionListener = new SwitchListener(4, this.boardController);
		this.triggerSwitch.addActionListener(actionListener);
		
		//final WlVerticalPanel triggerSwitchPanel = new WlVerticalPanel();
		//triggerSwitchPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.triggerSwitchPanel.add(this.triggerSwitch.getWidget());
		this.triggerSwitchPanel.add(new Label("Trigger"));					
		this.writeAndTriggerSwitchPanel.add(this.triggerSwitchPanel);	
		
		
/*		
		// 3rd column: "Trigger" Switch
		final WlVerticalPanel thirdCol = new WlVerticalPanel();
		thirdCol.setSpacing(15);
		thirdCol.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		thirdCol.setWidth("100%");
		inputWidgetsPanel.add(thirdCol);			
*/		
		
		// Messages
		this.messages = new WlWaitingLabel("Programming device");
		this.messages.start();
		this.removableWidgetsPanel.add(this.messages.getWidget());
		
		/*
		// 1st row: Switches and Pulses
		final WlHorizontalPanel firstRow = new WlHorizontalPanel();
		firstRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		firstRow.setWidth("100%");
		this.removableWidgetsPanel.add(firstRow);
		this.addInteractiveWidget(firstRow);
		
		// Switches
		final WlHorizontalPanel switchesPanel = new WlHorizontalPanel();
		this.switches = new WlSwitch[WlDeustoPicBasedBoard.SWITCH_NUMBER];
		for(int i = 0; i < WlDeustoPicBasedBoard.SWITCH_NUMBER; ++i){
			this.switches[i] = new WlSwitch();
			final IWlActionListener actionListener = new SwitchListener(i, this.boardController);
			this.switches[i].addActionListener(actionListener);
			final WlVerticalPanel switchPanel = new WlVerticalPanel();
			switchPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			switchPanel.add(this.switches[i].getWidget());
			switchPanel.add(new Label("" + (WlDeustoPicBasedBoard.SWITCH_NUMBER - i - 1)));			
			switchesPanel.add(switchPanel);
		}
		firstRow.add(switchesPanel);
		
		// Pulses
		final WlHorizontalPanel pulsesPanel = new WlHorizontalPanel();
		this.buttons = new WlTimedButton[WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER];
		for(int i = 0; i < WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER; ++i){
			this.buttons[i] = new WlTimedButton();
			final ButtonListener buttonListener = new ButtonListener(i, this.buttons[i], this.boardController);
			this.buttons[i].addButtonListener(buttonListener);
			final WlVerticalPanel pulsePanel = new WlVerticalPanel();
			pulsePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			pulsePanel.add(this.buttons[i].getWidget());
			pulsePanel.add(new Label("" + (WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER - i - 1)));			
			pulsesPanel.add(pulsePanel);
		}	
		firstRow.add(pulsesPanel);
		
		// 2nd row: Potentiometers, Write and "trigger" Switch
		final WlHorizontalPanel secondRow = new WlHorizontalPanel();
		secondRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		secondRow.setWidth("100%");
		this.removableWidgetsPanel.add(secondRow);
		this.addInteractiveWidget(secondRow);
		
		// Potentiometers
		final WlHorizontalPanel potentiometersPanel = new WlHorizontalPanel();
		this.potentiometers = new WlPotentiometer[WlDeustoPicBasedBoard.POTENTIOMETER_NUMBER];
		for(int i = 0; i < WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER; ++i){
			this.potentiometers[i] = new WlPotentiometer();
			final PotentiometerListener potentiometerListener = new PotentiometerListener(i, this.boardController);
			this.potentiometers[i].addActionListener(potentiometerListener);
			final WlVerticalPanel potentiometerPanel = new WlVerticalPanel();
			potentiometerPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			potentiometerPanel.add(this.potentiometers[i].getWidget());
			potentiometerPanel.add(new Label("" + (WlDeustoPicBasedBoard.POTENTIOMETER_NUMBER - i - 1)));			
			pulsesPanel.add(potentiometerPanel);		
			potentiometersPanel.add(potentiometerPanel);
		}	
		secondRow.add(potentiometersPanel);		
		
		// Write
		this.serialPortText = new WlTextBoxWithButton();
		this.serialPortText.addActionListener(
			new WriteListener(
				0, // The only one by the moment :-)
				this.boardController
			)
		);
		final WlVerticalPanel writePanel = new WlVerticalPanel();
		writePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		writePanel.add(this.serialPortText.getWidget());
		writePanel.add(new Label("UART"));					
		secondRow.add(writePanel);		
		
		// "Trigger" Switch
		this.triggerSwitch = new WlSwitch();
		final IWlActionListener actionListener = new SwitchListener(4, this.boardController);
		this.triggerSwitch.addActionListener(actionListener);
		final WlVerticalPanel triggetSwitchPanel = new WlVerticalPanel();
		triggetSwitchPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		triggetSwitchPanel.add(this.triggerSwitch.getWidget());
		triggetSwitchPanel.add(new Label("Trigger"));					
		secondRow.add(triggetSwitchPanel);	
		*/
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
