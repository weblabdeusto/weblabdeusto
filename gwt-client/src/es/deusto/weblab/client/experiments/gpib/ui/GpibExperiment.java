/*
* Copyright (C) 2005 onwards University of Deusto
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
package es.deusto.weblab.client.experiments.gpib.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.experiments.gpib.commands.PollCommand;
import es.deusto.weblab.client.experiments.gpib.commands.ResultCodeCommand;
import es.deusto.weblab.client.experiments.gpib.commands.ResultFileCommand;
import es.deusto.weblab.client.experiments.gpib.commands.ResultStderrCommand;
import es.deusto.weblab.client.experiments.gpib.commands.ResultStdoutCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;


public class GpibExperiment extends ExperimentBase {
	
	
	/******************
	 * UIBINDER RELATED
	 ******************/

	interface WlDeustoGpibBoardUiBinder extends UiBinder<Widget, GpibExperiment> {
	}

	static final WlDeustoGpibBoardUiBinder uiBinder = GWT.create(WlDeustoGpibBoardUiBinder.class);

	
	
	
	public static final String GPIB_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.gpib.webcam.image.url";
	public static final String DEFAULT_GPIB_WEBCAM_IMAGE_URL       = "http://gpib.weblab.deusto.es/cliente/camview.jpg";
	
	public static final String GPIB_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.gpib.webcam.refresh.millis";
	public static final int    DEFAULT_GPIB_WEBCAM_REFRESH_TIME       = 400;
	
	public static final String GPIB_USER_GUIDE_LINK_PROPERTY_NAME = "es.deusto.weblab.gpib.userguide.link";
	public static final String DEFAULT_GPIB_USER_GUIDE_LINK       = "https://www.weblab.deusto.es/help/gpib-user-guide.pdf";
		
	public static class Style{
		public static final String TIME_REMAINING         = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL = "wl-clock_activation_panel"; 
	}
	
	
	// Widgets
	private final VerticalPanel widget;
	private final VerticalPanel removableWidgetsPanel;
	private WlWebcam webcam;
	private WlTimer timer;
	private WlWaitingLabel messages;
	private UploadStructure uploadStructure;
	private Timer pollingTimer = null;

	// DTOs
	private Command lastCommand = null;
	private String resultFileContent = "";
	private String resultStdout = "";
	private String resultStderr = "";
	
	private final IResponseCommandCallback commandCallback = new IResponseCommandCallback(){

	    @Override
		public void onSuccess(ResponseCommand responseCommand) {
		GpibExperiment.this.processCommandSent(responseCommand);		    
	    }

	    @Override
		public void onFailure(CommException e) {
		GpibExperiment.this.messages.setText("Error: " + e.getMessage() + ". Please, notify the WebLab-Deusto administrators at weblab@deusto.es about this error.");
	    }
	};
	
	public GpibExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.widget = new VerticalPanel();
		this.widget.setWidth("100%");
		this.widget.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.removableWidgetsPanel = new VerticalPanel();
		this.removableWidgetsPanel.setWidth("100%");
		this.removableWidgetsPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.removableWidgetsPanel.setSpacing(20);
	}
		
	@Override
	public void initialize(){
	    	this.removableWidgetsPanel.add(new HTML("<a href='" + GpibExperiment.DEFAULT_GPIB_USER_GUIDE_LINK + "' alt='GPIB User Guide'>User Guide</a>"));
	    
		this.removableWidgetsPanel.add(new Label("Select the program to send:"));
		
		this.uploadStructure = new UploadStructure();
		this.uploadStructure.setFileInfo("program");
		
		this.widget.add(this.removableWidgetsPanel);
		this.widget.add(this.uploadStructure.getFormPanel());
	}	
	
	@Override
	public void queued(){
	    	this.widget.setVisible(false);
	}	
	
	@Override
	public void start(int time, String initialConfiguration) {
	    	this.widget.setVisible(true);
		
		while(this.removableWidgetsPanel.getWidgetCount() > 0)
		    this.removableWidgetsPanel.remove(0);
		
	    	// Webcam
		this.webcam = new WlWebcam(this.getWebcamRefreshingTime(), this.getWebcamImageUrl());
		this.webcam.start();
		this.removableWidgetsPanel.add(this.webcam.getWidget());
		
		// Timer
		this.timer = new WlTimer();
		this.timer.setStyleName(GpibExperiment.Style.TIME_REMAINING);
		this.timer.getWidget().setWidth("30%");
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
				GpibExperiment.this.boardController.clean();
			}
		});
		this.removableWidgetsPanel.add(this.timer.getWidget());
		
		// Messages
		this.messages = new WlWaitingLabel("Sending message");
		this.messages.start();
		this.removableWidgetsPanel.add(this.messages.getWidget());

		this.uploadStructure.getFormPanel().setVisible(false);
		
		this.boardController.sendFile(this.uploadStructure, new IResponseCommandCallback() {
		    
		    @Override
		    public void onSuccess(ResponseCommand response) {
			GpibExperiment.this.messages.setText("File compiled, executing file...");
			GpibExperiment.this.messages.stop();			
			GpibExperiment.this.sendCommand(new PollCommand());			
		    }

		    @Override
		    public void onFailure(CommException e) {
			GpibExperiment.this.messages.setText("Error sending file: " + e.getMessage());
		    }
		});  
	}	
	
	@Override
	public void setTime(int time) {
		this.timer.updateTime(time);
	}

	@Override
	public Widget getWidget() {
		return this.widget;
	}

	@Override
	public void end() {
		if(this.pollingTimer != null)
			this.pollingTimer.cancel();		
		if(this.webcam != null){
			this.webcam.dispose();
			this.webcam = null;
		}	
		if(this.timer != null){
			this.timer.dispose();
			this.timer = null;
		}
		if(this.messages != null){
			this.messages.dispose();
			this.messages = null;
		}
	}
	
	private String getWebcamImageUrl() {
		return this.configurationRetriever.getProperty(
				GpibExperiment.GPIB_WEBCAM_IMAGE_URL_PROPERTY, 
				this.getDefaultWebcamImageUrl()
			);
	}
	
	protected String getDefaultWebcamImageUrl(){
		return GpibExperiment.DEFAULT_GPIB_WEBCAM_IMAGE_URL;
	}

	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
				GpibExperiment.GPIB_WEBCAM_REFRESH_TIME_PROPERTY, 
				GpibExperiment.DEFAULT_GPIB_WEBCAM_REFRESH_TIME
			);
	}

	private void sendCommand(Command command){
		this.lastCommand = command;
		this.boardController.sendCommand(command, this.commandCallback);
	}
	
	private void processCommandSent(ResponseCommand responseCommand){
		
		if ( this.lastCommand instanceof PollCommand ){
			final String response = responseCommand.getCommandString();
			if ( response.substring(0, 2).equals("OK") ){
			    	this.pollingTimer = null;
				this.messages.setText("File executed, retrieving results...");
				this.sendCommand(new ResultCodeCommand());
			} else {
				this.pollingTimer = new Timer(){
					@Override
					public void run(){
						GpibExperiment.this.sendCommand(new PollCommand());
						GpibExperiment.this.pollingTimer = null;
					}
				};
				this.pollingTimer.schedule(500);
			}
		}else if ( this.lastCommand instanceof ResultCodeCommand ){
			this.sendCommand(new ResultStdoutCommand());
		}else if ( this.lastCommand instanceof ResultStdoutCommand ){
			this.sendCommand(new ResultStderrCommand());
			this.resultStdout = responseCommand.getCommandString();
		}else if ( this.lastCommand instanceof ResultStderrCommand ){
			this.sendCommand(new ResultFileCommand());
			this.resultStderr = responseCommand.getCommandString();
		}else if ( this.lastCommand instanceof ResultFileCommand ){
			this.messages.setText("");
			final String code = responseCommand.getCommandString().substring(0, 2);
			final String text = responseCommand.getCommandString().substring(2);
			if ( code.equals("OK") ){
				this.resultFileContent = text;
			}else{
				this.resultFileContent = "Error: Your program did not generate the required file.";
			}

			this.boardController.clean();
			this.showResults();
		}else{
			// TODO: Unknown command!
		}
	}

	private void showResults()
	{
		final PopupPanel popup = new PopupPanel(false, true);
		
		popup.setStyleName("results-popup");
		
		final VerticalPanel mainPanel = new VerticalPanel();
		mainPanel.setWidth("100%");
		mainPanel.setSpacing(10);
		
			final Label title = new Label("Your experiment's results");
			title.setStyleName("results-title");
			mainPanel.add(title);
			mainPanel.setCellHorizontalAlignment(title, HasHorizontalAlignment.ALIGN_CENTER);
			
			final TextArea textAreaFileResult = new TextArea();
			textAreaFileResult.setText(this.resultFileContent);
			textAreaFileResult.setVisibleLines(15);
			textAreaFileResult.setWidth("100%");
			mainPanel.add(textAreaFileResult);
		
			final VerticalPanel stdoutPanel = new VerticalPanel();
				final Label stdoutLabel = new Label("stdout:");
				stdoutLabel.setStyleName("results-label");
				stdoutPanel.add(stdoutLabel);
					final TextArea textAreaStdout  = new TextArea();
					textAreaStdout.setVisibleLines(8);
					textAreaStdout.setText(this.resultStdout);
					textAreaStdout.setSize("100%", "100%");
					stdoutPanel.add(textAreaStdout);
					stdoutPanel.setWidth("100%");						
			mainPanel.add(stdoutPanel);
			
			final VerticalPanel stderrPanel = new VerticalPanel();
				final Label stderrLabel = new Label("stderr:");
				stderrLabel.setStyleName("results-label");
				stderrPanel.add(stderrLabel);
					final TextArea textAreaStderr  = new TextArea();
					textAreaStderr.setVisibleLines(4);
					textAreaStderr.setText(this.resultStderr);
					textAreaStderr.setSize("100%", "100%");
					stderrPanel.add(textAreaStderr);
					stderrPanel.setWidth("100%");
			mainPanel.add(stderrPanel);

			final HorizontalPanel buttonPanel = new HorizontalPanel();
			buttonPanel.setSpacing(10);
			buttonPanel.setSize("100%", "100%");
			
				final Button button = new Button("Close");
				button.addClickHandler(new ClickHandler(){
				    @Override
					public void onClick(ClickEvent event) {
					popup.hide();
				    }
				});
				buttonPanel.add(button);
				buttonPanel.setCellHorizontalAlignment(button, HasHorizontalAlignment.ALIGN_CENTER);
			mainPanel.add(buttonPanel);
		popup.setWidget(mainPanel);
		popup.show();
	}
}
