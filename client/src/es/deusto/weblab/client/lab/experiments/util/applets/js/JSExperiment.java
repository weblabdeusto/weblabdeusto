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
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.json.client.JSONParser;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard;




public class JSExperiment extends AbstractExternalAppBasedBoard {
	
	//! To store the file name and to identify whether it's an HTML or a JS script.
	private String file;
	private boolean isJSFile;
	
	//! To handle file uploading, in case it is enabled in the config.
	private boolean provideFileUpload;
	private Button uploadButton;
	
	private final UploadStructure uploadStructure;
	
	//! This is used to keep a static reference to the last created instance of this class. 
	//! It is particularly ugly, but should work as expected because there shouldn't be more
	//! than a single active JSExperiment class at once. 
	//! It is needed because apparently only static GWT methods can be invoked from JavaScript.
	//! If a way to invoke non-static methods from JavaScript is ever found, it could probably
	//! be removed.
	private static JSExperiment staticSelf;
	
	//! These are used to track the experiment state. Particularly, to know what is its loading
	//! state so that start() can be invoked appropriately.
	private boolean frameLoaded = false; // The frame has finished loading.
	private boolean startRequested = false; // Start requested but should only be carried out if the frame has finished loading.
	
	//! The following two variables are used to temporarily store the data to pass to start()
	//! when the real start() execution (through doStart) is deferred because the iframe
	//! has not yet finished loading.
	int startTime;
	String startInitialConfiguration;

    //! The following two variables are used to store the width and height of the iframe. Though most experiments of
    //! this kind traditionally had an int width and height, the JS case is special because we can (and it is
    //! useful to) use css-style widths and heights.
    private String cssWidth;
    private String cssHeight;
	
