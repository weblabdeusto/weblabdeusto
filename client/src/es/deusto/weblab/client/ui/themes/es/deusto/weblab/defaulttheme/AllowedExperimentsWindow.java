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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class AllowedExperimentsWindow extends LoggedBaseWindow {

	public interface IAllowedExperimentsWindowCallback extends ILoggedBaseWindowCallback {
		public void onChooseExperimentButtonClicked(ExperimentAllowed experimentAllowed);
	}
	
	// Widgets
	private WlWaitingLabel waitingLabel;
	private Label generalErrorLabel;

	// DTOs
	private ExperimentAllowed [] experimentsAllowed;
	
	public AllowedExperimentsWindow(IConfigurationManager configurationManager, User user, ExperimentAllowed[] experimentsAllowed, IAllowedExperimentsWindowCallback callback) {
	    super(configurationManager, user, callback);
	    this.experimentsAllowed = experimentsAllowed;

	    this.loadWidgets();	    
	}

	@Override
	protected void loadWidgets(){
		super.loadWidgets();

		AbsolutePanel navigationPanel = new AbsolutePanel();
		navigationPanel.setSize("100%", "30px");
		this.contentPanel.add(navigationPanel);
		
		Label contentTitleLabel = new Label(this.i18nMessages.myExperiments());
		contentTitleLabel.setStyleName("title-label");
		this.contentPanel.add(contentTitleLabel);
		this.contentPanel.setCellHeight(contentTitleLabel, "40px");
				
		this.generalErrorLabel = new Label();
		this.generalErrorLabel.setStyleName(DefaultTheme.Style.ERROR_MESSAGE);
		this.contentPanel.add(this.generalErrorLabel);

		WlVerticalPanel listExperimentsPanel = new WlVerticalPanel();
		listExperimentsPanel.setWidth("100%");
		listExperimentsPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	    	    
		final Grid grid = new Grid(this.experimentsAllowed.length + 1, 3);

		Label experimentCategoryHeader = new Label(this.i18nMessages.experimentCategory());
		experimentCategoryHeader.setStyleName("table-header");
		Label experimentNameHeader = new Label(this.i18nMessages.experimentName());
		experimentNameHeader.setStyleName("table-header");
		grid.setWidget(0, 0, experimentCategoryHeader);
		grid.setWidget(0, 1, experimentNameHeader);
		grid.setWidget(0, 2, new Label(""));
		grid.setCellPadding(10);
		grid.setBorderWidth(0);
		for(int i = 0; i < this.experimentsAllowed.length; ++i){
			final String category = this.experimentsAllowed[i].getExperiment().getCategory().getCategory();
			
			final Anchor nameLink = new Anchor(this.experimentsAllowed[i].getExperiment().getName());
			nameLink.addClickHandler(new ExperimentClickListener(i));

			grid.setWidget(i + 1, 0, new Label(category));
			grid.setWidget(i + 1, 1, nameLink);
		}
		
		while(listExperimentsPanel.getWidgetCount() > 0)
			listExperimentsPanel.remove(0);
		listExperimentsPanel.add(grid);
		
		this.contentPanel.add(listExperimentsPanel);
		
		this.waitingLabel = new WlWaitingLabel();
		this.contentPanel.add(this.waitingLabel.getWidget());
	}
	
        public void showError(String message) {
            this.generalErrorLabel.setText(message);
            this.waitingLabel.stop();
            this.waitingLabel.setText("");
        }	
	
	public void showMessage(String message) {
		this.generalErrorLabel.setText(message);
	}
	
	private class ExperimentClickListener implements ClickHandler
	{
		private final int number;
		
		public ExperimentClickListener(int n) {
			this.number = n;
		}
		
		@Override
		public void onClick(ClickEvent event) {
			final ExperimentAllowed ea = AllowedExperimentsWindow.this.experimentsAllowed[this.number];
			((IAllowedExperimentsWindowCallback)AllowedExperimentsWindow.this.callback).onChooseExperimentButtonClicked(ea);
		}
	}	
}
