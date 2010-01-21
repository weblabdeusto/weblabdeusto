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

import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
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
import es.deusto.weblab.client.ui.widgets.WlClockActivator;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlTimedButton;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlButton.IWlButtonUsed;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public abstract class WlDeustoXilinxBasedBoard extends BoardBase{

	public static class Style{
		public static final String TIME_REMAINING         = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL = "wl-clock_activation_panel"; 
	}
	
	protected IConfigurationManager configurationManager;
	
	private static final int TIMED_BUTTON_NUMBER = 4;
	private static final int SWITCH_NUMBER = 10;
	
	protected VerticalPanel verticalPanel;
	private VerticalPanel widget;
	private final List<Widget> interactiveWidgets;
	
	private WlWebcam webcam;
	
	private WlTimer timer;
	private WlWaitingLabel messages;
	private WlClockActivator clockActivator;
	
	private WlSwitch [] switches;
	
	private WlTimedButton [] timedButtons;
	
	protected abstract int getWebcamRefreshingTime();
	protected abstract String getWebcamImageUrl();
	
	private UploadStructure uploadStructure;
	
	public WlDeustoXilinxBasedBoard(IConfigurationManager configurationManager, IBoardBaseController boardController){
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
			WlDeustoXilinxBasedBoard.this.enableInteractiveWidgets();
			WlDeustoXilinxBasedBoard.this.messages.setText("Device ready");
			WlDeustoXilinxBasedBoard.this.messages.stop();
		    }

		    @Override
		    public void onFailure(WlCommException e) {
			WlDeustoXilinxBasedBoard.this.messages.setText("Error sending file: " + e.getMessage());
		    }
		});
	}
	
	private void loadWidgets() {
		final Widget firstRow = this.createFirstRow();
		
		final HorizontalPanel secondRow = this.createSecondRow();
		final HorizontalPanel thirdRow = this.createThirdRow();
		final HorizontalPanel fourthRow = this.createFourthRow();

		while(this.verticalPanel.getWidgetCount() > 0)
		    this.verticalPanel.remove(0);
		
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
		this.timer.setStyleName(WlDeustoXilinxBasedBoard.Style.TIME_REMAINING);
		this.timer.getWidget().setWidth("30%");
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			public void onFinished() {
				WlDeustoXilinxBasedBoard.this.boardController.onClean();
			}
		});
		
		this.messages = new WlWaitingLabel("Programming device");
		this.messages.start();
		this.clockActivator = new WlClockActivator();
		this.clockActivator.getWidget().setWidth("70%");
		this.clockActivator.setStyleName(WlDeustoXilinxBasedBoard.Style.CLOCK_ACTIVATION_PANEL);
		final ClockActivationListener clockActivationListener = new ClockActivationListener(this.boardController, this.getResponseCommandCallback());
		this.clockActivator.addClockActivationListener(clockActivationListener);
		
		final HorizontalPanel secondRow = new HorizontalPanel();
		secondRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		secondRow.setWidth("100%");
		secondRow.add(this.timer.getWidget());
		secondRow.add(this.messages.getWidget());
		secondRow.add(this.clockActivator.getWidget());
		
		this.addInteractiveWidget(this.timer.getWidget());
		this.addInteractiveWidget(this.clockActivator.getWidget());
		
		return secondRow;
	}
	
	private HorizontalPanel createThirdRow() {
		this.switches = new WlSwitch[WlDeustoXilinxBasedBoard.SWITCH_NUMBER];
		for(int i = 0; i < WlDeustoXilinxBasedBoard.SWITCH_NUMBER; ++i){
			this.switches[i] = new WlSwitch();
			final IWlActionListener actionListener = new SwitchListener(i, this.boardController, this.getResponseCommandCallback());
			this.switches[i].addActionListener(actionListener);
		}
		
		final HorizontalPanel thirdRow = new HorizontalPanel();
		thirdRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		thirdRow.setWidth("100%");
		for(int i = 0; i < WlDeustoXilinxBasedBoard.SWITCH_NUMBER; ++i){
			this.switches[i].getWidget().setWidth("100%");
			
			final VerticalPanel vp = new VerticalPanel();
			vp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			vp.add(new Label("" + (WlDeustoXilinxBasedBoard.SWITCH_NUMBER - i - 1)));
			vp.add(this.switches[i].getWidget());
			thirdRow.add(vp);
			
			this.addInteractiveWidget(vp);
		}
		return thirdRow;
	}

	private HorizontalPanel createFourthRow() {
		this.timedButtons = new WlTimedButton[WlDeustoXilinxBasedBoard.TIMED_BUTTON_NUMBER];
		for(int i = 0; i < WlDeustoXilinxBasedBoard.TIMED_BUTTON_NUMBER; ++i){
			this.timedButtons[i] = new WlTimedButton();
			final IWlButtonUsed buttonUsed = new ButtonListener(i, this.boardController, this.getResponseCommandCallback());
			this.timedButtons[i].addButtonListener(buttonUsed);
		}
		
		final HorizontalPanel fourthRow = new HorizontalPanel();
		fourthRow.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		fourthRow.setWidth("100%");
		for(int i = 0; i < WlDeustoXilinxBasedBoard.TIMED_BUTTON_NUMBER; ++i){
			final VerticalPanel vp = new VerticalPanel();
			vp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			vp.add(new Label("" + (WlDeustoXilinxBasedBoard.TIMED_BUTTON_NUMBER - i - 1)));
			vp.add(this.timedButtons[i].getWidget());
			fourthRow.add(vp);
			this.addInteractiveWidget(vp);
		}
		return fourthRow;
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
		
		if(this.switches != null){
			for(int i = 0; i < this.switches.length; ++i)
				this.switches[i].dispose();
			this.switches = null;
		}
		
		if(this.timedButtons != null){
			for(int i = 0; i < this.timedButtons.length; ++i)
				this.timedButtons[i].dispose();
			this.timedButtons = null;
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
