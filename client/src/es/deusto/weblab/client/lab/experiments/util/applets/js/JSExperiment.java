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

import com.google.gwt.user.client.Element;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.util.applets.AbstractExternalAppBasedBoard;



public class JSExperiment extends AbstractExternalAppBasedBoard {
	
	
	private String jsfile;
	private String htmlfile;

	
	/**
	 * Constructs a JSExperiment.
	 * 
	 * @param configurationRetriever Reference to the configuration manager.
	 * @param boardController Reference to the board controller.
	 */
	public JSExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController, String jsfile, String htmlfile, int width, int height) 
	{
		super(configurationRetriever, boardController, width, height);
		
		this.jsfile = jsfile;
		this.htmlfile = htmlfile;
		JSExperiment.createJavaScriptCode(this.html.getElement(), this.width+10, 0);
	}
	
	private static native void createJavaScriptCode(Element element, int width, int height) /*-{
	var iFrameHtml   = "<iframe name=\"wlframe\" frameborder=\"0\"  vspace=\"0\"  hspace=\"0\"  marginwidth=\"0\"  marginheight=\"0\" " +
								"width=\"" + width + "\"  scrolling=\"no\"  height=\"" + height +  "\" " +
							"></iframe>";
	var divHtml = "<div id=\"div_extra\"></div>";
	element.innerHTML = iFrameHtml + divHtml;
	$wnd.wl_div_extra = $doc.getElementById('div_extra');
	$wnd.wl_iframe    = element.getElementsByTagName('iframe')[0];
	$wnd.wl_inst = {}; // This is the object that will contain the in-javascript callbacks.
}-*/;
	
	/**
	 * Populates the iframe that will host the JS experiment.
	 * @param file This is the file that describes the experiment. It can either be an HTML, 
	 * which will generally contain or reference several JS scripts, or a JS script, which will
	 * be embedded into a generic HTML stub.
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
	    var scriptinc = "\n<script language=\"JavaScript\" src=\"" + jsfile + "\"></script>\n";
	    
	//    var metasHtml = "<meta http-Equiv=\"Cache-Control\" Content=\"no-cache\">\n" +
	//						"<meta http-Equiv=\"Pragma\" Content=\"no-cache\">\n" +
	//						"<meta http-Equiv=\"Expires\" Content=\"0\">\n\n";
	    var metasHtml = "";
	
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
				"" +
				"function onHandleCommandResponse(a, b) { alert(a); } \n" +
				"function onHandleCommandError(a, b) { alert(a); } \n" +
				"</script>";
				
							
		var completeHtml = "<html>" +
								"<head>" + metasHtml + functionsHtml + libsinc + scriptinc"</head>" +
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
		JSExperiment.populateIframe(this.jsfile, this.width, 
				this.height, this.width + 10, this.height + 10);
	}
	
	/**
	 * Called by the WebLab server to tell the experiment that it is
	 * meant to start.
	 * Internally, it calls the base classes' startInteractionImpl to 
	 * refer the call to the JS file.
	 */
	@Override
	public void start(int time, String initialConfiguration) {
		AbstractExternalAppBasedBoard.startInteractionImpl();
	}
	
	
	public static native void wlSendCommand()/*-{
		alert('test');
	}-*/;
	
}
