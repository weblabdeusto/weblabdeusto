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
package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
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
	@UiField HorizontalPanel headerPanel;

	// Callbacks
	private final IAllowedExperimentsWindowCallback callback;

	// DTOs
	private final User user;
	private final ExperimentAllowed [] experimentsAllowed;
	private final ExperimentAllowed [] failedExperiments;
	
	public AllowedExperimentsWindow(IConfigurationManager configurationManager, User user, ExperimentAllowed[] experimentsAllowed, IAllowedExperimentsWindowCallback callback) {
	    super(configurationManager);
	    
	    this.user = user;
	    this.experimentsAllowed = experimentsAllowed;
	    this.callback = callback;
	    
	    this.failedExperiments = this.loadWidgets();
	}
	
	public ExperimentAllowed [] getFailedLoadingExperiments(){
		return this.failedExperiments;
	}
	
	@Override
	public Widget getWidget(){
		return this.containerPanel;
	}		
	
	protected ExperimentAllowed [] loadWidgets(){
		final List<ExperimentAllowed> failedExperiments = new Vector<ExperimentAllowed>();
	    AllowedExperimentsWindow.uiBinder.createAndBindUi(this);
	    
	    final boolean visibleHeader = HistoryProperties.getBooleanValue(HistoryProperties.HEADER_VISIBLE, true);
	    this.headerPanel.setVisible(visibleHeader);
	    this.navigationPanel.setVisible(visibleHeader);

	    if(this.user != null)
	    	this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
		
		this.experimentsTable.resize(this.experimentsAllowed.length+1, 3);

		final Label experimentCategoryHeader = new Label(this.i18nMessages.experimentCategory());
		experimentCategoryHeader.setStyleName("web-allowedexperiments-table-header");
		this.experimentsTable.setWidget(0, 0, experimentCategoryHeader);

		final Label experimentNameHeader = new Label(this.i18nMessages.experimentName());
		experimentNameHeader.setStyleName("web-allowedexperiments-table-header");
		this.experimentsTable.setWidget(0, 1, experimentNameHeader);
		
		//final Label experimentPictureHeader = new Label(this.i18nMessages.experimentPicture());
		//experimentPictureHeader.setStyleName("web-allowedexperiments-table-header");
		//this.experimentsTable.setWidget(0,2, experimentPictureHeader);

		for(int i = 0; i < this.experimentsAllowed.length; ++i) {
			
			final ExperimentAllowed experiment = this.experimentsAllowed[i];
			
			final String category = experiment.getExperiment().getCategory().getCategory();
			final Anchor nameLink = new Anchor(experiment.getExperiment().getName());
			nameLink.addClickHandler(new ExperimentClickListener(i));
			
			IConfigurationRetriever retriever;
			try{
				retriever = ExperimentFactory.getExperimentConfigurationRetriever(experiment.getExperiment().getExperimentUniqueName());
			}catch(IllegalArgumentException e){
				failedExperiments.add(experiment);
				e.printStackTrace();
				continue;
			}
			String picture = retriever.getProperty("experiment.picture", "");
			
			if(picture.isEmpty())
				picture = retriever.getProperty("experiments.default_picture", "");
			
            if(picture.startsWith("/"))
                picture = GWT.getModuleBaseURL() + picture;
			final Image img = new Image(picture);
            img.setHeight("40px");
			img.setStyleName("web-allowedexperiments-image");
			
			img.addClickHandler(new ExperimentClickListener(i));
						
			this.experimentsTable.setWidget(i+1, 0, new Label(category));
			this.experimentsTable.setWidget(i+1, 1, nameLink);
			
			this.experimentsTable.setWidget(i+1, 2, img);
            this.experimentsTable.getCellFormatter().setHorizontalAlignment(i+1, 2, HasHorizontalAlignment.ALIGN_CENTER);
		}
		
	    if(this.callback.startedLoggedIn()){
	    	this.logoutLink.setVisible(false);
	    	this.separatorLabel.setVisible(false);
	    	this.separatorLabel2.setVisible(false);
	    }
	    return failedExperiments.toArray(new ExperimentAllowed[]{});
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
		private final int number;
		
		public ExperimentClickListener(int n) {
			this.number = n;
		}
		
		@Override
		public void onClick(ClickEvent event) {
			final ExperimentAllowed ea = AllowedExperimentsWindow.this.experimentsAllowed[this.number];
			AllowedExperimentsWindow.this.callback.onChooseExperimentButtonClicked(ea);
		}
	}	
}
