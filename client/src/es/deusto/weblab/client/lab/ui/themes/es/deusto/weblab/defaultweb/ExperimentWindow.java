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
*         Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CellPanel;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.ui.widgets.WlAHref;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;



/**
 * Window that displays basic information about a selected experiment and 
 * lets the user Reserve it.
 */
class ExperimentWindow extends BaseWindow {
	
	interface MyUiBinder extends UiBinder<Widget, ExperimentWindow> {}
	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);

	public interface IExperimentWindowCallback {
		public boolean startedLoggedIn();
		public boolean startedReserved();
		public void disableFinishOnClose();
		public void onLogoutButtonClicked();
		public void onBackButtonClicked();
		public void onReserveButtonClicked();
		public void onFinishButtonClicked();
	}

	// Widgets
	@UiField Image logoImage;
	@UiField VerticalPanel containerPanel;
	@UiField Label userLabel;
	@UiField Anchor logoutLink;
	@UiField HorizontalPanel navigationPanel;
	@UiField Anchor backLink;
	@UiField VerticalPanel experimentAreaPanel;
	@UiField Label contentTitleLabel;
	@UiField Label contentTitleLabelSelected;
	@UiField Anchor contentTitleLabelInfo;
	@UiField DecoratorPanel detailsGrid;
	@UiField Label experimentNameLabel;
	@UiField Label experimentCategoryLabel;
	@UiField Label timeAllowedLabel;
	@UiField Anchor informationLink;
	@UiField Label informationLinkLabel;
	@UiField Button reserveButton;
	@UiField Button finishButton;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField Label separatorLabel;
	@UiField Label separatorLabel2;
	@UiField Label separatorLabel3;
	@UiField WlAHref profileLink;
	@UiField WlAHref administrationLink;
	@UiField Label separatorLabelAdministration;
	@UiField CellPanel headerPanel;
	@UiField CellPanel footerPanel;
	@UiField WlAHref bottomInstitutionLink;
	@UiField WlAHref institutionLink;
	@UiField Image bottomLogoImage;
	@UiField HorizontalPanel hostedByPanel;
	@UiField HorizontalPanel poweredByPanel;

	// Callbacks
	private final IExperimentWindowCallback callback;

	// Properties
	private static final String ADMIN_EMAIL_PROPERTY = "admin.email";
	private static final String DEFAULT_ADMIN_EMAIL = "<admin.email not set>";
	
	private static final String EXPERIMENT_INFOLINK_PROPERTY = "experiment.info.link";
	private static final String DEFAULT_EXPERIMENT_INFOLINK = "";
	
	private static final String EXPERIMENT_INFODESCRIPTION_PROPERTY = "experiment.info.description";
	private static final String DEFAULT_EXPERIMENT_INFODESCRIPTION = "";
	
	private static final String RESERVE_BUTTON_SHOWN_PROPERTY = "experiment.reserve.button.shown";
	private static final boolean DEFAULT_RESERVE_BUTTON_SHOWN  = true;
    
	// DTOs
	private final User user;
	private final ExperimentAllowed experimentAllowed;
	private final ExperimentBase experimentBase;
	
	private String infolink = null;
    
	public ExperimentWindow(IConfigurationManager configurationManager, User user, ExperimentAllowed experimentAllowed, ExperimentBase experimentBase, IExperimentWindowCallback callback){
	    super(configurationManager);
	
	    this.user = user;
	    this.experimentAllowed = experimentAllowed;
	    this.experimentBase = experimentBase;	
	    this.callback = callback;
	    
	    this.loadWidgets();
	}

	@Override
	public Widget getWidget(){
		return this.containerPanel;
	}	
	
    @Override
	public void showError(String message){
		this.generalErrorLabel.setText(message);
	}

	public void loadWidgets(){		
		ExperimentWindow.uiBinder.createAndBindUi(this);
		
		final String hostEntityImage = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_IMAGE, "");
		this.logoImage.setUrl(GWT.getModuleBaseURL() + hostEntityImage);
		
		final String smallHostEntityImage = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_MOBILE_IMAGE, "");
		this.bottomLogoImage.setUrl(GWT.getModuleBaseURL() + smallHostEntityImage);
		
		final String hostEntityLink = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_LINK, "");
		this.bottomInstitutionLink.setHref(hostEntityLink);
		this.institutionLink.setHref(hostEntityLink);
		
		final IConfigurationRetriever retriever = ExperimentFactory.getExperimentConfigurationRetriever(this.experimentAllowed.getExperiment().getExperimentUniqueName());
	    this.reserveButton.setVisible(retriever.getBoolProperty(RESERVE_BUTTON_SHOWN_PROPERTY, DEFAULT_RESERVE_BUTTON_SHOWN));
	    
		final boolean visibleHeader = HistoryProperties.getBooleanValue(HistoryProperties.HEADER_VISIBLE, true);
	    this.headerPanel.setVisible(visibleHeader);
	    this.navigationPanel.setVisible(visibleHeader);
	    this.hostedByPanel.setVisible(!visibleHeader);
	    
		final String widgetMode = HistoryProperties.getValue(HistoryProperties.WIDGET, "");

	    if(!widgetMode.isEmpty()) {
	    	this.poweredByPanel.setVisible(false);
		    this.contentTitleLabel.setVisible(false);
		    this.contentTitleLabelSelected.setVisible(false);
		    this.hostedByPanel.setVisible(false);
		    this.headerPanel.setVisible(false);
		    this.footerPanel.setVisible(false);
		    this.institutionLink.setVisible(false);
		    this.logoutLink.setVisible(false);
	    } else {
	    	this.poweredByPanel.setVisible(true);
	    	this.institutionLink.setVisible(true);
	    	this.logoutLink.setVisible(true);
	    }
	    
	    
	    if(this.user != null) {
	    	this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
	    	if(this.user.getAdminUrl() != null && !this.user.getAdminUrl().equals("")) {
	    		this.administrationLink.setVisible(true);
	    		this.administrationLink.setHref(this.user.getAdminUrl());
	    		this.separatorLabelAdministration.setVisible(true);
	    	}
	    	this.profileLink.setHref(WebLabClient.PROFILE_URL);
	    }
	    
	    if(this.callback.startedLoggedIn()){
	    	this.logoutLink.setVisible(false);
	    	this.separatorLabel3.setVisible(false);
	    }
	}
	
	
	/**
	 * Instances a configuration retriever and uses it to obtain the infolink and
	 * to display it through the appropriate field in the GUI.
	 */
	private void updateInfolinkField() {
		
		IConfigurationRetriever retriever = null;
		try {
			
			retriever = ExperimentFactory.getExperimentConfigurationRetriever(this.experimentAllowed.getExperiment().getExperimentUniqueName());
			
			// Retrieve the address of the experiment info page
			this.infolink = retriever.getProperty(ExperimentWindow.EXPERIMENT_INFOLINK_PROPERTY, ExperimentWindow.DEFAULT_EXPERIMENT_INFOLINK);
			
			// Retrieve the short description of the experiment info page
			final String infodesc = retriever.getProperty(ExperimentWindow.EXPERIMENT_INFODESCRIPTION_PROPERTY, ExperimentWindow.DEFAULT_EXPERIMENT_INFODESCRIPTION);
			
			if(this.infolink != null && !this.infolink.isEmpty())
				this.informationLink.setHref(this.infolink);
			else
				this.infolink = null;
			this.informationLink.setText(infodesc);
			
		} catch(IllegalArgumentException e){
			e.printStackTrace();
			
			this.informationLink.setText("<not available>");
			this.infolink = null;
		}
		
		// If there is actually no information available, we will just hide the label
		if(this.informationLink.getHref().isEmpty()) {
			this.informationLinkLabel.setVisible(false);
			this.informationLink.setVisible(false);
		}
	}
	
	
	public void loadExperimentReservationPanels(boolean reserved) {	    
		if(reserved){
			this.reserveButton.setVisible(false);
			this.waitingLabel.start();
			
			final boolean widgetMode = !HistoryProperties.getValue(HistoryProperties.WIDGET, "").isEmpty();
			if(widgetMode)
				this.contentTitleLabelSelected.setVisible(false);
			this.contentTitleLabel.setVisible(false);
		}else{
			this.contentTitleLabelSelected.setVisible(false);
			this.contentTitleLabel.setVisible(true);
		}
		this.experimentNameLabel.setText(this.experimentAllowed.getExperiment().getName());
		this.experimentCategoryLabel.setText(this.experimentAllowed.getExperiment().getCategory().getCategory());
		this.timeAllowedLabel.setText(this.experimentAllowed.getTimeAllowed()+"");
		this.updateInfolinkField();

		// Important note: this MUST be done here or FileUpload will cause problems
		this.experimentAreaPanel.add(this.experimentBase.getWidget());	
		// end of Important note
	}

	public void loadUsingExperimentPanels() {
		final boolean widgetMode = !HistoryProperties.getValue(HistoryProperties.WIDGET, "").isEmpty();
		
		this.contentTitleLabelInfo.setVisible(this.infolink != null && !widgetMode);
		if(this.infolink != null)
			this.contentTitleLabelInfo.setHref(this.infolink);

	    this.contentTitleLabel.setText(this.experimentAllowed.getExperiment().getName());
	    this.contentTitleLabelSelected.setText(this.experimentAllowed.getExperiment().getName());
	    this.detailsGrid.setVisible(false);
	    this.waitingLabel.stop();
	    this.waitingLabel.setText("");
	    this.reserveButton.setVisible(false);
		this.finishButton.setVisible(true);
	}
	
	public void loadRemoteExperimentPanel(final String url, final String remoteReservationId) {
		loadUsingExperimentPanels();
		
		this.experimentAreaPanel.clear();
		String remoteUrl = url + "client/federated.html#reservation_id=" + remoteReservationId + "&back=" + HistoryProperties.encode(Window.Location.getHref());
        if(WebLabClient.getLocale() != null)
            remoteUrl += "&locale=" + WebLabClient.getLocale();

        this.callback.disableFinishOnClose();
		Window.Location.assign(remoteUrl);
	}

	
	@UiHandler("backLink")
	void onBackLinkClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onBackButtonClicked();	
	}	
	
	@UiHandler("logoutLink")
	void onLogoutLinkClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onLogoutButtonClicked();
	}	

	@UiHandler("reserveButton")
	void onReserveButtonClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.reserveButton.setEnabled(false);
		this.backLink.setVisible(false);
		this.waitingLabel.setText(ExperimentWindow.this.i18nMessages.reserving());
		this.waitingLabel.start();
		this.callback.onReserveButtonClicked();	
	}	

	@UiHandler("finishButton")
	void onFinishButtonClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onFinishButtonClicked();		
	}	
	
    @Override
	public void showMessage(String message) {
		this.generalErrorLabel.setText(message);
	}

    public void showWaitingInstances(int position) {
    	this.waitingLabel.setText(
    			this.i18nMessages.waitingForAnInstancePosition(
    					this.configurationManager.getProperty(
    							ExperimentWindow.ADMIN_EMAIL_PROPERTY,
    							ExperimentWindow.DEFAULT_ADMIN_EMAIL
    					),
    					position
    			)
    	);
    }

	public void showWaitingReservation(int position) {
	    this.waitingLabel.setText(this.i18nMessages.waitingInQueuePosition(position));
	}

	public void showWaitingReservationConfirmation() {
	    this.waitingLabel.setText(this.i18nMessages.waitingForConfirmation());
	}

	public void onExperimentInteractionFinished() {
		this.containerPanel.clear();
		this.containerPanel.add(new ExperimentFinishedWindow(this.configurationManager).getWidget());
	}
}
