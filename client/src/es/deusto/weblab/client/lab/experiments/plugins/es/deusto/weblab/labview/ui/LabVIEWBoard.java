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
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.labview.ui;

import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.ui.BoardBase;

public class LabVIEWBoard extends BoardBase {

	@SuppressWarnings("unused")
	private IConfigurationRetriever configurationRetriever;
	private VerticalPanel panel = new VerticalPanel();
	
	public LabVIEWBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(boardController);
		this.configurationRetriever = configurationRetriever;
	}

	@Override
	public void setTime(int time) {

	}

	@Override
	public void start() {
		this.panel.add(new HTML("<iframe src=\"http://www.weblab.deusto.es/testone/TestOne.html\">"));
	}

	@Override
	public void end() {

	}

	@Override
	public Widget getWidget() {
		return this.panel;
	}

}
