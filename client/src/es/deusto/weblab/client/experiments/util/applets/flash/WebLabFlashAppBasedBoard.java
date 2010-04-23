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

package es.deusto.weblab.client.experiments.util.applets.flash;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Element;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.experiments.util.applets.AbstractExternalAppBasedBoard;

public class WebLabFlashAppBasedBoard extends AbstractExternalAppBasedBoard{

	private final int width;
	private final int height;
	private final String swfFile;
	private final String flashvars;
	
	public WebLabFlashAppBasedBoard(IConfigurationManager configurationManager, IBoardBaseController boardController,
			String swfFile,
			int width,
			int height, 
			String flashvars,
			String message
	) {
		super(configurationManager, boardController);
		this.height  = height;
		this.width   = width;
		this.swfFile = GWT.getModuleBaseURL() + swfFile;
		this.flashvars = flashvars;
		this.message.setText(message);
		
		WebLabFlashAppBasedBoard.createJavaScriptCode(this.html.getElement(), this.swfFile, width + 10, height + 10);
	}

	/*
	 * We must create an iframe and inside this iframe build the flash object because Flash's ExternalInterface
	 * doesn't seem to work on Microsoft Internet Explorer (v8) if the flash object is dynamically created. Opera, 
	 * Chrome, Firefox performed well with the dynamically created flash object.
	 */
	private static native void createJavaScriptCode(Element element, String swfFile, int width, int height) /*-{
		var iFrameHtml   = "<iframe name=\"wlframe\" frameborder=\"0\"  vspace=\"0\"  hspace=\"0\"  marginwidth=\"0\"  marginheight=\"0\" " +
									"width=\"" + width + "\"  scrolling=\"no\"  height=\"" + height +  "\" " +
								"></iframe>";
		element.innerHTML = iFrameHtml;
		$wnd.wl_iframe    = element.getElementsByTagName('iframe')[0];
		$wnd.wl_inst  = null;
    }-*/;
	
	@Override
	public void initialize(){
		WebLabFlashAppBasedBoard.populateIframe(this.swfFile, this.width, this.height, this.flashvars);
	}

	@Override
	public void setTime(int time) {
		WebLabFlashAppBasedBoard.findFlashReference();
		AbstractExternalAppBasedBoard.setTimeImpl(time);
	}

	@Override
	public void start() {
		WebLabFlashAppBasedBoard.findFlashReference();
		AbstractExternalAppBasedBoard.startInteractionImpl();
	}
	
	@Override
	public void end() {
		WebLabFlashAppBasedBoard.findFlashReference();
		AbstractExternalAppBasedBoard.endImpl();
	}

	private static native void populateIframe(String swfFile, int width, int height, String flashvars) /*-{
		var doc = $wnd.wl_iframe.contentDocument;
    	if (doc == undefined || doc == null)
        	doc = $wnd.wl_iframe.contentWindow.document;
        
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
		    
		    alert("Flash does not seem to be reachable by your web browser. Contact the administrator saying what web browser you are using and this line: " + errorMessages);
		    throw "Flash does not seem to be working: " + errorMessages;
		}
		if($wnd.wl_inst == null){
			$wnd.wl_inst = getAndTestFlashObject();
		}
	}-*/;
}
