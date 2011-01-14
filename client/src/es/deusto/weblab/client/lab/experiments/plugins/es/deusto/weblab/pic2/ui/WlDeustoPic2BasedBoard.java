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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pic2.ui;

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.commands.RequestWebcamCommand;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.IWlWidget;
import es.deusto.weblab.client.ui.widgets.WlPotentiometer;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

@SuppressWarnings("unqualified-field-access")
public class WlDeustoPic2BasedBoard extends BoardBase{
	
	protected static final boolean DEBUG_ENABLED = true;
	
	public static final String PIC_WEBCAM_REFRESH_TIME_PROPERTY = "webcam.refresh.millis";
	public static final int DEFAULT_PIC_WEBCAM_REFRESH_TIME = 400;
	

	protected IConfigurationRetriever configurationRetriever;

	private VerticalPanel widget;
	
	private WlWebcam webcam;
	private WlTimer timer;
	private WlWaitingLabel messages;
	private WlPotentiometer potentiometer;
	
	private UploadStructure uploadStructure;
	
	
	public WlDeustoPic2BasedBoard(IConfigurationRetriever configurationRetriever, final IBoardBaseController boardController){
		super(boardController);
		
		this.configurationRetriever = configurationRetriever;
		
		widget = new VerticalPanel();
		widget.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		int refreshTime = configurationRetriever.getIntProperty(PIC_WEBCAM_REFRESH_TIME_PROPERTY, DEFAULT_PIC_WEBCAM_REFRESH_TIME);
		
		webcam = new WlWebcam(refreshTime);
		timer = new WlTimer(false);
		timer.setTimerFinishedCallback(new IWlTimerFinishedCallback() {
			@Override
			public void onFinished() {
				boardController.onClean();
			}
		});
		messages = new WlWaitingLabel();
		potentiometer = new WlPotentiometer(10.0);
	}
	
	@Override
	public void initialize(){
		uploadStructure = new UploadStructure();
		uploadStructure.setFileInfo("program");
		widget.add(uploadStructure.getFormPanel());
		widget.add(messages);
	}
	
	@Override
	public void queued(){
	    widget.setVisible(false);
	}
	
	@Override
	public void start(){
		timer.start();
		webcam.start();
		
		uploadStructure.setVisible(false);
		
		widget.setVisible(true);
		widget.add(webcam);
		widget.add(timer);
		widget.add(potentiometer);
		potentiometer.addActionListener(new IWlActionListener() {
			
			@Override
			public void onAction(IWlWidget widget) {
				boardController.sendCommand("POTENTIOMETER: " + potentiometer.getPower(), new IResponseCommandCallback() {
					@Override
					public void onFailure(WlCommException e) {
						messages.setText("Error sending command POTENTIOMETER");
					}
					
					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						messages.setText("Returned: " + responseCommand.getCommandString());
					}
				});
			}
		});
		
		RequestWebcamCommand.createAndSend(boardController, webcam, messages);
		
		messages.setText("Sending file...");
		
		boardController.sendFile(uploadStructure, new IResponseCommandCallback() {
		    
		    @Override
		    public void onSuccess(ResponseCommand response) {
		    	messages.setText("Device ready");
		    	messages.stop();
		    }

		    @Override
		    public void onFailure(WlCommException e) {
		    	messages.setText("Error sending file: " + e.getMessage());
			    messages.stop();
		    }
		});
	}


	@Override
	public void end(){
		if(webcam != null){
			webcam.dispose();
			webcam = null;
		}		
		if(timer != null){
			timer.dispose();
			timer = null;
		}			
		
		messages.stop();	
	}	
	
	@Override
	public void setTime(int time) {
		timer.updateTime(time);
	}
	
	@Override
	public Widget getWidget() {
		return widget;
	}	
}
