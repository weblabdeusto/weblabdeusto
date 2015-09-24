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
* Author: Luis Rodríguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.experiments.commands;

import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class RequestWebcamCommand extends Command{
	
	public RequestWebcamCommand(){

	}
	
	@Override
	public String getCommandString() {
		return "WEBCAMURL"; 
	}
	
	/**
	 * Retrieves the webcam URL from the response to the RequestWebcam command.
	 * Note: The webcam request command follows the following format:
	 * WEBCAMURL=http://www.whatever/webcam
	 * 
	 * @param requestResponse String containing the response to the command
	 * @return Webcam URL. Null if the string can't be parsed.
	 */
	public static String retrieveWebcamURL(String requestResponse) {
		final int eqsign = requestResponse.indexOf("=");
		if(eqsign == -1)
			return null;
		final String url = requestResponse.substring(eqsign+1);
		return url;
	}
	
	/**
	 * Helper method which creates a RequestWebcamCommands and sends it, 
	 * updating by itself the webcam if it is successful or setting an error 
	 * message if not.
	 *
	 * @param boardController Reference to the board controller to send
	 * the command through.
	 * @param webcam Reference to the wecam whose URL should be set.
	 * @param messages Reference to the label which will display the 
	 * error message, if any. If null, no error message will be set.
	 */
	public static void createAndSend(IBoardBaseController boardController, final WlWebcam webcam, final Label messages) {
		
		final RequestWebcamCommand command = new RequestWebcamCommand();
		
		boardController.sendCommand(command,
				new IResponseCommandCallback() {

					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						final String url = RequestWebcamCommand.retrieveWebcamURL(responseCommand.getCommandString());
						if(url != null && url.length() > 0) {
							webcam.setUrl(url);
						}
					}

					@Override
					public void onFailure(CommException e) {
						if(messages != null)
							messages.setText("Failed to obtain the webcam URL");
					}
				}
		);
		
	}
	
	
}
