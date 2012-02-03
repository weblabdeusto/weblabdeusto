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
*         Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
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
		public void onLogoutButtonClicked();
		public void onBackButtonClicked();
		public void onReserveButtonClicked();
		public void onFinishButtonClicked();
	}

	// Widgets
	@UiField VerticalPanel containerPanel;
	@UiField Label userLabel;
	@UiField Anchor logoutLink;
	@UiField AbsolutePanel navigationPanel;
	@UiField Anchor backLink;
	@UiField VerticalPanel experimentAreaPanel;
	@UiField Label contentTitleLabel;
	@UiField Label contentTitleLabelSelected;
	@UiField Grid detailsGrid;
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
	@UiField HorizontalPanel headerPanel;

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
		
	    this.reserveButton.setVisible(this.configurationManager.getBoolProperty(RESERVE_BUTTON_SHOWN_PROPERTY, DEFAULT_RESERVE_BUTTON_SHOWN));
	    
		final boolean visibleHeader = HistoryProperties.getBooleanValue(HistoryProperties.HEADER_VISIBLE, true);
	    this.headerPanel.setVisible(visibleHeader);
	    this.navigationPanel.setVisible(visibleHeader);
	    
	    if(this.user != null)
	    	this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
		
	    if(this.callback.startedLoggedIn()){
	    	this.logoutLink.setVisible(false);
	    	this.separatorLabel.setVisible(false);
	    	this.separatorLabel2.setVisible(false);
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
			final String infolink = retriever.getProperty(ExperimentWindow.EXPERIMENT_INFOLINK_PROPERTY, 
					ExperimentWindow.DEFAULT_EXPERIMENT_INFOLINK
			);
			
			// Retrieve the short description of the experiment info page
			final String infodesc = retriever.getProperty(ExperimentWindow.EXPERIMENT_INFODESCRIPTION_PROPERTY,
					ExperimentWindow.DEFAULT_EXPERIMENT_INFODESCRIPTION
					);
			
			if(!infolink.isEmpty())
				this.informationLink.setHref(infolink);
			this.informationLink.setText(infodesc);
			
		} catch(IllegalArgumentException e){
			e.printStackTrace();
			
			this.informationLink.setText("<not available>");
		}
		
		// Open the info page in a new window.
		this.informationLink.setTarget("_blank");
		
		String href = this.informationLink.getHref();
		
		
		// If there is actually no information available, we will just hide the label
		if(this.informationLink.getHref().isEmpty())
			this.informationLinkLabel.setVisible(false);
	}
	
	
	public void loadExperimentReservationPanels(boolean reserved) {	    
		if(reserved){
			this.reserveButton.setVisible(false);
			this.waitingLabel.start();
			this.contentTitleLabelSelected.setVisible(true);
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
		final VerticalPanel vp = new VerticalPanel();
		vp.setWidth("100%");
		vp.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		final Button b = new Button(this.i18nMessages.clickHereToOpenExperiment());
		b.addClickHandler(new ClickHandler(){
			@Override
			public void onClick(ClickEvent event) {
				Window.open( url + "client/federated.html#reservation_id=" + remoteReservationId, "_blank", "resizable=yes,scrollbars=yes,dependent=yes,width=1000,height=800,top=0");
			}
		});
		vp.add(b);
		this.experimentAreaPanel.add(vp);
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
		this.containerPanel.add(new ExperimentFinishedWindow());
	}
}
