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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.binary.ui;

import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.commands.ClockActivationCommand;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.commands.PulseCommand;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.ui.XilinxExperiment;
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class BinaryExperiment extends ExperimentBase {

	public static final String BINARY_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.binary.webcam.image.url";
	public static final String DEFAULT_BINARY_WEBCAM_IMAGE_URL = "https://www.weblab.deusto.es/webcam/pld0/image.jpg";
	
	public static final String BINARY_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pld.webcam.refresh.millis";
	public static final int    DEFAULT_BINARY_WEBCAM_REFRESH_TIME       = 400;
	
	private static final int NUMBER_OF_SWITCHES = 4;
	private static final int CLOCK_ACTIVATOR_VALUE = 1000;
	private static final int BUTTON_NUMBER_TO_RESET = 3;
	private static final int BUTTON_NUMBER_TO_ASK_FOR_THE_NEXT_NUMBER = 2;
	private static final int BUTTON_NUMBER_CHECK_YOUR_NUMBER = 1;
	
	public static class Style{
		public static final String TIME_REMAINING         = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL = "wl-clock_activation_panel"; 
	}
	
	// Widgets
	private final VerticalPanel verticalPanel;
	private final VerticalPanel widget;
	private final List<Widget> interactiveWidgets;	
	private WlWebcam webcam;	
	private WlTimer timer;
	private WlWaitingLabel messages;	
	private WlSwitch [] switches;
	private Button nextNumberButton;
	private Button checkNumberButton;
	
	public BinaryExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		super(configurationRetriever, boardController);
		
		this.interactiveWidgets = new Vector<Widget>();
		
		this.widget = new VerticalPanel();
	    	this.widget.setWidth("100%");
	    	this.widget.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	    	
		this.verticalPanel = new VerticalPanel();
		this.verticalPanel.setWidth("100%");
		this.verticalPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.widget.add(this.verticalPanel);
	}
	
	protected String getWebcamImageUrl() {
		return this.configurationRetriever.getProperty(
				BinaryExperiment.BINARY_WEBCAM_IMAGE_URL_PROPERTY, 
				BinaryExperiment.DEFAULT_BINARY_WEBCAM_IMAGE_URL
			);
	}

	protected int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
				BinaryExperiment.BINARY_WEBCAM_REFRESH_TIME_PROPERTY, 
				BinaryExperiment.DEFAULT_BINARY_WEBCAM_REFRESH_TIME
			);
	}	
	
	@Override
	public void initialize(){	    	
		this.verticalPanel.setWidth("100%");
		this.verticalPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.verticalPanel.add(new Label("Welcome to the WebLab-Deusto Binnary Game!"));
		this.verticalPanel.add(new Label(""));
		this.verticalPanel.add(new Label("Practise your knowledge about binary code while getting points."));
	}
	
	@Override
	public void queued(){
	    	this.widget.setVisible(false);
	}

    @Override
    public void start(int time, String initialConfiguration) {
	this.widget.setVisible(true);
	this.loadWidgets();
	this.disableInteractiveWidgets();

	// 1. AutoProgram
	//this.boardController.sendCommand(new AutoProgramCommand(), new IResponseCommandCallback() {

	//	    @Override
	//	    public void onSuccess(ResponseCommand response) {
			BinaryExperiment.this.messages.stop();
			BinaryExperiment.this.messages.setText("Activating clock");
			BinaryExperiment.this.messages.start();

			// 2. Activate clock
			BinaryExperiment.this.boardController.sendCommand( new ClockActivationCommand(BinaryExperiment.CLOCK_ACTIVATOR_VALUE), new IResponseCommandCallback() {

					    @Override
					    public void onSuccess(ResponseCommand responseCommand) {
						BinaryExperiment.this.messages.stop();
						BinaryExperiment.this.messages.setText("Initializing game");
						BinaryExperiment.this.messages.start();

						// 3. Initialize the game (Press button 0)
						BinaryExperiment.this.boardController.sendCommand(new PulseCommand(BinaryExperiment.BUTTON_NUMBER_TO_RESET, true), new IResponseCommandCallback() {

								    @Override
								    public void onSuccess(ResponseCommand responseCommand) {
									BinaryExperiment.this.boardController.sendCommand(new PulseCommand(BinaryExperiment.BUTTON_NUMBER_TO_RESET, false), new IResponseCommandCallback() {

											    @Override
											    public void onSuccess(ResponseCommand responseCommand) {
												BinaryExperiment.this.messages.stop();
												BinaryExperiment.this.messages.setText("Game ready. Let's start!");
												BinaryExperiment.this.enableInteractiveWidgets();
												BinaryExperiment.this.nextNumberButton.setEnabled(true);
												BinaryExperiment.this.checkNumberButton.setEnabled(false);
											    }

											    @Override
											    public void onFailure(WlCommException e) {
												BinaryExperiment.this.messages.stop();
												BinaryExperiment.this.messages.setText("Error initializing (deactivating) the game: " + e.getMessage() + ". Please contact the WebLab-Deusto administrators at weblab@deusto.es");
											    }
											});
								    }

								    @Override
								    public void onFailure(WlCommException e) {
									BinaryExperiment.this.messages.stop();
									BinaryExperiment.this.messages.setText("Error initializing (activating) the game: " + e.getMessage() + ". Please contact the WebLab-Deusto administrators at weblab@deusto.es");
								    }
								});
					    }

					    @Override
					    public void onFailure(WlCommException e) {
						BinaryExperiment.this.messages.stop();
						BinaryExperiment.this.messages.setText("Error activating the clock: " + e.getMessage() + ". Please contact the WebLab-Deusto administrators at weblab@deusto.es");
					    }
					});
	//	    }

	//	    @Override
	//	    public void onFailure(WlCommException e) {
	//		WlDeustoBinaryBasedBoard.this.messages.stop();
	//		WlDeustoBinaryBasedBoard.this.messages.setText("Error autoprogramming the game: "+ e.getMessage() + ". Please contact the WebLab-Deusto administrators at weblab@deusto.es");
	//	    }
	//	});
    }
	
	private void loadWidgets() {

		while(this.verticalPanel.getWidgetCount() > 0)
		    this.verticalPanel.remove(0);	    

		final VerticalPanel otherVerticalPanel = new VerticalPanel();
		otherVerticalPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		otherVerticalPanel.setSpacing(15);

		// Webcam
		this.webcam = new WlWebcam(
			this.getWebcamRefreshingTime(),
			this.getWebcamImageUrl()
		);
		this.webcam.start();		
		otherVerticalPanel.add(this.webcam.getWidget());

		// Timer
		this.timer = new WlTimer();
		this.timer.setStyleName(XilinxExperiment.Style.TIME_REMAINING);
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    BinaryExperiment.this.boardController.clean();
			}
		});
		otherVerticalPanel.add(this.timer.getWidget());
		
		// Waiting label
		this.messages = new WlWaitingLabel("Programming Game");
		this.messages.start();
		otherVerticalPanel.add(this.messages.getWidget());
		
		// NextNumber button
		this.nextNumberButton = new Button("Ask a number");
		this.nextNumberButton.setEnabled(false);
		this.nextNumberButton.addClickHandler(new ClickHandler(){

		    @Override
		    public void onClick(ClickEvent event) {
			BinaryExperiment.this.boardController.sendCommand(new PulseCommand(BinaryExperiment.BUTTON_NUMBER_TO_ASK_FOR_THE_NEXT_NUMBER, true), new IResponseCommandCallback() {

			    @Override
			    public void onSuccess(ResponseCommand responseCommand) {
				BinaryExperiment.this.boardController.sendCommand(new PulseCommand(BinaryExperiment.BUTTON_NUMBER_TO_ASK_FOR_THE_NEXT_NUMBER, false), new IResponseCommandCallback() {

				    @Override
				    public void onSuccess(ResponseCommand responseCommand) {
					BinaryExperiment.this.messages.setText("Now you have to guess how to write that number in binary, turning on and off the different switches");
					BinaryExperiment.this.checkNumberButton.setEnabled(true);
					BinaryExperiment.this.nextNumberButton.setEnabled(false);					
				    }

				    @Override
				    public void onFailure(WlCommException e) {
					BinaryExperiment.this.messages.stop();
					BinaryExperiment.this.messages.setText("Error asking for another number (off): " + e.getMessage() + ". Please contact the WebLab-Deusto administrators at weblab@deusto.es");
				    }});
			    }

			    @Override
			    public void onFailure(WlCommException e) {
				BinaryExperiment.this.messages.stop();
				BinaryExperiment.this.messages.setText("Error asking for another number (on): " + e.getMessage() + ". Please contact the WebLab-Deusto administrators at weblab@deusto.es");
			    }});
		    }});
		this.addInteractiveWidget(this.nextNumberButton);
		otherVerticalPanel.add(this.nextNumberButton);
		
		// Switches
		this.switches = new WlSwitch[BinaryExperiment.NUMBER_OF_SWITCHES];
		for(int i = 0; i < BinaryExperiment.NUMBER_OF_SWITCHES; ++i){
			this.switches[i] = new WlSwitch();
			final IWlActionListener actionListener = new SwitchListener(6 + i, this.boardController, this.getResponseCommandCallback());
			this.switches[i].addActionListener(actionListener);
		}		
		final HorizontalPanel switchesPanel = new HorizontalPanel();
		switchesPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		switchesPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		switchesPanel.setSpacing(25);
		for(int i = 0; i < BinaryExperiment.NUMBER_OF_SWITCHES; ++i){
			this.switches[i].getWidget().setWidth("100%");			
			final VerticalPanel vp = new VerticalPanel();
			vp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
			vp.add(new Label("" + (BinaryExperiment.NUMBER_OF_SWITCHES - i - 1)));
			vp.add(this.switches[i].getWidget());
			switchesPanel.add(vp);
			this.addInteractiveWidget(vp);
		}
		
		// Check number button
		this.checkNumberButton = new Button("Check number!");
		this.checkNumberButton.setEnabled(false);
		this.checkNumberButton.addClickHandler(new ClickHandler(){

		    @Override
		    public void onClick(ClickEvent event) {
			BinaryExperiment.this.boardController.sendCommand(new PulseCommand(BinaryExperiment.BUTTON_NUMBER_CHECK_YOUR_NUMBER, true), new IResponseCommandCallback() {

			    @Override
			    public void onSuccess(ResponseCommand responseCommand) {
				BinaryExperiment.this.boardController.sendCommand(new PulseCommand(BinaryExperiment.BUTTON_NUMBER_CHECK_YOUR_NUMBER, false), new IResponseCommandCallback() {

				    @Override
				    public void onSuccess(ResponseCommand responseCommand) {
					BinaryExperiment.this.messages.setText("Press on 'Ask a number' to play again!");					
					BinaryExperiment.this.checkNumberButton.setEnabled(false);
					BinaryExperiment.this.nextNumberButton.setEnabled(true);					
				    }

				    @Override
				    public void onFailure(WlCommException e) {
					BinaryExperiment.this.messages.stop();
					BinaryExperiment.this.messages.setText("Error checking your number (off): " + e.getMessage() + ". Please contact the WebLab-Deusto administrators at weblab@deusto.es");
				    }});
			    }

			    @Override
			    public void onFailure(WlCommException e) {
				BinaryExperiment.this.messages.stop();
				BinaryExperiment.this.messages.setText("Error checking your number (on): " + e.getMessage() + ". Please contact the WebLab-Deusto administrators at weblab@deusto.es");
			    }});
		    }});
		this.addInteractiveWidget(this.checkNumberButton);
		switchesPanel.add(this.checkNumberButton);
		
		otherVerticalPanel.add(switchesPanel);
				
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
	
	protected IResponseCommandCallback getResponseCommandCallback(){
	    return new IResponseCommandCallback(){
		    @Override
			public void onSuccess(ResponseCommand responseCommand) {
			GWT.log("responseCommand: success", null);
		    }

		    @Override
			public void onFailure(WlCommException e) {
			GWT.log("responseCommand: failure", null);
		    }
		};	    
	}	
}