	/**
	 * Constructs a JSExperiment.
	 * 
	 * @param configurationRetriever Reference to the configuration manager.
	 * @param boardController Reference to the board controller.
	 */
	public JSExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController, String file, boolean isJSFile, String cssWidth, String cssHeight, boolean provideFileUpload)
	{
        // Width and height passed to this parent class are actually unused in this case.
        // This is so that we can support css-style width and height.
		super(configurationRetriever, boardController, 100, 100);

        this.cssWidth = cssWidth;
        this.cssHeight = cssHeight;
		
		printLine("[DBG]: Creating JSExperiment: " + this);
		
		JSExperiment.staticSelf = this;
		
		exportIframeLoadListener();
		
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
		System.out.println(this.cssWidth);
		final String realCssHeight = this.cssHeight.equals("auto")?"300px":this.cssHeight;
		JSExperiment.createJavaScriptCode(this.html.getElement(), this.file, this.isJSFile, this.cssWidth, realCssHeight);
	}


	/**
	 * This is invoked when reserve is requested to provide the initial data to the client.
	 */
	@Override
	public JSONValue getInitialData() {	
        printLine("[DBG]: getInitialData called");
        final String valToRet = getInitialDataImpl();
	    return JSONParser.parse(valToRet);
	}

	/**
	 * To indicate whether we require a post-end or not.
	 */
	@Override
	public boolean expectsPostEnd() {
	    return expectsPostEndImpl();
	}
	
	

	/** This callback will be invoked when the Iframe finished loading.
	 * It is invoked indirectly from JavaScript. To do so, it relies
	 * on the static reference to the active object of this class 
	 * that is always kept.
	 */
	public static void onIframeLoaded() {
		if (staticSelf.cssHeight.equals("auto"))
			runIframeResizer();
		else
			System.out.println("cssHeight not set to auto. Not running iframeResizer");
		
		printLine("[DBG] The iframe finished loading. " + staticSelf);
		
		staticSelf.frameLoaded = true;
	
		// If startRequested is true, then the start() method has already
		// been invoked, but we weren't able to really() start because the
		// frame hadn't been loaded yet. We will do it now.
		if(staticSelf.startRequested) {
			printLine("[DBG]: Start had been requested. We will doStart next.");
			staticSelf.doStart(staticSelf.startTime, staticSelf.startInitialConfiguration);
			
			// Important to set startRequested to false, so that this method can be freely
			// invoked more than once without ill-effect. (A fake load can be forced from
			// the JavaScript library, for convenience).
			staticSelf.startRequested = false;
		}
	}


	/**
	 * Provides the JavaScript implementation for the function to call the JS-client-defined callback to
	 * provide the initial data for the experiment.
	 */
	protected static native String getInitialDataImpl() /*-{
                console.log("IN: getInitialDataImpl");
		var getInitialData = $wnd.wl_inst.getInitialData;

		if(getInitialData !== undefined)
        	    var retval = getInitialData();
                if(retval === undefined)
                    return "{}";
        	if(typeof(retval) !== 'string')
        	    retval = JSON.stringify(retval);
                console.log("RETURNING: getInitialDataImpl");
                console.log(retval);
        	return retval;

        return "";
	}-*/;

	/**
	 * In this case it provides the JS implementation that returns true if it expects a PostEnd and
	 * false otherwise. The WeblabJS library itself will handle this transparently. If a postEnd callback
	 * (known in JS as onFinished) exists, then this will be true.
	 */
	protected static native boolean expectsPostEndImpl() /*-{
		var expectsPostEnd = $wnd.wl_inst.expectsPostEnd;

		if(expectsPostEnd !== undefined)
			return expectsPostEnd();

		return false;
	}-*/;



	
	
	/**
	 * Exports the IframeLoadListener to JavaScript. That is, the JS 
	 * method through which JavaScript will tell GWT that the Iframe finished loading.
	 */
	private static native void exportIframeLoadListener() /*-{
		$wnd.onFrameLoad = $entry(@es.deusto.weblab.client.lab.experiments.util.applets.js.JSExperiment::onIframeLoaded());
	}-*/;
	
	private static native void runIframeResizer() /*-{
		$wnd.iFrameResize({
        	log : false,
        	enablePublicMethods : true,
    	}, "#wlframe");
	}-*/;
	
	private static native void createJavaScriptCode(Element element, String file, boolean isJSFile, String width, String height) /*-{
		
		var divHtml = "<div id=\"div_extra\"></div>";	
		
		$wnd.wl_inst = {}; // This is the object that will contain the in-javascript callbacks.
	
		var iFrameHtml = "<iframe id=\"wlframe\" name=\"wlframe\" frameborder=\"0\" allowfullscreen webkitallowfullscreen mozzallowfullscreen  vspace=\"0\"  hspace=\"0\"  marginwidth=\"0\"  marginheight=\"0\" " +
							"width=\"" + width + "\"  scrolling=\"auto\"  height=\"" + height +  "\" " +
										"onLoad=\"onFrameLoad();\"";
		if(!isJSFile)
			iFrameHtml = iFrameHtml + "src=\"" + file + "\"";
			 
		iFrameHtml = iFrameHtml + "></iframe>";
		
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
	private static native void populateIframe(String file, String iframeWidth, String iframeHeight) /*-{
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
	 * how much time it has available.
	 * 
	 * @param time Time available, in seconds.
	 */
	@Override
	public void setTime(int time) {
		super.setTime(time);
		
		printLine("[DBG]: setTime callback invoked on GWT with time: " + time);
		
		AbstractExternalAppBasedBoard.setTimeImpl(time);
	}
	
    @Override
    public void end() {
    	AbstractExternalAppBasedBoard.endImpl();
    }

    @Override
    public void postEnd(String initialData, String endData) {
    	postEndImpl(endData);
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
			JSExperiment.populateIframe(this.file, this.cssWidth, this.cssHeight);
		}
	}
	
	/**
	 * This method is the one that carries the real start. It will invoke
	 * the startInteraction JavaScript callback internally. It is 
	 * REQUIRED that the startInteraction be registered before invoking
	 * this method.
	 * @param time
	 * @param initialConfiguration
	 */
	public void doStart(int time, String initialConfiguration) {
		
		printLine("[DBG]: Carrying out doStart() [This is the real start]");
		printLine("[DBG]: Time: " + time);
		printLine("[DBG]: initConfig: " + initialConfiguration);
		
		if(this.provideFileUpload)
			tryUpload();
		
		// TODO: Ensure that this is called only once.
		// Added as an attempt for a bugfix.
		AbstractExternalAppBasedBoard.setTimeImpl(time);
		AbstractExternalAppBasedBoard.startInteractionImpl(initialConfiguration);
		
		printLine("[DBG]: DoStart done.");
	}
	
	/**
	 * Called by the WebLab server to tell the experiment that it is
	 * meant to start. It will however only start for real if the frame has already loaded.
	 * Otherwise, it would fail, because the code executed within the frame is the one that
	 * registers the startInteraction callback.
	 */
	@Override
	public void start(int time, String initialConfiguration) {
		
		printLine("[DBG]: Carrying out start() [Maybe we will really start, or defer it]" + this);
		
		// If the frame has been loaded, we're ready to start.
		if(this.frameLoaded)
			this.doStart(time, initialConfiguration);
		
		// If the frame has not been loaded, we're not yet ready.
		// We store the arguments, and wait for the onReady callback, 
		// which will in this case call us.
		else {
			printLine("[DBG]: Storing start data for later.");
			this.startTime = time;
			this.startInitialConfiguration = initialConfiguration;
			this.startRequested = true;
			
			printLine("[DBG]: Stored start data: " + initialConfiguration);
			printLine("[DBG]: Stored start time: " + this.startTime);
		}
	}
	
	
	/**
	* Prints a line through both System.out.println and native console.log and GWT.log.
	*/
	public static void printLine( String line ) {
		System.out.println(line);
		consoleLog(line);
		GWT.log(line);
	}
	
	public static native void consoleLog( String message) /*-{
		try {
			console.log( "[GDBG]:" + message );
		} catch (e) {
		}
	}-*/;

	protected static native void postEndImpl( String endData ) /*-{
		$wnd.wl_inst.finished(endData);
	}-*/;
	
	
	public static native void wlSendCommand()/*-{
		alert('test');
	}-*/;
	
	
	private final IResponseCommandCallback sendFileCallback = new IResponseCommandCallback() {
	    
	    @Override
	    public void onSuccess(ResponseCommand response) {
	    	printLine("The file was sent");
	    	handleFileResponse(response.getCommandString(), 0);
	    }

	    @Override
	    public void onFailure(CommException e) {
	    	printLine("It was not possible to send the file");
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
			
			printLine("Now trying to send file");
			
			this.boardController.sendFile(this.uploadStructure, this.sendFileCallback);
			
			printLine("sendFile was run");
			
			//this.loadStartControls();
		} else {
			printLine("The user did not really choose a file");
		}
		
		return didChooseFile;
	}
	
}
