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
package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.logical.shared.ResizeEvent;
import com.google.gwt.event.logical.shared.ResizeHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.DisclosurePanel;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.web.bindery.event.shared.HandlerRegistration;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.ui.widgets.WlAHref;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

/**
 * Window that displays the list of allowed experiments for the logged in 
 * user, and lets the user select one.
 */
class AllowedExperimentsWindow extends BaseWindow {

	interface MyUiBinder extends UiBinder<Widget, AllowedExperimentsWindow> {}
	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);
	
	public interface IAllowedExperimentsWindowCallback {
		public boolean startedLoggedIn();
		public void onLogoutButtonClicked();
		public void onChooseExperimentButtonClicked(ExperimentAllowed experimentAllowed);
	}
	
	// Widgets
	@UiField Image logoImage;
	@UiField VerticalPanel containerPanel;
	@UiField Label userLabel;
	@UiField Anchor logoutLink;
	@UiField AbsolutePanel navigationPanel;
	@UiField Label contentTitleLabel;
	@UiField Grid experimentsTable;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField Label separatorLabel;
	@UiField Label separatorLabel2;
	@UiField Label separatorLabel3;
	@UiField WlAHref administrationLink;
	@UiField WlAHref profileLink;
	@UiField Label separatorLabelAdministration;
	@UiField HorizontalPanel headerPanel;
	@UiField WlAHref institutionLink;

	// Callbacks
	private final IAllowedExperimentsWindowCallback callback;

	private static HandlerRegistration RESIZE_HANDLER = null;
	
	// DTOs
	private final User user;
	private Map<String, Map<ExperimentAllowed, IConfigurationRetriever>> experimentsAllowed;
	private ExperimentAllowed [] failedExperiments;
	
	AllowedExperimentsWindow(IConfigurationManager configurationManager, User user, ExperimentAllowed[] experimentsAllowed, IAllowedExperimentsWindowCallback callback) {
	    super(configurationManager);
	    
	    this.user = user;
	    this.callback = callback;
	    
	    loadExperimentsAllowedConfigurations(experimentsAllowed);
	    
	    this.loadWidgets();

	    
	    
	    if(RESIZE_HANDLER != null)
	    	RESIZE_HANDLER.removeHandler();
	    
	    RESIZE_HANDLER = Window.addResizeHandler(new ResizeHandler() {
			
			@Override
			public void onResize(ResizeEvent event) {
				System.out.println("Resizing. New width: " + event.getWidth());
				AllowedExperimentsWindow.this.experimentsTable.clear();
			    while(AllowedExperimentsWindow.this.experimentsTable.getRowCount() > 0)
			    	AllowedExperimentsWindow.this.experimentsTable.removeRow(0);
				loadExperimentsTable();
			}
		});
	}
	
	void dispose() {
	    if(RESIZE_HANDLER != null) {
	    	RESIZE_HANDLER.removeHandler();
	    	RESIZE_HANDLER = null;
	    }
	}
	
	private void loadExperimentsAllowedConfigurations(ExperimentAllowed [] experimentsAllowed) {
		final List<ExperimentAllowed> failedExperiments = new Vector<ExperimentAllowed>();
		this.experimentsAllowed = new HashMap<String, Map<ExperimentAllowed, IConfigurationRetriever>>();
		for(ExperimentAllowed experimentAllowed : experimentsAllowed) {
			// Try to retrieve the configuration for that experiment
			final IConfigurationRetriever retriever;
			try{
				retriever = ExperimentFactory.getExperimentConfigurationRetriever(experimentAllowed.getExperiment().getExperimentUniqueName());
			}catch(IllegalArgumentException e){
				failedExperiments.add(experimentAllowed);
				e.printStackTrace();
				continue;
			}
			
			// if not failed, then add it to the map
			final String category = experimentAllowed.getExperiment().getCategory().getCategory();
			if(!this.experimentsAllowed .containsKey(category))
				this.experimentsAllowed .put(category, new HashMap<ExperimentAllowed, IConfigurationRetriever>());
			this.experimentsAllowed .get(category).put(experimentAllowed, retriever);
		}
		
		this.failedExperiments = failedExperiments.toArray(new ExperimentAllowed[]{});
	}
	
	public ExperimentAllowed [] getFailedLoadingExperiments(){
		return this.failedExperiments;
	}
	
	@Override
	public Widget getWidget(){
		return this.containerPanel;
	}		
	
	protected void loadWidgets(){
	    AllowedExperimentsWindow.uiBinder.createAndBindUi(this);

		final String hostEntityImage = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_IMAGE, "");
		this.logoImage.setUrl(GWT.getModuleBaseURL() + hostEntityImage);
		
		final String hostEntityLink = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_LINK, "");
		this.institutionLink.setHref(hostEntityLink);

	    final boolean visibleHeader = HistoryProperties.getBooleanValue(HistoryProperties.HEADER_VISIBLE, true);
	    this.headerPanel.setVisible(visibleHeader);
	    this.navigationPanel.setVisible(visibleHeader);

	    if(this.user != null) {
	    	this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
	    	if(this.user.getAdminUrl() != null && !this.user.getAdminUrl().equals("")) {
                this.administrationLink.setTarget("_top");
	    		this.administrationLink.setVisible(true);
	    		this.administrationLink.setHref(this.user.getAdminUrl());
	    		this.separatorLabelAdministration.setVisible(true);
	    	}
	    	this.profileLink.setHref(WebLabClient.PROFILE_URL);
	    }
	    loadExperimentsTable();
		
	    if(this.callback.startedLoggedIn()){
	    	this.logoutLink.setVisible(false);
	    	this.separatorLabel3.setVisible(false);
	    }
	}

	private void loadExperimentsTable() {
		int INTENDED_COLUMNS = (80 * Window.getClientWidth() / 100) / 250;
        if(INTENDED_COLUMNS == 0)
            INTENDED_COLUMNS = 1;
	    final int COLUMNS = this.experimentsAllowed.size() > INTENDED_COLUMNS? INTENDED_COLUMNS : this.experimentsAllowed.size();
	    
	    this.experimentsTable.resize(this.experimentsAllowed.size() / COLUMNS + 1, COLUMNS);
	    
		final List<String> categories = new Vector<String>(this.experimentsAllowed.keySet());
		Collections.sort(categories);
		
		for(int i = 0; i < categories.size(); ++i) {
			
			final String category = categories.get(i);
			final List<ExperimentAllowed> categoryExperiments = new Vector<ExperimentAllowed>(this.experimentsAllowed.get(category).keySet());
			Collections.sort(categoryExperiments);
			
			final Grid categoryGrid = new Grid();
			categoryGrid.resize(categoryExperiments.size(), 2);
			categoryGrid.setWidth("100%");

			for(int j = 0; j < categoryExperiments.size(); ++j) {
				final ExperimentAllowed experiment = categoryExperiments.get(j);
				
				ExperimentClickListener listener = new ExperimentClickListener(experiment);
				final Anchor nameLink = new Anchor(experiment.getExperiment().getName());
				nameLink.addClickHandler(listener);
				
				IConfigurationRetriever retriever = this.experimentsAllowed.get(category).get(experiment);
				
				String picture = retriever.getProperty("experiment.picture", "");
				
				if(picture.isEmpty())
					picture = retriever.getProperty("experiments.default_picture", "");
				
	            if(picture.startsWith("/"))
	                picture = GWT.getModuleBaseURL() + picture;
				final Image img = new Image(picture);
	            img.setHeight("40px");
				img.setStyleName("web-allowedexperiments-image");
				
				img.addClickHandler(listener);
							
				categoryGrid.setWidget(j, 0, nameLink);
				
				categoryGrid.setWidget(j, 1, new SimplePanel(img));
				categoryGrid.getCellFormatter().setHorizontalAlignment(j, 1, HasHorizontalAlignment.ALIGN_CENTER);
			}
			
			final DisclosurePanel categoryPanel = new DisclosurePanel(category);
			categoryPanel.add(categoryGrid);
			categoryPanel.setAnimationEnabled(true);
			categoryPanel.setOpen(true);
			categoryPanel.setWidth("250px");
			categoryPanel.addStyleName("experiment-list-category-panel");
			
			final SimplePanel decoratedCategoryPanel = new SimplePanel(categoryPanel);
			decoratedCategoryPanel.setWidth("250px");
			decoratedCategoryPanel.addStyleName("experiment-list-category-container");

			this.experimentsTable.setWidget(i / COLUMNS, i % COLUMNS, decoratedCategoryPanel);
			this.experimentsTable.getCellFormatter().setVerticalAlignment(i / COLUMNS, i % COLUMNS, HasVerticalAlignment.ALIGN_TOP);
		}
	}
	
    @Override
    public void showError(String message) {
        this.generalErrorLabel.setText(message);
        this.waitingLabel.stop();
        this.waitingLabel.setText("");
    }	
	
    @Override
	public void showMessage(String message) {
		this.generalErrorLabel.setText(message);
	}
    
	@UiHandler("logoutLink")
	void onLogoutClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onLogoutButtonClicked();
	}
	
	private class ExperimentClickListener implements ClickHandler
	{
		private final ExperimentAllowed experimentAllowed;
		
		public ExperimentClickListener(ExperimentAllowed experimentAllowed) {
			this.experimentAllowed = experimentAllowed;
		}
		
		@Override
		public void onClick(ClickEvent event) {
			AllowedExperimentsWindow.this.callback.onChooseExperimentButtonClicked(this.experimentAllowed);
		}
	}	
}
