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
* Author: Luis Rodriguez Gil <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.lab.experiments.util.applets.js;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Button;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard;



public class JSExperiment extends AbstractExternalAppBasedBoard {
	
	
	private String file;
	private boolean isJSFile;
	private boolean provideFileUpload;
	private Button uploadButton;
	
	private final UploadStructure uploadStructure;
	
	/**
	 * Constructs a JSExperiment.
	 * 
	 * @param configurationRetriever Reference to the configuration manager.
	 * @param boardController Reference to the board controller.
	 */
	public JSExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController, String file, boolean isJSFile, int width, int height, boolean provideFileUpload) 
	{
		super(configurationRetriever, boardController, width, height);
		
		this.uploadButton = new Button(ExperimentBase.i18n.upload());
		this.file = file;
		this.isJSFile = isJSFile;
		this.provideFileUpload = provideFileUpload;
		
		if(!this.isJSFile)
		{
			// If it seems to be a relative address, preppend the module base.
			if(!this.file.trim().startsWith("http://") && !this.file.trim().startsWith("https://"))
				this.file = GWT.getModuleBaseURL() + this.file;
		}
		
		this.uploadStructure = new UploadStructure();
		
		
		this.uploadButton.addClickHandler(new ClickHandler() {
			@Override
			public void onClick(ClickEvent event) {
				@SuppressWarnings("unused")
				final boolean success = JSExperiment.this.tryUpload();
				
				// Originally, the ud-fpga experiment only lets the user upload once.
				// For now however, in this experiment we will let the user upload
				// several times.
				//if(success)
				//	this.uploadButton.setVisible(false);
			}});
		
		
		if(this.provideFileUpload) {
			GWT.log("Creating upload structure");
			this.uploadStructure.setFileInfo("program");
			this.fileUploadPanel.add(this.uploadStructure.getFormPanel());
			this.fileUploadPanel.add(this.uploadButton);
		} else {
			GWT.log("NOT creating upload structure");
		}
		
		JSExperiment.createJavaScriptCode(this.html.getElement(), this.file, this.isJSFile, this.width+10, this.height);
	}
	
	private static native void createJavaScriptCode(Element element, String file, boolean isJSFile, int width, int height) /*-{
		
		var divHtml = "<div id=\"div_extra\"></div>";	
		
		$wnd.wl_inst = {}; // This is the object that will contain the in-javascript callbacks.
	
		if(isJSFile)
		{	
			var iFrameHtml = "<iframe name=\"wlframe\" frameborder=\"0\" allowfullscreen webkitallowfullscreen mozzallowfullscreen  vspace=\"0\"  hspace=\"0\"  marginwidth=\"0\"  marginheight=\"0\" " +
										"width=\"" + width + "\"  scrolling=\"no\"  height=\"" + height +  "\" " +
									"></iframe>";
		}
		else
		{
			var iFrameHtml = "<iframe name=\"wlframe\" frameborder=\"0\"  allowfullscreen webkitallowfullscreen mozallowfullscreen vspace=\"0\"  hspace=\"0\"  marginwidth=\"0\"  marginheight=\"0\" " +
										"width=\"" + width + "\"  scrolling=\"no\"  height=\"" + height +  "\" " +
									"src=\"" + file + "\"" + "></iframe>"; 
		}
		
		element.innerHTML = iFrameHtml + divHtml;
		$wnd.wl_div_extra = $doc.getElementById('div_extra');
		$wnd.wl_iframe    = element.getElementsByTagName('iframe')[0];

}-*/;
	
	/**
	 * Populates the iframe that will host the JS experiment. This is only used when a JS file is used as
	 * a base for the experiment. If an HTML file is used, the whole file is used straightaway to populate 
	 * it, and this method is not invoked.
	 * @param file This is the file that describes the experiment. It is a JS script, which is
	 * included within an iframe.
	 * 
	 * TODO: Probably there is currently no need to separate kinds of width/height.
	 * Probably, a set of height/width should be removed.
	 * 
	 * @param isJS Specifies whether the file is an HTML file or a JS script.
	 * @param width 
	 * @param height 
	 * @param iframeWidth 
	 * @param iframeHeight
	 */
	private static native void populateIframe(String file, boolean isJS, int width, int height, int iframeWidth, int iframeHeight) /*-{
		var doc = $wnd.wl_iframe.contentDocument;
		if (doc == undefined || doc == null)
	    	doc = $wnd.wl_iframe.contentWindow.document;
	    	
	    $wnd.wl_inst = {};
	    $wnd.wl_inst.handleCommandResponse = function(a, b) { $doc.wlframe.onHandleCommandResponse(a, b);};
	    $wnd.wl_inst.handleCommandError = function(a, b) { $doc.wlframe.onHandleCommandError(a, b);};
	    
	    $wnd.wl_iframe.height = iframeHeight;
	    $wnd.wl_iframe.width = iframeWidth;
	    
	    var libsinc = "\n<script language=\"JavaScript\" src=\"jslib/three.min.js\"></script>\n";
	    
	    var scriptinc = "\n<script language=\"JavaScript\" src=\"" + file + "\"></script>\n";
	    
	    var metasHtml = "";
	
		var weblabjsScript = "<script src=\"jslib/weblabjs.js\">";
				
							
		var completeHtml = "<html>" +
								"<head>" + metasHtml + weblabjsScript + libsinc + scriptinc"</head>" +
								"<body></body>" +
							"</html>";
		
		doc.open();
		doc.write(completeHtml);
		doc.close();
	}-*/;
	
	
	/**
	 * Called by the WebLab server to tell the experiment
	 * how much time it has available.¡
	 * 
	 * @param time Time available, in seconds.
	 */
	@Override
	public void setTime(int time) {
		super.setTime(time);
		AbstractExternalAppBasedBoard.setTimeImpl(time);
	}
	
    @Override
    public void end() {
    	AbstractExternalAppBasedBoard.endImpl();
    }
	
	@Override
	/**
	 * Called on initialization.
	 */
	public void initialize() {
		
		// We will only populate the iframe if we chose to use a JS file as base for the experiment.
		// If we're using an HTML, the HTML file itself will populate the iframe, and the stub that
		// the population method uses is hence no longer required.
		if(this.isJSFile)
		{
			JSExperiment.populateIframe(this.file, this.isJSFile, this.width, 
					this.height, this.width + 10, this.height + 10);
		}
	}
	
	/**
	 * Called by the WebLab server to tell the experiment that it is
	 * meant to start.
	 * Internally, it calls the base classes' startInteractionImpl to 
	 * refer the call to the JS file.
	 */
	@Override
	public void start(int time, String initialConfiguration) {
		if(this.provideFileUpload)
			tryUpload();
		
		AbstractExternalAppBasedBoard.startInteractionImpl();
	}
	
	
	public static native void wlSendCommand()/*-{
		alert('test');
	}-*/;
	
	
	private final IResponseCommandCallback sendFileCallback = new IResponseCommandCallback() {
	    
	    @Override
	    public void onSuccess(ResponseCommand response) {
	    	GWT.log("The file was sent");
	    	handleFileResponse(response.getCommandString(), 0);
	    }

	    @Override
	    public void onFailure(CommException e) {
	    	GWT.log("It was not possible to send the file");
	    	handleFileError(e.getMessage(), 0);
	    }
	    
	};	
	
	
	/**
	 * Helper method to try to upload a file. Currently, we only consider that an upload
	 * failed if the filename the user chose is empty.
	 * If the upload succeeds we load the standard experiment controls through loadStartControls and
	 * hide the upload panel, which is no longer needed.
	 * 
	 * @return True if the upload succeeds, false otherwise.
	 */
	private boolean tryUpload() {
		final boolean didChooseFile = !this.uploadStructure.getFileUpload().getFilename().isEmpty();
		
		if(didChooseFile) {
			// Extract the file extension.
			final String filename = this.uploadStructure.getFileUpload().getFilename();
			final String [] split = filename.split("\\.");
			String extension;
			if(split.length == 0)
				extension = "bit"; // BIT as default
			extension = split[split.length-1];
			
			this.uploadStructure.getFormPanel().setVisible(false);
			this.uploadStructure.setFileInfo(extension.toLowerCase());
			
			// TODO: Probably it would be more elegant if the server itself would decide whether we are synthesizing
			// and programming or just programming. However, at least for now, this will do fine. The mode is currently
			// used only to decide how to estimate progress bar length.
			//if(extension.toLowerCase().equals("vhd"))
			//	this.synthesizingMode = true;
			
			GWT.log("Now trying to send file");
			
			this.boardController.sendFile(this.uploadStructure, this.sendFileCallback);
			
			GWT.log("sendFile was run");
			
			//this.loadStartControls();
		} else {
			GWT.log("The user did not really choose a file");
		}
		
		return didChooseFile;
	}
	
}
