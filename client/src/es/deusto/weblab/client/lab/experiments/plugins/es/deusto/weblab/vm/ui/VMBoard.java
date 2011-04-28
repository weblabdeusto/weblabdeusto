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
* 		  Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.vm.ui;

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

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.ui.WlDeustoXilinxBasedBoard;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarListener;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.TextProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class VMBoard extends BoardBase {
	
	private static final String DEFAULT_VNC_HEIGHT = "900";
	private static final String DEFAULT_VNC_WIDTH  = "1152";

	private static final String VNC_WIDTH  = "vnc.width";
	private static final String VNC_HEIGHT = "vnc.height";

	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface VMBoardUiBinder extends UiBinder<Widget, VMBoard> {
	}

	private static final VMBoardUiBinder uiBinder = GWT.create(VMBoardUiBinder.class);
	
	private static final int IS_READY_QUERY_TIMER = 1000;

	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
	}

	private final IConfigurationRetriever configurationRetriever;
	
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
	
	
	public VMBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(commandSender);
		
		this.configurationRetriever = configurationRetriever;
		
		this.createProvidedWidgets();
		
		VMBoard.uiBinder.createAndBindUi(this);
	}
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    VMBoard.this.boardController.onClean();
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
				
				VMBoard.this.boardController.sendCommand(command, new IResponseCommandCallback() {
					@Override
					public void onFailure(WlCommException e) {
						VMBoard.this.setMessage("There was an error while trying to find out whether the Virtual Machine is ready");
						
						VMBoard.this.progressBar.setTextUpdater(new IProgressBarTextUpdater() {
							@Override
							public String generateText(double progress) {
								return "Error: Server not available";
							}} );
						if(VMBoard.this.progressBar.isWaiting()){
							VMBoard.this.progressBar.stop();
							VMBoard.this.progressBar.setVisible(false);
						}else{
							// Will automatically remove itself once it reaches 100%, when the
							// finished callback gets called.
							VMBoard.this.progressBar.finish(300);
						}
					}
					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						
						// Read the full message returned by the exp server and ensure it's not empty
						final String resp = responseCommand.getCommandString();
						if(resp.length() == 0) 
							VMBoard.this.setMessage("The is_ready query returned an empty result");
						
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
							VMBoard.this.setMessage("Your Virtual Machine is not yet ready. Please, wait. It often takes around " + argStr + " seconds.");
							VMBoard.this.readyTimer.schedule(IS_READY_QUERY_TIMER);
							
							if(!VMBoard.this.progressBar.isRunning() && !VMBoard.this.progressBarRun) {
								
								VMBoard.this.progressBarRun = true;
								final double estimatedSeconds = Double.parseDouble(argStr);
								VMBoard.this.progressBar.setEstimatedTime((int) (estimatedSeconds * 1000));
								VMBoard.this.progressBar.setResolution(40);
								VMBoard.this.progressBar.setWaitPoint(0.9);
								
								// The progress bar will automatically disappear as soon as it
								// is full.
								VMBoard.this.progressBar.setListener(new IProgressBarListener(){
									@Override
									public void onFinished() {
										if(VMBoard.this.vmReady){
											VMBoard.this.progressBar.setVisible(false);
										}else{
											VMBoard.this.progressBar.keepWaiting();
											VMBoard.this.progressBar.setTextUpdater(new TextProgressBarTextUpdater("Finishing..."));
										}
									}});
								
								VMBoard.this.progressBar.setTextUpdater(new IProgressBarTextUpdater() {
									
									@Override
									public String generateText(double progress) {
										
										final long elapsed = VMBoard.this.progressBar.getElapsedTime();
										
										if(elapsed > 1000 * (estimatedSeconds + 1)) {
											VMBoard.this.setMessage("Setting up the VM is taking longer than expected. There might be some problem.");
											return "Taking longer than expected.";
										} 
										
										if(progress == 1) {
											return "Done. VM is ready";
										}
										
										return "Loading, please wait (" + (int)(progress*100) + "%)";
									}} );
								
								VMBoard.this.progressBar.start();
								
							}
							
						} else if(codeStr.equals("1")) {
							VMBoard.this.vmReady = true;
							// Ready
							VMBoard.this.setMessage("Your Virtual Machine is now ready!");
							if(VMBoard.this.protocol.equals("vnc"))
								loadVNCApplet();
							
							if(VMBoard.this.progressBar.isWaiting()){
								VMBoard.this.progressBar.stop();
								VMBoard.this.progressBar.setVisible(false);
							}else{
								// Will automatically remove itself once it reaches 100%, when the
								// finished callback gets called.
								VMBoard.this.progressBar.finish(300);
							}
							
						} else {
							VMBoard.this.vmReady = true;
							// Unexpected answer
							VMBoard.this.setMessage("Received unexpected response to the is_ready query");
							
							VMBoard.this.progressBar.setTextUpdater(new IProgressBarTextUpdater() {
								@Override
								public String generateText(double progress) {
									return "Error: Unexpected reply";
								}} );
							if(VMBoard.this.progressBar.isWaiting()){
								VMBoard.this.progressBar.stop();
								VMBoard.this.progressBar.setVisible(false);
							}else{
								// Will automatically remove itself once it reaches 100%, when the
								// finished callback gets called.
								VMBoard.this.progressBar.finish(300);
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
		final Anchor anchor = new Anchor("Load Java applet VNC Client");
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
				VMBoard.this.applets.clear();
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
				VMBoard.this.applets.add(appletHTML);
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
	public void start() {
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
			public void onFailure(WlCommException e) {
				VMBoard.this.setMessage("It was not possible to obtain the VM configuration");
			}
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				final String msg = "VM address:";
				VMBoard.this.setMessage(msg);
				VMBoard.this.url.setText(responseCommand.getCommandString());
				VMBoard.this.protocol = responseCommand.getCommandString().split(":")[0].toLowerCase();
				VMBoard.this.fullURLPassword = responseCommand.getCommandString();
			}
		});
	}
	
}
