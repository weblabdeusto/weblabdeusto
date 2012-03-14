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

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.widgets.exceptions.WlWidgetException;

public class WlClockActivator extends HorizontalPanel implements IWlWidget{

	private final HorizontalPanel horizontalPanel;
	private final WlNumberChooser numberChooser;
	private final Button activate;
	private final Button deactivate;
	
	public interface IWlClockActivationListener{
		public void onActivate(int value);
		public void onDeactivate();
	}
	
	public interface IWlClockActivationErrorHandler{
		public void onError(Throwable t);
	}
	
	private IWlClockActivationListener listener;
	private IWlClockActivationErrorHandler errorHandler;
	
	@Override
	public void setWidth(String width) {
		super.setWidth(width);
		
		this.horizontalPanel.setWidth(width);
		this.horizontalPanel.setSpacing(25);
	}
	
	public WlClockActivator(){
		super();
		
		this.horizontalPanel = new HorizontalPanel();
		
		this.setWidth("100%");
		this.add(this.horizontalPanel);
		
		this.numberChooser = new WlNumberChooser(Integer.class);
		
		this.activate = new Button();
		this.deactivate = new Button();
		
		this.activate.addClickHandler(new ClickHandler(){
			@Override
			public void onClick(ClickEvent sender) {
				if(WlClockActivator.this.listener != null){
					try {
						WlClockActivator.this.listener.onActivate(
								((Integer)WlClockActivator.this.numberChooser.getValue()).intValue()
							);
					} catch (final WlWidgetException e) {
						if(WlClockActivator.this.errorHandler != null)
							WlClockActivator.this.errorHandler.onError(e);
					}
				}
			}
		});
		
		this.deactivate.addClickHandler(new ClickHandler(){
			@Override
			public void onClick(ClickEvent sender) {
				if(WlClockActivator.this.listener != null)
					WlClockActivator.this.listener.onDeactivate();
			}
		});
		
		this.activate.setText("Activate");
		this.deactivate.setText("Deactivate");
		
		
		this.horizontalPanel.add(this.numberChooser.getWidget());
		this.horizontalPanel.add(this.activate);
		this.horizontalPanel.add(this.deactivate);
	}
	
	@Override
	public void dispose(){
		this.numberChooser.dispose();
	}
	
	public void addClockActivationListener(IWlClockActivationListener listener){
		this.listener = listener;
	}
	
	@Override
	public Widget getWidget() {
		return this;
	}
	
	public void setErrorHandler(IWlClockActivationErrorHandler handler){
		this.errorHandler = handler;
	}
	
	@Override
	public void setStyleName(String style){
		this.horizontalPanel.setStyleName(style);
	}
}
