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
* Author: Luis Rodriguez Gil <zstars@gmail.com>
*         Pablo Orduña <pablo@ordunya.com>
*
*/

package es.deusto.weblab.client.lab.experiments.util.applets.flash;

import java.util.Date;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.Window;


import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard;

public class WebLabFlashAppBasedBoard extends AbstractExternalAppBasedBoard{

	public static final int WAIT_AFTER_START = 500;
	
	private final boolean deferred;
	
	private String swfFile;
	private String flashvars;
	
	
	// Time to wait for the flash app to load before we consider it has
	// failed. Though it has a default, it can be specified through the js config file 
	// for the experiment, and should often be higher for large flash files.
	private final int flashTimeout;
	
	// Timer to enforce the flash loading timeout.
	private Timer initializationTimer;
	
	// True if flash failed to start.
	private boolean startTimedOut = false;
	
	
	// We need to store the time set when we are in deferred mode.
	private int timeSet;
	
	/**
	 * Constructs a WeblabFlashAppBasedBoard. The flash applet is placed on the
	 * website immediately.
	 * 
	 * @param configurationRetriever Reference to the configuration manager.
	 * @param boardController Reference to the board controller.
	 * @param swfFile The path to the SWF file, including its name.
	 * @param width Width of the flash app.
	 * @param height Height of the flash app.
	 * @param flashvars String which will be passed to the flash app as its
	 * flashvars parameters.
	 * @param message Message to display.
	 */
	public WebLabFlashAppBasedBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController,
			String swfFile,
			int width,
			int height, 
			String flashvars,
			String message
	) {
		this(configurationRetriever, boardController, swfFile, width, height, flashvars, message, false);
	}
	
	
	/**
	 * Constructs a WeblabFlashAppBasedBoard. If deferFlashApp is set to true,
	 * the flash applet is not placed on the website until the experiment is
	 * started and hence the start() method is called.
	 * 
	 * @param configurationRetriever Reference to the configuration manager.
	 * @param boardController Reference to the board controller.
	 * @param swfFile The path to the SWF file, including its name. May be NULL, and set
	 * deferredly through setSwfFile instead (though only before the experiment starts).
	 * @param width Width of the flash app.
	 * @param height Height of the flash app.
	 * @param flashvars String which will be passed to the flash app as its
	 * flashvars parameters.
	 * @param message Message to display.
	 * @param deferFlashApp If true, the flash applet won't be placed until
	 * the experiment starts.
	 */
	public WebLabFlashAppBasedBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController,
			String swfFile,
			int width,
			int height, 
			String flashvars,
			String message,
			boolean deferFlashApp
	) {
		super(configurationRetriever, boardController, width, height);
		if(swfFile != null)
			this.swfFile = GWT.getModuleBaseURL() + swfFile;
		this.flashvars = flashvars;
		this.message.setText(message);
		this.deferred = deferFlashApp;
		

		this.flashTimeout = configurationRetriever.getIntProperty("flash.timeout", 10);
		
		WebLabFlashAppBasedBoard.createJavaScriptCode(this.html.getElement(), this.width+10, 0);
	}
	
	
	/**
	 * Sets the flashvars string. Once the iFrame has been populated, and the
	 * flashvars added to it, setting the flashvars will have no real effect.
	 * @param flashvars Flashvars string.
	 */
	public void setFlashVars(String flashvars) {
		this.flashvars = flashvars;
	}
	
	
	/**
	 * Sets or resets the swfFile to load.
	 * Takes no effect after the page has been populated (which is done on experiment start,
	 * if on deferred mode).
	 * @param swfFile Path to the swf file, relative to the gwt module base.
	 */
	public void setSwfFile(String swfFile) {
		this.swfFile = GWT.getModuleBaseURL() + swfFile;
	}
	
	
	/*
	 * We must create an iframe and inside this iframe build the flash object because Flash's ExternalInterface
	 * doesn't seem to work on Microsoft Internet Explorer (v8) if the flash object is dynamically created. Opera, 
	 * Chrome, Firefox performed well with the dynamically created flash object.
	 */
	private static native void createJavaScriptCode(Element element, int width, int height) /*-{
		var iFrameHtml   = "<iframe name=\"wlframe\" frameborder=\"0\"  vspace=\"0\"  hspace=\"0\"  marginwidth=\"0\"  marginheight=\"0\" " +
									"width=\"" + width + "\"  scrolling=\"no\"  height=\"" + height +  "\" " +
								"></iframe>";
		element.innerHTML = iFrameHtml;
		$wnd.wl_iframe    = element.getElementsByTagName('iframe')[0];
		$wnd.wl_inst  = null;
    }-*/;
	
	@Override
	public void initialize(){
		if(!this.deferred)
			WebLabFlashAppBasedBoard.populateIframe(this.swfFile, this.width, 
					this.height, this.width + 10, this.height + 10, this.flashvars);
	}

	@Override
	public void setTime(int time) {
		
		// Call required for the standard timer to work properly, if it is enabled.
		super.setTime(time);
		
		if(!this.deferred) {
			WebLabFlashAppBasedBoard.findFlashReference();
			AbstractExternalAppBasedBoard.setTimeImpl(time);
		} else {
			this.timeSet = time;
		}
	}
	
	@Override
	public void start() {
		
		if(this.deferred)
			WebLabFlashAppBasedBoard.populateIframe(this.swfFile, this.width, 
				this.height, this.width+10, this.height+10, this.flashvars);
		
		
		final long whenStarted = (new Date()).getTime();
		this.initializationTimer = new Timer() {
			
			@Override
			public void run() {
				try{
					WebLabFlashAppBasedBoard.findFlashReference();
				}catch(Exception e){
					
					final long ended = (new Date()).getTime();
					final long elapsed = ended - whenStarted;
					
					// Make sure we have not spent too much time waiting for flash to start
					if(elapsed > WebLabFlashAppBasedBoard.this.flashTimeout*1000){	
						WebLabFlashAppBasedBoard.this.startTimedOut = true;
						Window.alert("Flash does not seem to be reachable by your web browser. Contact the administrator saying what web browser you are using and this line: " + e.getMessage());
						e.printStackTrace();
					}else
						WebLabFlashAppBasedBoard.this.initializationTimer.schedule(WebLabFlashAppBasedBoard.WAIT_AFTER_START);
					return;
				}
				
				AbstractExternalAppBasedBoard.startInteractionImpl();
				AbstractExternalAppBasedBoard.setTimeImpl(WebLabFlashAppBasedBoard.this.timeSet);
			}
			
		};
		
		if(this.deferred)
			this.initializationTimer.schedule(WebLabFlashAppBasedBoard.WAIT_AFTER_START);
		else
			this.initializationTimer.schedule(1);
	}
	
	@Override
	public void end() {
		// Check that we were in fact able to access flash. Otherwise, it is pointless to
		// try to call the end function on it.
		if(!this.startTimedOut)  {
			WebLabFlashAppBasedBoard.findFlashReference();
			AbstractExternalAppBasedBoard.endImpl();
		}
	}

	private static native void populateIframe(String swfFile, int width, int height, int iframeWidth, int iframeHeight, String flashvars) /*-{
		var doc = $wnd.wl_iframe.contentDocument;
    	if (doc == undefined || doc == null)
        	doc = $wnd.wl_iframe.contentWindow.document;
        	
        $wnd.wl_iframe.height = iframeHeight;
        $wnd.wl_iframe.width = iframeWidth;
        
		var functionsHtml = "<script language=\"JavaScript\">\n" +
				"function wl_getIntProperty(name){ " +
					"return parent.wl_getIntProperty(name); " +
				"} \n" +
				"" +
				"function wl_getIntPropertyDef(name, defaultValue){ " +
					"return parent.wl_getIntPropertyDef(name, defaultValue); " +
				"} \n" +
				"" +
				"function wl_getProperty(name){ " +
					"return parent.wl_getProperty(name); " +
				"} \n" +
				"" +
				"function wl_getPropertyDef(name, defaultValue){ " +
					"return parent.wl_getPropertyDef(name, defaultValue); " +
				"} \n" +
				"" +
				"function wl_sendCommand(command, commandId){" + 
					"return parent.wl_sendCommand(command, commandId); " +
				"} \n" +
				"" +
				"function wl_onClean(){ " +
					"return parent.wl_onClean(); " +
				"} \n" +
				"</script>";
		var flashHtml    = "<object classid=\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\" type=\"application/x-shockwave-flash\" width=\"" + width + "\" height=\"" + height + "\" id=\"flashobj\">" + 
								"<param name=\"movie\" value=\"" + swfFile + "\" id\"flash_emb\"/>" + 
								"<embed src=\"" + swfFile + "\" width=\"" + width + "\" height=\"" + height + "\" flashvars=\"" + flashvars + "\"   />" + 
							"</object>";
		
		var completeHtml = "<html>" +
								"<head>" + functionsHtml + "</head>" +
								"<body>" + flashHtml + "</body>" +
							"</html>";
		
		doc.open();
		doc.write(completeHtml);
		doc.close();
	}-*/;
	
	private static native void findFlashReference()/*-{
		
		// Returns a reference to a flash object, whether it is an <object> or an <embed>. The <object> must have 'flash_obj' as id, 
		// and the <embed> 'flash_emb'. It uses flash testEcho to test the JS/Flash connection.
		function getAndTestFlashObject(){
			var doc = $wnd.wl_iframe.contentDocument;
	    	if (doc == undefined || doc == null)
	        	doc = $wnd.wl_iframe.contentWindow.document;
	        	
			$wnd.wl_flashobj   = doc.getElementsByTagName('object')[0];
			$wnd.wl_flashembed = doc.getElementsByTagName('embed')[0];
			
		    var errorMessages = "";
		
		    try{
		        var fl = $wnd.wl_flashobj;
		        var test = fl.testEcho('teststr');
		        if( test == 'teststr' )
		            return fl;
		        else
		            errorMessages = errorMessages + ' returned ' + test;
		    }catch(err){
		        errorMessages = errorMessages + '  raised ' + err + ' ' + err.description + ';';
		    }
		    
		    try{
		        var fl = $wnd.wl_flashembed;
		        var test = fl.testEcho('teststr');
		        if( test == 'teststr' )
		            return fl;
		        else
		            errorMessages = errorMessages + ' returned ' + test;
		    }catch(err){
		        errorMessages = errorMessages + ' raised ' + err + ' ' + err.description  + ';';
		    }
		    
		    throw "Flash does not seem to be working: " + errorMessages;
		}
		if($wnd.wl_inst == null){
			$wnd.wl_inst = getAndTestFlashObject();
		}
	}-*/;
}
