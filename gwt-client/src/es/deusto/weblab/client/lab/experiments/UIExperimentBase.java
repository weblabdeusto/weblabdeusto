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
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.experiments;

import java.util.List;
import java.util.Vector;

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;

public abstract class UIExperimentBase extends ExperimentBase {

	protected final VerticalPanel panel = new VerticalPanel();
	protected final List<IWlDisposableWidget> disposableWidgets = new Vector<IWlDisposableWidget>();
	
	public UIExperimentBase(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
		this.panel.setWidth("100%");
		this.panel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	}

	protected void putWidget(Widget widget) {
		this.panel.clear();
		this.panel.add(widget);
	}
	
	protected void addDisposableWidgets(IWlDisposableWidget widget) {
		this.disposableWidgets.add(widget);
	}
	
	@Override
	public void end() {
		for(IWlDisposableWidget widget : this.disposableWidgets)
			try {
				widget.dispose();
			} catch (Exception e) {
				e.printStackTrace();
			}
	}

	@Override
	public Widget getWidget() {
		return this.panel;
	}
}
