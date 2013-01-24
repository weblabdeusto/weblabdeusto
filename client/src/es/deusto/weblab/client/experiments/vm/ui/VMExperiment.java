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
* 		  Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.experiments.vm.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarListener;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.TextProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class VMExperiment extends ExperimentBase {
	
	private static final String DEFAULT_VNC_HEIGHT = "900";
	private static final String DEFAULT_VNC_WIDTH  = "1152";

	private static final String VNC_WIDTH  = "vnc.width";
	private static final String VNC_HEIGHT = "vnc.height";

	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface VMBoardUiBinder extends UiBinder<Widget, VMExperiment> {
	}

	private static final VMBoardUiBinder uiBinder = GWT.create(VMBoardUiBinder.class);
	
	private static final int IS_READY_QUERY_TIMER = 1000;

	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
	}

	// Root panel.
	@UiField VerticalPanel widget;
	
	@UiField WlWaitingLabel messages;
	@UiField Label url;
	@UiField VerticalPanel applets;
	
	@UiField WlPredictiveProgressBar progressBar;

	@UiField(provided = true) WlTimer timer;
	
	private Timer readyTimer;
	private String fullURLPassword = "";
	private String protocol = "";
	
	private boolean progressBarRun = false;
	private boolean vmReady = false;
	
	
	public VMExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.createProvidedWidgets();
		
		VMExperiment.uiBinder.createAndBindUi(this);
	}
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    VMExperiment.this.boardController.clean();
			}
		});
		this.timer.start();
		
		this.progressBar.setVisible(true);
		
		
		this.readyTimer = new Timer() {
			@Override
			public void run() {
				final Command command = new Command() {
					@Override
					public String getCommandString() {
						return "is_ready";
					}
				};
				
				VMExperiment.this.boardController.sendCommand(command, new IResponseCommandCallback() {
					@Override
					public void onFailure(CommException e) {
						VMExperiment.this.setMessage("There was an error while trying to find out whether the Virtual Machine is ready");
						
						VMExperiment.this.progressBar.setTextUpdater(new IProgressBarTextUpdater() {
							@Override
							public String generateText(double progress) {
								return "Error: Server not available";
							}} );
						if(VMExperiment.this.progressBar.isWaiting()){
							VMExperiment.this.progressBar.stop();
							VMExperiment.this.progressBar.setVisible(false);
						}else{
							// Will automatically remove itself once it reaches 100%, when the
							// finished callback gets called.
							VMExperiment.this.progressBar.finish(300);
						}
					}
					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						
						// Read the full message returned by the exp server and ensure it's not empty
						final String resp = responseCommand.getCommandString();
						if(resp.length() == 0) 
							VMExperiment.this.setMessage("The is_ready query returned an empty result");
						
						// It may come with an argument, in the format <code>;<arg>,
						// so we split it to retrieve the <code> and the <arg>.
						final String [] codeSplit = resp.split(";", 2);
						final String codeStr;
						if(codeSplit.length == 0)
							codeStr = resp;
						else
							codeStr = codeSplit[0];
						
						final String argStr;
						if(codeSplit.length >= 2)
							argStr = codeSplit[1];
						else
							argStr = "";
						
						
						if(codeStr.equals("0")) {
							// Not ready
							VMExperiment.this.setMessage(i18n.yourVirtualMachineIsNotYetReady(argStr));
							VMExperiment.this.readyTimer.schedule(IS_READY_QUERY_TIMER);
							
							if(!VMExperiment.this.progressBar.isRunning() && !VMExperiment.this.progressBarRun) {
								
								VMExperiment.this.progressBarRun = true;
								final double estimatedSeconds = Double.parseDouble(argStr);
								VMExperiment.this.progressBar.setEstimatedTime((int) (estimatedSeconds * 1000));
								VMExperiment.this.progressBar.setResolution(40);
								VMExperiment.this.progressBar.setWaitPoint(0.98);
								
								// The progress bar will automatically disappear as soon as it
								// is full.
								VMExperiment.this.progressBar.setListener(new IProgressBarListener(){
									@Override
									public void onFinished() {
										if(VMExperiment.this.vmReady){
											VMExperiment.this.progressBar.setVisible(false);
										}else{
											VMExperiment.this.progressBar.keepWaiting();
											VMExperiment.this.progressBar.setTextUpdater(new TextProgressBarTextUpdater(i18n.finishing() + "..."));
										}
									}});
								
								VMExperiment.this.progressBar.setTextUpdater(new IProgressBarTextUpdater() {
									
									@Override
									public String generateText(double progress) {
										
										final long elapsed = VMExperiment.this.progressBar.getElapsedTime();
										
										if(elapsed > 1000 * (estimatedSeconds + 1)) {
											return i18n.finishing() + "...";
										} 
										
										if(progress == 1) {
											return i18n.doneVMisReady();
										}
										
										return i18n.loadingPleaseWait((int)(progress*100));
									}} );
								
								VMExperiment.this.progressBar.start();
								
							}
							
						} else if(codeStr.equals("1")) {
							VMExperiment.this.vmReady = true;
							// Ready
							VMExperiment.this.setMessage(i18n.yourVirtualMachineIsNowReady());
							if(VMExperiment.this.protocol.equals("vnc"))
								loadVNCApplet();
							
							if(VMExperiment.this.progressBar.isWaiting()){
								VMExperiment.this.progressBar.stop();
								VMExperiment.this.progressBar.setVisible(false);
							}else{
								// Will automatically remove itself once it reaches 100%, when the
								// finished callback gets called.
								VMExperiment.this.progressBar.finish(300);
							}
							
						} else {
							VMExperiment.this.vmReady = true;
							// Unexpected answer
							VMExperiment.this.setMessage("Received unexpected response to the is_ready query");
							
							VMExperiment.this.progressBar.setTextUpdater(new IProgressBarTextUpdater() {
								@Override
								public String generateText(double progress) {
									return "Error: Unexpected reply";
								}} );
							if(VMExperiment.this.progressBar.isWaiting()){
								VMExperiment.this.progressBar.stop();
								VMExperiment.this.progressBar.setVisible(false);
							}else{
								// Will automatically remove itself once it reaches 100%, when the
								// finished callback gets called.
								VMExperiment.this.progressBar.finish(300);
							}
						}
					}
				});
			}
		};
		
		// We do not do a Repeating schedule because we want to wait for a response before asking again
		this.readyTimer.schedule(IS_READY_QUERY_TIMER);
	}
	
	private void loadVNCApplet(){
		this.applets.clear();
		final Anchor anchor = new Anchor(i18n.loadJavaVNCApplet());
		this.applets.add(anchor);
		
		final String archive = GWT.getModuleBaseURL() + "vnc/tightvncviewer.jar";
		final String code = "VncViewer.class";
		
		final String width  = this.configurationRetriever.getProperty(VNC_WIDTH,  DEFAULT_VNC_WIDTH);
		final String height = this.configurationRetriever.getProperty(VNC_HEIGHT, DEFAULT_VNC_HEIGHT);
		
		final String [] tokens = this.fullURLPassword.split(" ");
		// "vnc://host:port/   with password:  asdf"
		final String hostPort = tokens[0].split("//")[1].split("/")[0];
		final String host;
		final String port;
		if(hostPort.indexOf(":") >= 0){
			host = hostPort.split(":")[0];
			port = hostPort.split(":")[1];
		}else{
			host = hostPort;
			port = "5900"; // standard default VNC port
		}
		final String password = tokens[tokens.length - 1];
		
		anchor.addClickHandler(new ClickHandler() {
			@Override
			public void onClick(ClickEvent event) {
				VMExperiment.this.applets.clear();
				final HTML appletHTML = new HTML();
				appletHTML.setHTML("<applet archive='" + archive + "' " + 
		        		"code='" + code + "' " + 
		        		"width='" + width + "' " +  
		        		"height='" + height + "' " +
		        		"> " +
		        		"<PARAM NAME=\"PORT\" VALUE=\"" + port + "\"> " +
		        		"<PARAM NAME=\"HOST\" VALUE=\"" + host + "\"> " +
		        		"<PARAM NAME=\"PASSWORD\" VALUE=\"" + password + "\"> " +	
		        	"</applet>");
				VMExperiment.this.applets.add(appletHTML);
			}
		});
	}
	
	/* Creates those widgets that are placed through UiBinder but
	 * whose ctors need to take certain parameters and hence be
	 * instanced in code.
	 */
	private void createProvidedWidgets() {
		this.timer = new WlTimer(false);	
	}
	

	/**
	 * The initialize function gets called on the "reserve" stage,
	 * before the experiment starts.
	 */
	@Override
	public void initialize(){
	}	
	
	
	/**
	 * This function gets called just when the actual experiment starts, after
	 * the reserve is done and the queue is over.
	 */
	@Override
	public void start(int time, String initialConfiguration) {
	    this.widget.setVisible(true);
	    
	    this.setupWidgets();
	    
	    this.setMessage("Obtaining VM config...");
	    
	    this.sendGetConfigurationCommand();
	    
	    this.progressBarRun = false;
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
		if(this.timer != null){
			this.timer.dispose();
			this.timer = null;
		}			
		if(this.progressBar != null)
			this.progressBar.stop();
	}
	
	public void setMessage(String msg) {
		this.messages.setText(msg);
	}
	
	private void sendGetConfigurationCommand(){
		final Command command = new Command() {
			@Override
			public String getCommandString() {
				return "get_configuration";
			}
		};
		
		this.boardController.sendCommand(command, new IResponseCommandCallback() {
			@Override
			public void onFailure(CommException e) {
				VMExperiment.this.setMessage("It was not possible to obtain the VM configuration");
			}
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				VMExperiment.this.setMessage(i18n.vmAddress());
				VMExperiment.this.url.setText(responseCommand.getCommandString());
				VMExperiment.this.protocol = responseCommand.getCommandString().split(":")[0].toLowerCase();
				VMExperiment.this.fullURLPassword = responseCommand.getCommandString();
			}
		});
	}
	
}
