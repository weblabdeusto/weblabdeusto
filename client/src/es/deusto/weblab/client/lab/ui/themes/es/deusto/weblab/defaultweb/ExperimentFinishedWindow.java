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
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.Window.Location;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.ui.widgets.WlAHref;

public class ExperimentFinishedWindow extends BaseWindow {

	private static ExperimentFinishedWindowUiBinder uiBinder = GWT
			.create(ExperimentFinishedWindowUiBinder.class);

	@UiField VerticalPanel containerPanel;
	@UiField Image logoImage;
	@UiField Label userLabel;
	@UiField Anchor logoutLink;
	@UiField Label separatorLabel;
	@UiField Label separatorLabel2;
	@UiField Label separatorLabel3;
	@UiField WlAHref administrationLink;
	@UiField Label separatorLabelAdministration;
	@UiField HorizontalPanel headerPanel;
	@UiField WlAHref bottomInstitutionLink;
	@UiField WlAHref institutionLink;
	@UiField Image bottomLogoImage;
	@UiField HorizontalPanel hostedByPanel;
	@UiField Button backButton;
	@UiField HorizontalPanel poweredByPanel;
	
	interface ExperimentFinishedWindowUiBinder extends UiBinder<Widget, ExperimentFinishedWindow> {
	}

	public ExperimentFinishedWindow(IConfigurationManager configurationManager) {
		super(configurationManager);
		
		loadWidgets();
	}

	private void loadWidgets() {
		ExperimentFinishedWindow.uiBinder.createAndBindUi(this);
		
		final String hostEntityImage = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_IMAGE, "");
		this.logoImage.setUrl(GWT.getModuleBaseURL() + hostEntityImage);
		
		final String smallHostEntityImage = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_MOBILE_IMAGE, "");
		this.bottomLogoImage.setUrl(GWT.getModuleBaseURL() + smallHostEntityImage);
		
		final String hostEntityLink = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_LINK, "");
		this.bottomInstitutionLink.setHref(hostEntityLink);
		this.institutionLink.setHref(hostEntityLink);
		
		final boolean visibleHeader = HistoryProperties.getBooleanValue(HistoryProperties.HEADER_VISIBLE, true);
	    this.headerPanel.setVisible(visibleHeader);
	    this.hostedByPanel.setVisible(!visibleHeader);

	    final String widgetName = HistoryProperties.getValue(HistoryProperties.WIDGET, "");
	    if(!widgetName.isEmpty()) {
	    	this.hostedByPanel.setVisible(false);
	    	this.poweredByPanel.setVisible(false);
	    }
	    
    	this.logoutLink.setVisible(false);
    	this.separatorLabel.setVisible(false);
    	this.separatorLabel2.setVisible(false);
    	this.separatorLabel3.setVisible(false);
	}
	
	@UiHandler("backButton")
	public void back(@SuppressWarnings("unused") ClickEvent event) {
		final String backURL = HistoryProperties.getValue(HistoryProperties.BACK);
		if(backURL == null)
			History.back();
		else {
			final String decoded = HistoryProperties.decode(backURL);
			System.out.println("Voy a llevarle a: " + decoded);
			Location.assign(decoded);
		}
	}
	
	@Override
	public Widget getWidget(){
		return this.containerPanel;
	}

	@Override
	void showMessage(String message) {
		Window.alert(message);
	}

	@Override
	void showError(String message) {
		Window.alert(message);
	}	
}
