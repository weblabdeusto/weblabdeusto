/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.experiments.aquarium.ui;

import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.lab.experiments.IDisposableWidgetsContainer;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;
import es.deusto.weblab.client.ui.widgets.WlTimer;

public class WidgetContainerPanel extends Composite implements IDisposableWidgetsContainer, IStatusUpdatable  {

	private static WidgetContainerUiBinder uiBinder = GWT.create(WidgetContainerUiBinder.class);

	interface WidgetContainerUiBinder extends UiBinder<Widget, WidgetContainerPanel> {}
	
	@UiField(provided=true) WlTimer timer;
	@UiField VerticalPanel panel;
	
	private final IDisposableWidgetsContainer mainWidget;
	private final IStatusUpdatable statusUpdatable;  

	public WidgetContainerPanel(Widget widget, int time) {
		if(widget instanceof IDisposableWidgetsContainer)
			this.mainWidget = (IDisposableWidgetsContainer)widget;
		else
			this.mainWidget = null;
		
		if(widget instanceof IStatusUpdatable) 
			this.statusUpdatable = (IStatusUpdatable)widget;
		else
			this.statusUpdatable = null;
		
		this.timer = new WlTimer(false);
		initWidget(uiBinder.createAndBindUi(this));
		this.timer.updateTime(time);
		this.timer.start();
		
		this.panel.add(widget);
	}

	@Override
	public IWlDisposableWidget[] getDisposableWidgets() {
		final List<IWlDisposableWidget> disposables = new Vector<IWlDisposableWidget>();
		disposables.add(this.timer);
		
		if (this.mainWidget != null)
			for(IWlDisposableWidget disposable : this.mainWidget.getDisposableWidgets()) 
				disposables.add(disposable);
		
		return disposables.toArray(new IWlDisposableWidget[]{});
	}

	@Override
	public Widget asGwtWidget() {
		return this;
	}

	@Override
	public void updateStatus(Status status) {
		if(this.statusUpdatable != null)
			this.statusUpdatable.updateStatus(status);
	}
}
