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
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.experiments.ExperimentBase;
import es.deusto.weblab.client.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class ExperimentWindow extends LoggedBaseWindow {

	public interface IExperimentWindowCallback extends ILoggedBaseWindowCallback {
		public void onBackButtonClicked();
		public void onReserveButtonClicked();
		public void onFinishButtonClicked();
	}

	private static final String ADMIN_EMAIL_PROPERTY = "admin.email";
	private static final String DEFAULT_ADMIN_EMAIL = "<admin.email not set>";
    
	// Widgets
	private WlWaitingLabel waitingLabel;
	private Label generalErrorLabel;
	private WlVerticalPanel experimentAreaPanel;
	private WlVerticalPanel preExperimentAreaPanel;
	private WlVerticalPanel postExperimentAreaPanel;
	private Anchor backLink;
	private Button reserveButton;
	private Button finishButton;
	
	// DTOs
	private ExperimentAllowed experimentAllowed;
	private ExperimentBase experimentBase;
	private BoardBase boardBase;
	private int timeAllowed;
	
	public ExperimentWindow(IConfigurationManager configurationManager, User user, ExperimentAllowed experimentAllowed, ExperimentBase experimentBase, IExperimentWindowCallback callback){
	    super(configurationManager, user, callback);
	    this.experimentAllowed = experimentAllowed;
	    this.experimentBase = experimentBase;	
	    this.boardBase = this.experimentBase.getUI();
		
	    this.loadWidgets();
	}
	
	public void showError(String message){
		this.generalErrorLabel.setText(message);
	}

	@Override
	protected void loadWidgets(){
		super.loadWidgets();
				
		this.preExperimentAreaPanel = new WlVerticalPanel();
		this.preExperimentAreaPanel.setWidth("100%");
		this.preExperimentAreaPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.experimentAreaPanel = new WlVerticalPanel();
		this.experimentAreaPanel.setWidth("100%");
		this.experimentAreaPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);

		this.contentPanel.add(this.experimentAreaPanel);		
		
		this.postExperimentAreaPanel = new WlVerticalPanel();
		this.postExperimentAreaPanel.setWidth("100%");
		this.preExperimentAreaPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.contentPanel.add(this.preExperimentAreaPanel);
		this.contentPanel.add(this.experimentAreaPanel);
		this.contentPanel.add(this.postExperimentAreaPanel);
		
		this.mainPanel.add(this.contentPanel);
		
		this.generalErrorLabel = new Label();
		this.generalErrorLabel.setStyleName(DefaultTheme.Style.ERROR_MESSAGE);
		
		this.mainPanel.add(this.generalErrorLabel);	
		this.mainPanel.setCellHeight(this.generalErrorLabel, "30px");
	}

	public void loadExperimentReservationPanels() {	    
	    	/*
	    	 * preExperimentAreaPanel
	    	 */
		AbsolutePanel navigationPanel = new AbsolutePanel();
		navigationPanel.setSize("100%", "30px");
		
		this.backLink = new Anchor("< " + this.i18nMessages.backToMyExperiments());
		this.backLink.addClickHandler(new ClickHandler() {
		    @Override
		    public void onClick(ClickEvent event) {
			((IExperimentWindowCallback)ExperimentWindow.this.callback).onBackButtonClicked();
			
		    }
		});
		navigationPanel.add(this.backLink);
		this.preExperimentAreaPanel.add(navigationPanel);
		this.preExperimentAreaPanel.setCellHorizontalAlignment(navigationPanel, HasHorizontalAlignment.ALIGN_LEFT);
		//this.preExperimentAreaPanel.setCellHorizontalAlignment(this.backLink, HasHorizontalAlignment.ALIGN_LEFT);
		
		final Label contentTitleLabel = new Label(this.i18nMessages.reserveThisExperiment());
		contentTitleLabel.setStyleName("title-label");
		this.preExperimentAreaPanel.add(contentTitleLabel);
		this.preExperimentAreaPanel.setCellHeight(contentTitleLabel, "30px");

		final Grid grid = new Grid(4, 2);
		
		grid.setBorderWidth(0);
		grid.setCellPadding(5);
		
		grid.setWidget(0, 0, new Label(this.i18nMessages.experimentName() + ":"));
		grid.setWidget(1, 0, new Label(this.i18nMessages.experimentCategory() + ":"));
		grid.setWidget(2, 0, new Label(this.i18nMessages.experimentOwner() + ":"));
		grid.setWidget(3, 0, new Label(this.i18nMessages.timeAllowed() + ":"));
		
		final Label experimentName = new Label(this.experimentAllowed.getExperiment().getName());
		experimentName.setStyleName("experiment-detail");
		
		final Label experimentCategoryName = new Label(this.experimentAllowed.getExperiment().getCategory().getCategory());
		experimentCategoryName.setStyleName("experiment-detail");
		
		final Label experimentOwner = new HTML("<a href=\"mailto:" + WlUtil.escape(this.experimentAllowed.getExperiment().getOwner()) + "\" target=\"_blank\">" + WlUtil.escapeNotQuote(this.experimentAllowed.getExperiment().getOwner()) + "</a>");
		experimentOwner.setStyleName("experiment-detail");
		
		final Label experimentTime = new Label(""+this.experimentAllowed.getTimeAllowed());
		experimentTime.setStyleName("experiment-detail");		
		
		grid.setWidget(0, 1, experimentName);
		grid.setWidget(1, 1, experimentCategoryName);
		grid.setWidget(2, 1, experimentOwner);
		grid.setWidget(3, 1, experimentTime);
		
		this.preExperimentAreaPanel.add(grid);
		this.preExperimentAreaPanel.setCellHeight(grid, "130px");
		
	    	/*
	    	 * ExperimentAreaPanel
	    	 */		
		// Important note: this MUST be done here or FileUpload will cause problems
		this.experimentAreaPanel.add(this.boardBase.getWidget());	
		this.boardBase.initialize();
		// end of Important note

	    	/*
	    	 * postExperimentAreaPanel
	    	 */
		this.waitingLabel = new WlWaitingLabel();
		this.postExperimentAreaPanel.add(this.waitingLabel.getWidget());
		this.postExperimentAreaPanel.setCellHorizontalAlignment(this.waitingLabel.getWidget(), HasHorizontalAlignment.ALIGN_CENTER);
		this.postExperimentAreaPanel.setCellHeight(this.waitingLabel.getWidget(), "30px");
		
		this.reserveButton = new Button(this.i18nMessages.reserve());			
		this.reserveButton.addClickHandler(new ClickHandler(){
		    @Override
			public void onClick(ClickEvent event) {
		    	    	ExperimentWindow.this.reserveButton.setEnabled(false);
		    	    	ExperimentWindow.this.backLink.setVisible(false);
		    	    	ExperimentWindow.this.waitingLabel.setText(ExperimentWindow.this.i18nMessages.reserving());
		    	    	ExperimentWindow.this.waitingLabel.start();
		    	    	((IExperimentWindowCallback)ExperimentWindow.this.callback).onReserveButtonClicked();
			}
		});
		
		this.postExperimentAreaPanel.add(this.reserveButton);
		this.postExperimentAreaPanel.setCellHorizontalAlignment(this.reserveButton, HasHorizontalAlignment.ALIGN_CENTER);
		this.postExperimentAreaPanel.setCellHeight(this.reserveButton, "30px");
	}

	public void loadUsingExperimentPanels(int time) {
	    this.timeAllowed = time;
	    
	    while ( this.preExperimentAreaPanel.getWidgetCount() > 0)
		this.preExperimentAreaPanel.remove(0);
	    while ( this.postExperimentAreaPanel.getWidgetCount() > 0)
		this.postExperimentAreaPanel.remove(0);
	    
    	/*
    	 * preExperimentAreaPanel
    	 */	    
		AbsolutePanel navigationPanel = new AbsolutePanel();
		navigationPanel.setSize("100%", "30px");
		this.preExperimentAreaPanel.add(navigationPanel);
		
		final Label contentTitleLabel = new Label(this.experimentAllowed.getExperiment().getName());
		contentTitleLabel.setStyleName("title-label");				
		this.preExperimentAreaPanel.add(contentTitleLabel);

    	/*
    	 * experimentAreaPanel
    	 */		
		// This can't be before adding the widget to the DOM tree 
		// If it's done, applets will not work 
		this.experimentBase.getUI().start();
		this.experimentBase.getUI().setTime(this.timeAllowed);
		
	    	/*
	    	 * postExperimentAreaPanel
	    	 */			
		this.postExperimentAreaPanel.add(new HTML("&nbsp;"));
		
		this.finishButton = new Button(this.i18nMessages.finish());		
		this.finishButton.addClickHandler(new ClickHandler() {
		    @Override
		    public void onClick(ClickEvent sender) {
			((IExperimentWindowCallback)ExperimentWindow.this.callback).onFinishButtonClicked();			
		    }
		});
		this.postExperimentAreaPanel.add(this.finishButton);
		this.postExperimentAreaPanel.setCellHorizontalAlignment(this.finishButton, HasHorizontalAlignment.ALIGN_CENTER);
	}	
	
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
}