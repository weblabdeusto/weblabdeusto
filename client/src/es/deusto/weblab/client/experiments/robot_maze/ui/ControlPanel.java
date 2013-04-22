/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: FILLME
*
*/

package es.deusto.weblab.client.experiments.robot_maze.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.MouseDownEvent;
import com.google.gwt.event.dom.client.MouseUpEvent;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class ControlPanel extends Composite {

	private static final String WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME    = 200;
	
	private static final String RIGHT = "RIGHT";
	private static final String LEFT = "LEFT";
	private static final String DOWN = "BACK";
	private static final String UP = "FORWARD";

	private final IBoardBaseController boardController;
	private final IConfigurationRetriever configurationRetriever;
	
	private final Map<String, Image> buttons;
	private int moveNumber = 0;
	private boolean buttonsEnabled = true;
	
	@UiField(provided = true) WlWebcam webcam;
	@UiField(provided = true) WlTimer timer;
	
	// Root panel.
	@UiField VerticalPanel widget;
	
	@UiField VerticalPanel mainWidgetsPanel;
	@UiField HorizontalPanel inputWidgetsPanel;
	
	@UiField WlWaitingLabel messages;
	@UiField Image upButton;
	@UiField Image downButton;
	@UiField Image rightButton;
	@UiField Image leftButton;
	
	private boolean upPressed = false;
	private boolean downPressed = false;
	private boolean leftPressed = false;
	private boolean rightPressed = false;
	
	private static ControlPanelUiBinder uiBinder = GWT.create(ControlPanelUiBinder.class);

	interface ControlPanelUiBinder extends UiBinder<Widget, ControlPanel> {}

	public ControlPanel(IBoardBaseController boardController, IConfigurationRetriever configurationRetriever, JSONObject initialConfigObject, int time) {
		
		// Basic configuration
		this.boardController = boardController;
		this.configurationRetriever = configurationRetriever;
		
		// Create provided widgets (e.g. timer and so on) before using the UI Binder, then the rest 
		createProvidedWidgets(time);
		initWidget(uiBinder.createAndBindUi(this));
		setupWidgets();

		// Once images are bound by the UI Binder
		this.buttons = new HashMap<String, Image>();
		this.buttons.put(UP,    this.upButton);
		this.buttons.put(DOWN,  this.downButton);
		this.buttons.put(LEFT,  this.leftButton);
		this.buttons.put(RIGHT, this.rightButton);
		
		// The camera is special, once everything is shown, then configure and start it
		this.webcam.configureWebcam(initialConfigObject);
	    this.webcam.setVisible(true);
	    this.webcam.start();
	}
	
	public IWlDisposableWidget [] getDisposableWidgets() {
		return new IWlDisposableWidget[]{
			this.timer,
			this.messages,
			this.webcam,
		};
	}

	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    ControlPanel.this.boardController.clean();
			}
		});
		this.timer.start();
	}
	
	
	/* Creates those widgets that are placed through UiBinder but
	 * whose ctors need to take certain parameters and hence be
	 * instanced in code.
	 */
	private void createProvidedWidgets(int time) {
		this.timer = new WlTimer(false);
		this.timer.updateTime(time);
		
		this.webcam = GWT.create(WlWebcam.class);
		
		final int refreshingTime = this.configurationRetriever.getIntProperty(WEBCAM_REFRESH_TIME_PROPERTY, DEFAULT_WEBCAM_REFRESH_TIME);
		this.webcam.setTime(refreshingTime);
	}

	@SuppressWarnings("unused")
	@UiHandler("upButton")
	public void onUpClick(ClickEvent event){
		sendMove(UP);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownClick(ClickEvent event){
		sendMove(DOWN);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("leftButton")
	public void onLeftClick(ClickEvent event){
		sendMove(LEFT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("rightButton")
	public void onRightClick(ClickEvent event){
		sendMove(RIGHT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("upButton")
	public void onUpMouseDown(MouseDownEvent event) {
		sendMove(UP);
		this.upPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownMouseDown(MouseDownEvent event) {
		sendMove(DOWN);
		this.downPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("leftButton")
	public void onLeftMouseDown(MouseDownEvent event) {
		sendMove(LEFT);
		this.leftPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("rightButton")
	public void onRightMouseDown(MouseDownEvent event) {
		sendMove(RIGHT);
		this.rightPressed = true;
	}

	@SuppressWarnings("unused")
	@UiHandler("upButton")
	public void onUpMouseUp(MouseUpEvent event) {
		this.upPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownMouseUp(MouseUpEvent event) {
		this.downPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("leftButton")
	public void onLeftMouseUp(MouseUpEvent event) {
		this.leftPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("rightButton")
	public void onRightMouseUp(MouseUpEvent event) {
		this.rightPressed = false;
	}

	
	private void enableButton(String button){
		this.buttons.get(button).setStyleName("wl-img-button");
	}
	
	private void disableButton(String button){
		this.buttons.get(button).setStyleName("wl-disabled-img-button");
	}
	
	private void enableButtons(){
		for(Image img : this.buttons.values())
			img.setStyleName("wl-img-button");
	}
	
	private void disableButtons(){
		for(Image img : this.buttons.values())
			img.setStyleName("wl-disabled-img-button");
	}

	void sendMove(final String s){
		if(!this.buttonsEnabled)
			return;
		
		disableButtons();
		enableButton(s);
		this.buttonsEnabled = false;
		final int currentMove = ++this.moveNumber;
		
		this.boardController.sendCommand("move:" + s, new IResponseCommandCallback() {
			
			@Override
			public void onFailure(CommException e) {
				
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				ControlPanel.this.buttonsEnabled = true;
				if(currentMove == ControlPanel.this.moveNumber){
					enableButtons();
					if(ControlPanel.this.upPressed) {
						sendMove(UP);
					} else if(ControlPanel.this.downPressed) {
						sendMove(DOWN);
					} else if(ControlPanel.this.rightPressed) {
						sendMove(RIGHT);
					} else if(ControlPanel.this.leftPressed) {
						sendMove(LEFT);
					}
				}else
					disableButton(s);
			}
		});
	}
	
}
