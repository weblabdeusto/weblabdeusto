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

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.visir;

import com.google.gwt.http.client.URL;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard;
import es.deusto.weblab.client.lab.experiments.util.applets.flash.WebLabFlashAppBasedBoard;

public class VisirFlashBoard extends WebLabFlashAppBasedBoard {
	
	
	private String cookie = null;
	private String url = null;
	private String savedata = null;

	/**
	 * Constructs a Board for the Visir client. It does not actually generate the
	 * full HTML code until the experiment is started (and hence Start called), as
	 * it uses the WebLabFlashAppBasedBoard's deferred mode.
	 * 
	 * @param configurationRetriever
	 * @param boardController
	 */
	public VisirFlashBoard(IConfigurationRetriever configurationRetriever,
			IBoardBaseController boardController) {
		super(configurationRetriever, boardController, "", 800, 500,
				 "",
				 "Visir Flash Experiment", true);
	}
	
	@Override
	public void end() {
		super.end();
	}

	@Override
	public void initialize() {
		super.initialize();
	}

	@Override
	public void setTime(int time) {
		super.setTime(time);
	}

	@Override
	public void start() {
		
		// Request the visir session "cookie" to the server.
		final VisirSetupDataRequestCommand reqData = new VisirSetupDataRequestCommand();
		AbstractExternalAppBasedBoard.boardController.sendCommand(reqData, 
				new IResponseCommandCallback() {

					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						
						// Use the command's helper method to parse the JSON response
						boolean success = reqData.parseResponse(responseCommand.getCommandString());
						
						if(success) {
							VisirFlashBoard.this.cookie = reqData.getCookie();
							VisirFlashBoard.this.savedata = reqData.getSaveData();
							VisirFlashBoard.this.url = reqData.getURL();
						
							VisirFlashBoard.this.updateFlashVars();
							VisirFlashBoard.this.setSwfFile(VisirFlashBoard.this.url);
							
							VisirFlashBoard.super.start();
						} else {
							System.out.println("Could not parse response: " + responseCommand.getCommandString());
						}
					}

					@Override
					public void onFailure(WlCommException e) {
						System.out.println("Error: Could not retrieve data");
						VisirFlashBoard.super.start();
					}
				}
		);
		
		//super.start();
		
	}

	/**
	 * Will set or update the flash vars with local parameters such as cookie or savedata.
	 * These parameters should be set beforehand. Flashvars updates have no effect once the iframe containing
	 * the flash object has been populated.
	 * Note that savedata is assumed to be URL-encoded.
	 */
	protected void updateFlashVars() {
		//final String testsavedata = "<save><instruments+list=\"breadboard/breadboard.swf|multimeter/multimeter.swf|functiongenerator/functiongenerator.swf|oscilloscope/oscilloscope.swf|tripledc/tripledc.swf\"+/><multimeter+/><circuit><circuitlist><component>R+1.6k+52+26+0</component><component>R+2.7k+117+26+0</component><component>R+10k+182+78+0</component><component>R+10k+182+52+0</component><component>R+10k+182+26+0</component><component>C+56n+247+39+0</component><component>C+56n+247+91+0</component></circuitlist></circuit></save>&amp;http=1<save><instruments+list=\"breadboard/breadboard.swf|multimeter/multimeter.swf|functiongenerator/functiongenerator.swf|oscilloscope/oscilloscope.swf|tripledc/tripledc.swf\"+/><multimeter+/><circuit><circuitlist><component>R+1.6k+52+26+0</component><component>R+2.7k+117+26+0</component><component>R+10k+182+78+0</component><component>R+10k+182+52+0</component><component>R+10k+182+26+0</component><component>C+56n+247+39+0</component><component>C+56n+247+91+0</component></circuitlist></circuit></save>";
		
		// Data is received encoded through Python, decoded, and encoded again. This avoids certain
		// encoding issues that seem to be occurring. We enable teacher mode so that the
		// plus sign that gives us access to the full component palette is available.
		final String decodedSaveData = URL.decodeQueryString(this.savedata);
		String flashvars = "teacher=1";
		if(this.cookie != "")
			flashvars += "&cookie="+this.cookie;
		if(this.savedata != "")
			flashvars += "&savedata="+URL.encode(decodedSaveData);
		
		// Data is received encoded, and used to generate the website straightaway.
		//final String flashvars = "cookie="+this.cookie+"&savedata="+this.savedata;
		
		//System.out.println(this.savedata);
		//System.out.println(URL.decodeComponent(this.savedata));
		
		this.setFlashVars(flashvars);
	}
}
