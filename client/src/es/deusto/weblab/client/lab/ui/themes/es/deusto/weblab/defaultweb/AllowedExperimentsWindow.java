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
import com.google.gwt.event.logical.shared.CloseEvent;
import com.google.gwt.event.logical.shared.CloseHandler;
import com.google.gwt.event.logical.shared.OpenEvent;
import com.google.gwt.event.logical.shared.OpenHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.DisclosurePanel;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTMLPanel;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.SimplePanel;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
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
	@UiField HTMLPanel experimentsTable;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField Label separatorLabel;
	@UiField Label separatorLabel2;
	@UiField HorizontalPanel headerPanel;
	@UiField WlAHref institutionLink;

	// Callbacks
	private final IAllowedExperimentsWindowCallback callback;

	// DTOs
	private final User user;
	private Map<String, Map<ExperimentAllowed, IConfigurationRetriever>> experimentsAllowed;
	private ExperimentAllowed [] failedExperiments;
	
	private Map<SimplePanel, Integer> allCategories = new HashMap<SimplePanel, Integer>();
	
	public AllowedExperimentsWindow(IConfigurationManager configurationManager, User user, ExperimentAllowed[] experimentsAllowed, IAllowedExperimentsWindowCallback callback) {
	    super(configurationManager);
	    
	    this.user = user;
	    this.callback = callback;
	    
	    loadExperimentsAllowedConfigurations(experimentsAllowed);
	    
	    this.loadWidgets();
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
	
	// Important: call it once it has been added to the panel
	void initializeWidgetSizes() {
		int maxHeight = 0;
		for(SimplePanel categoryPanelContainer : this.allCategories.keySet()){
			if(categoryPanelContainer.getWidget().getOffsetHeight() > maxHeight)
				maxHeight = categoryPanelContainer.getWidget().getOffsetHeight();
			this.allCategories.put(categoryPanelContainer, categoryPanelContainer.getOffsetHeight());
		}
		
		setCategoryPanelsHeight(maxHeight);
	}
	
	private void setCategoryPanelsHeight(int height) {
		if(height <= 0)
			return;
		
		for(SimplePanel categoryPanelContainer : this.allCategories.keySet())
			categoryPanelContainer.setSize("250px", (height + 20) + "px");
	}
	
	void onClosePanel(SimplePanel categoryPanelContainer) {
		// Take into account only the rest, and not the current one
		int maxHeight = 0;
		
		for(SimplePanel currentContainer : this.allCategories.keySet()){
			
			if(categoryPanelContainer != currentContainer) {
				if(currentContainer.getWidget().getOffsetHeight() > maxHeight)
					maxHeight = currentContainer.getWidget().getOffsetHeight();
			}
		}
		
		setCategoryPanelsHeight(maxHeight);
	}
	
	void onOpenPanel(SimplePanel categoryPanelContainer) {
		// Take into account only the rest, and not the current one
		int maxHeight = 0;
		for(SimplePanel currentContainer : this.allCategories.keySet()){
			if(currentContainer.getWidget().getOffsetHeight() > maxHeight)
				maxHeight = currentContainer.getWidget().getOffsetHeight();
		}
		if(this.allCategories.get(categoryPanelContainer).intValue() > maxHeight)
			maxHeight = this.allCategories.get(categoryPanelContainer).intValue();
		
		setCategoryPanelsHeight(maxHeight);
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

	    if(this.user != null)
	    	this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));

		final List<String> categories = new Vector<String>(this.experimentsAllowed.keySet());
		Collections.sort(categories);
		
		for(int i = 0; i < categories.size(); ++i) {
			
			final String category = categories.get(i);
			final List<ExperimentAllowed> categoryExperiments = new Vector<ExperimentAllowed>(this.experimentsAllowed.get(category).keySet());
			Collections.sort(categoryExperiments);
			
			final Grid categoryGrid = new Grid();
			categoryGrid.resize(categoryExperiments.size(), 2);

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
				
				categoryGrid.setWidget(j, 1, img);
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

			categoryPanel.addOpenHandler(new OpenHandler<DisclosurePanel>() {
				@Override
				public void onOpen(OpenEvent<DisclosurePanel> event) {
					onOpenPanel(decoratedCategoryPanel);
				}
			});
			
			categoryPanel.addCloseHandler(new CloseHandler<DisclosurePanel>() {
				
				@Override
				public void onClose(CloseEvent<DisclosurePanel> event) {
					onClosePanel(decoratedCategoryPanel);
				}
			});

			this.allCategories.put(decoratedCategoryPanel, Integer.valueOf(0));
			this.experimentsTable.add(decoratedCategoryPanel);
		}
		
	    if(this.callback.startedLoggedIn()){
	    	this.logoutLink.setVisible(false);
	    	this.separatorLabel.setVisible(false);
	    	this.separatorLabel2.setVisible(false);
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
