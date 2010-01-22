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

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
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
import es.deusto.weblab.client.ui.widgets.WlPotentiometer;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlTextBoxWithButton;
import es.deusto.weblab.client.ui.widgets.WlTimedButton;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class WlDeustoPicBasedBoard extends BoardBase{
	
	public static class Style{
		public static final String TIME_REMAINING = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL = "wl-clock_activation_panel"; 
	}
	
	public static final String PIC_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.pic.webcam.image.url";
	public static final String DEFAULT_PIC_WEBCAM_IMAGE_URL = "https://fpga.weblab.deusto.es/webcam/fpga0/image.jpg";
	
	public static final String PIC_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pic.webcam.refresh.millis";
	public static final int DEFAULT_PIC_WEBCAM_REFRESH_TIME = 400;
	
	private static final int TIMED_BUTTON_NUMBER = 4;
	private static final int SWITCH_NUMBER = 4;

	protected IConfigurationManager configurationManager;

	private VerticalPanel widget;
	private VerticalPanel verticalPanel;
	private final List<Widget> interactiveWidgets;
	
	private WlWebcam webcam;
	
	private WlTimer timer;
	private WlWaitingLabel messages;
	
	private WlSwitch [] switches;	
	private WlTimedButton [] buttons;	
	private WlTextBoxWithButton serialPortText;	
	private WlPotentiometer potentiometer;
	private UploadStructure uploadStructure;
	
	public WlDeustoPicBasedBoard(IConfigurationManager configurationManager, IBoardBaseController boardController){
		super(boardController);
		
		this.configurationManager = configurationManager;

		this.interactiveWidgets = new Vector<Widget>();
		this.verticalPanel = new VerticalPanel();
		this.widget        = new VerticalPanel();
		this.widget.add(this.verticalPanel);
	}
	
	@Override
	public void initialize(){
	    this.widget.setWidth("100%");
	    this.widget.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	    	
		this.verticalPanel.setWidth("100%");
		this.verticalPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.verticalPanel.add(new Label("Select the program to send:"));
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
		final Widget firstRow = this.createFirstRow();
		
		final HorizontalPanel secondRow = this.createSecondRow();
		final HorizontalPanel thirdRow = this.createThirdRow();
		final HorizontalPanel fourthRow = this.createFourthRow();

		this.verticalPanel = new VerticalPanel();
		this.verticalPanel.setWidth("100%");
		this.verticalPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		final VerticalPanel otherVerticalPanel = new VerticalPanel();
		otherVerticalPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		otherVerticalPanel.setSpacing(20);
		otherVerticalPanel.setWidth("85%");
		
		otherVerticalPanel.add(firstRow);
		otherVerticalPanel.add(secondRow);
		otherVerticalPanel.add(thirdRow);
		otherVerticalPanel.add(fourthRow);
		
		this.verticalPanel.add(otherVerticalPanel);
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

	private Widget createFirstRow() {
		this.webcam = new WlWebcam(
				this.getWebcamRefreshingTime(),
				this.getWebcamImageUrl()
			);
		this.webcam.start();
		return this.webcam.getWidget();
	}
	
	private HorizontalPanel createSecondRow() {
		this.timer = new WlTimer();
		this.timer.setStyleName(WlDeustoPicBasedBoard.Style.TIME_REMAINING);
		this.timer.getWidget().setWidth("30%");
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			public void onFinished() {
			    WlDeustoPicBasedBoard.this.boardController.onClean();
			}
		});
		
		this.messages = new WlWaitingLabel("Programming device");
		this.messages.start();
		
		this.potentiometer = new WlPotentiometer();
		final PotentiometerListener potentiometerListener = new PotentiometerListener(
										0, // The only one by the moment :-) 
										this.boardController
								);
		this.potentiometer.addActionListener(potentiometerListener);
		this.potentiometer.getWidget().setWidth("70%");
		
		final HorizontalPanel secondRow = new HorizontalPanel();
		secondRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		secondRow.setWidth("100%");
		secondRow.add(this.timer.getWidget());
		secondRow.add(this.messages.getWidget());
		secondRow.add(this.potentiometer.getWidget());
		
		this.addInteractiveWidget(this.timer.getWidget());
		
		return secondRow;
	}
	
	private HorizontalPanel createThirdRow() {
		this.switches = new WlSwitch[WlDeustoPicBasedBoard.SWITCH_NUMBER];
		for(int i = 0; i < WlDeustoPicBasedBoard.SWITCH_NUMBER; ++i){
			this.switches[i] = new WlSwitch();
			final IWlActionListener actionListener = new SwitchListener(i, this.boardController);
			this.switches[i].addActionListener(actionListener);
		}
		
		this.buttons = new WlTimedButton[WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER];
		for(int i = 0; i < WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER; ++i){
			this.buttons[i] = new WlTimedButton();
			final ButtonListener buttonListener = new ButtonListener(i, this.buttons[i], this.boardController);
			this.buttons[i].addButtonListener(buttonListener);
		}
		
		final HorizontalPanel thirdRow = new HorizontalPanel();
		thirdRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		thirdRow.setWidth("100%");
		
		for(int i = 0; i < WlDeustoPicBasedBoard.SWITCH_NUMBER; ++i){
			this.switches[i].getWidget().setWidth("100%");
			
			final VerticalPanel vp = new VerticalPanel();
			vp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			vp.add(new Label("" + (WlDeustoPicBasedBoard.SWITCH_NUMBER - i - 1)));
			vp.add(this.switches[i].getWidget());
			thirdRow.add(vp);
			
			this.addInteractiveWidget(vp);
		}
		
		for(int i = 0; i < WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER; ++i){
			this.buttons[i].getWidget().setWidth("100%");
			
			final VerticalPanel vp = new VerticalPanel();
			vp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			vp.add(new Label("" + (WlDeustoPicBasedBoard.TIMED_BUTTON_NUMBER - i - 1)));
			vp.add(this.buttons[i].getWidget());
			thirdRow.add(vp);
			
			this.addInteractiveWidget(vp);
		}
		
		return thirdRow;
	}

	private HorizontalPanel createFourthRow() {
		this.serialPortText = new WlTextBoxWithButton();
		this.serialPortText.addActionListener(
			new WriteListener(
				0, // The only one by the moment :-)
				this.boardController
			)
		);
		
		final HorizontalPanel fourthRow = new HorizontalPanel();
		fourthRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		fourthRow.setWidth("100%");
		
		fourthRow.add(this.serialPortText.getWidget());
		
		return fourthRow;
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
