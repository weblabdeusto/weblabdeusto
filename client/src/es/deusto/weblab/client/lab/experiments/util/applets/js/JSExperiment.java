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
import es.deusto.weblab.client.lab.experiments.util.applets.flash.FlashExperiment;



public class JSExperiment extends AbstractExternalAppBasedBoard {

	
	/**
	 * Constructs a JSExperiment.
	 * 
	 * @param configurationRetriever Reference to the configuration manager.
	 * @param boardController Reference to the board controller.
	 * flashvars parameters.
	 */
	public JSExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController, int width, int height) 
	{
		super(configurationRetriever, boardController, width, height);
		
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
	$wnd.wl_inst  = null;
}-*/;
	
	private static native void populateIframe(String swfFile, int width, int height, int iframeWidth, int iframeHeight, String flashvars) /*-{
		var doc = $wnd.wl_iframe.contentDocument;
		if (doc == undefined || doc == null)
	    	doc = $wnd.wl_iframe.contentWindow.document;
	    	
	    $wnd.wl_inst = {};
	    $wnd.wl_inst.handleCommandResponse = function(a, b) { $doc.wlframe.onHandleCommandResponse(a, b);};
	    $wnd.wl_iframe.height = iframeHeight;
	    $wnd.wl_iframe.width = iframeWidth;
	    
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
				"</script>";
		// Important: this must be the first <div> element
		var flashHtml    = "<div id=\"wl_flashobj_container\"><object id=\"wl_flashobj\" classid=\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\" type=\"application/x-shockwave-flash\" width=\"" + width + "\" height=\"" + height + "\" id=\"flashobj\">" + 
								"<param name=\"movie\" value=\"" + swfFile + "\" id=\"flash_emb\"/>" + 
								"<param name=\"flashvars\" value=\"" + flashvars + "\"/>" + 
								"<embed type=\"application/x-shockwave-flash\" src=\"" + swfFile + "\" width=\"" + width + "\" height=\"" + height + "\" flashvars=\"" + flashvars + "\"   />" + 
							"</object></div>";
							
		var other		= "<div id=\"div_iframe_extra\"></div>";
		
		var completeHtml = "<html>" +
								"<head>" + metasHtml + functionsHtml + "</head>" +
								"<body>" + flashHtml + other + "</body>" +
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
	}
	
	@Override
	/**
	 * Called on initialization.
	 */
	public void initialize() {
		JSExperiment.populateIframe("oo.swf", this.width, 
				this.height, this.width + 10, this.height + 10, "");
	}
	
	/**
	 * Called by the WebLab server to tell the experiment that it is
	 * meant to start.
	 */
	@Override
	public void start(int time, String initialConfiguration) {
		
	}
	
	public static native void wlSendCommand()/*-{
		alert('test');
	}-*/;
	
}
