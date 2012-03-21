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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.ui.widgets;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Widget;

public class WlWebcamSafariBased extends WlWebcam {
	
	private static enum WebcamFormat {
		jpeg,
		mjpeg
	}
	
	private static Map<WebcamFormat, String> NAMES = new HashMap<WebcamFormat, String>();
	
	static {
		NAMES.put(WebcamFormat.jpeg, "jpg");
		NAMES.put(WebcamFormat.mjpeg, "video (mjpeg)");
		
		if(NAMES.size() != WebcamFormat.values().length)
			System.err.println("Error: missing value for " + WebcamFormat.class.getName());
	}
	
	private WebcamFormat currentWebcam = WebcamFormat.jpeg;
	private WebcamFormat lastWebcam    = WebcamFormat.jpeg;
	private final HorizontalPanel choicePanel;
	
	public WlWebcamSafariBased(){
		this(WlWebcam.DEFAULT_REFRESH_TIME, WlWebcam.DEFAULT_IMAGE_URL);
	}
	
	public WlWebcamSafariBased(int time){
		this(time, WlWebcam.DEFAULT_IMAGE_URL);
	}
	
	public WlWebcamSafariBased(int time, String url){
		this(time, url, WlWebcam.DEFAULT_IMAGE_URL);
	}
	
	public WlWebcamSafariBased(int time, String url, String streamingUrl){
		super(time, url, streamingUrl);

		this.choicePanel = new HorizontalPanel();
		this.choicePanel.setWidth("160px");
		this.choicePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.add(this.choicePanel);
	}
	
	@Override
	public void dispose(){
		this.running = false;
		
		if(this.timer != null)
			this.timer.cancel();
		
		this.timer = null;
	}
	
	@Override
	public void setVisible(boolean visible){
		super.setVisible(visible);
		this.image.setVisible(visible);
	}
	
	@Override
	public void reload(){
		if(this.running){
			switch(this.currentWebcam) {
				case jpeg:
					ensureJpeg();
					reloadJpeg();
					break;
				case mjpeg:
					reloadMJpeg();
					break;
			}
			this.lastWebcam = this.currentWebcam;
		}
	}
	
	private void ensureJpeg() {
		if(this.lastWebcam != WebcamFormat.jpeg) {
			this.imagePanel.clear();
			this.image = new Image();
			this.imagePanel.add(this.image);
		}
	}

	private void reloadMJpeg() {
		if(this.lastWebcam != WebcamFormat.mjpeg) {
			this.imagePanel.clear();
			final HTML html = new HTML();
			html.setHTML("<div/>");
			this.imagePanel.add(html);
			createJavaScriptCode(html.getElement(), this.streamingWidth, this.streamingHeight, this.streamingUrl);
			System.out.println(html.getHTML());
		}
	}
	
	private static native void createJavaScriptCode(Element element, int width, int height, String imageUrl) /*-{
		var iFrameHtml   = "<iframe name=\"wlframe\" frameborder=\"0\"  vspace=\"0\"  hspace=\"0\"  marginwidth=\"0\"  marginheight=\"0\" " +
									"width=\"" + width + "\"  scrolling=\"no\"  height=\"" + height + "\" " +
								"></iframe>";
		element.innerHTML = iFrameHtml;
		var wl_iframe    = element.getElementsByTagName('iframe')[0];
		
		var doc = wl_iframe.contentDocument;
    	if (doc == undefined || doc == null)
        	doc = wl_iframe.contentWindow.document;
        	
        var completeHtml = "<html>" +
								"<head></head>" +
								"<body><img id=\"webcam\" src=\"" + imageUrl + "\"/></body>" +
							"</html>";
        doc.open();
		doc.write(completeHtml);
		doc.close();
	}-*/;

	@Override
	protected void reloadPanel() {
		reloadPanel(null);
	}
	
	private void reloadPanel(WebcamFormat format) {
		final List<WebcamFormat> possibleFormats = new Vector<WebcamFormat>();
		if(this.url != DEFAULT_IMAGE_URL) {
			possibleFormats.add(WebcamFormat.jpeg);
		}
		if(this.streamingUrl != DEFAULT_IMAGE_URL) {
			possibleFormats.add(WebcamFormat.mjpeg);
		}

		if(format != null)
			this.currentWebcam = format;
		else if(possibleFormats.size() > 0)
			this.currentWebcam = possibleFormats.get(0);
		
		this.choicePanel.clear();
		if(possibleFormats.size() > 1) {
			for(final WebcamFormat webcam : possibleFormats) {
				final Widget anchor;
				if(webcam.equals(this.currentWebcam)) {
					anchor = new HTML("<b>" + NAMES.get(webcam) + "</b>");
				} else {
					anchor = new Anchor(NAMES.get(webcam));
					((Anchor)anchor).addClickHandler(new ClickHandler() {
						@Override
						public void onClick(ClickEvent event) {
							reloadPanel(webcam);
						}
					});
				}
				this.choicePanel.add(anchor);
			}
		}
		reload();
		if(this.image.getWidth() > 0)
			this.choicePanel.setWidth((this.image.getWidth() / 2) + "px");
	}
}
