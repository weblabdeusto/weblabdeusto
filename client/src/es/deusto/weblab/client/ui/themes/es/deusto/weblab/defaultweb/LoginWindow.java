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
package es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyPressHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultweb.i18n.IWebLabDeustoThemeMessages;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultweb.widgets.EasyGrid;
import es.deusto.weblab.client.ui.widgets.WlHorizontalPanel;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

class LoginWindow extends BaseWindow {

	
	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface MyUiBinder extends UiBinder<Widget, LoginWindow> {
	}

	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);
	

	@UiField WlHorizontalPanel langsPanel;
	
	@UiField Label usernameLabel;
	@UiField Label passwordLabel;
	@UiField Label usernameErrorLabel;
	@UiField Label passwordErrorLabel;
	@UiField TextBox usernameTextbox;
	@UiField PasswordTextBox passwordTextbox;
	@UiField Button loginButton;
	@UiField EasyGrid grid;
	
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	
	@UiField HTML demoAvailableHTML;
	@UiField HTML supportHTML;
	
	public interface ILoginWindowCallback {
		public void onLoginButtonClicked(String username, String password);
	}

	private static final String ADMIN_EMAIL_PROPERTY = "admin.email";
	private static final String DEFAULT_ADMIN_EMAIL = "<admin.email not set>";
	private static final String DEMO_AVAILABLE_PROPERTY = "demo.available";
	private static final boolean DEFAULT_DEMO_AVAILABLE = false;
	private static final String DEMO_USERNAME_PROPERTY = "demo.username";
	private static final String DEFAULT_DEMO_USERNAME = "demo";
	private static final String DEMO_PASSWORD_PROPERTY = "demo.username";
	private static final String DEFAULT_DEMO_PASSWORD = "demo";
	
	private final ILoginWindowCallback callback;
	

	public LoginWindow(IConfigurationManager configurationManager, ILoginWindowCallback callback) {
	    super(configurationManager);
	    
	    this.callback = callback;

	    // Load UIBinder widgets.
		final Widget wid = uiBinder.createAndBindUi(this);
		
	    this.loadWidgets();
	    
	    // Apply internationalization to UIBinder-declared widgets.
	    this.applyI18n();
	    
	    // Add UIBinder widget to main panel.
	    this.mainPanel.add(wid);
	    
	    // Additional setup of the UIBinder controls (which can't be done
	    // before they are into the mainPanel).
	    this.setupWidgets();
	}
	
	
	private void setupWidgets() {
		this.mainPanel.setCellHeight(this.loginButton, "40px");
		this.mainPanel.setCellHeight(this.waitingLabel.getWidget(), "30px");
		this.mainPanel.setCellHeight(this.generalErrorLabel, "30px");
		
		this.mainPanel.setCellHeight(this.demoAvailableHTML, "40px");
	}


	/**
	 * Applies internationalization to UIBinder-declared widgets.
	 * @param i18n Provider of the messages.
	 */
	public void applyI18n() {
		this.usernameLabel.setText(this.i18nMessages.username() + ":");
		this.passwordLabel.setText(this.i18nMessages.password() + ":");
		this.loginButton.setText(this.i18nMessages.logIn());
	}
	
	
	@Override
	protected void loadWidgets(){
		super.loadWidgets();
	    
		// If true, all the panels have a border,
		// in order to design the layout easily.
		final boolean DESIGN_MODE = false;
		
		 
		// If ENTER is pressed, login as if the button had been clicked.
		final KeyPressHandler keyboardHandler = new KeyPressHandler(){
			@Override
			public void onKeyPress(KeyPressEvent event) {
			    if(event.getCharCode() == KeyCodes.KEY_ENTER)
					LoginWindow.this.onLoginButtonClicked(null);   
			}
		};
		
		for(int i = 0; i < IWebLabDeustoThemeMessages.LANGUAGES.length; ++i){
			final String curLanguage = IWebLabDeustoThemeMessages.LANGUAGES[i];
			final String curLanguageCode = IWebLabDeustoThemeMessages.LANGUAGE_CODES[i];
			final Anchor languageButton = new Anchor(curLanguage);
			languageButton.addClickHandler(
					new LanguageButtonClickHandler(curLanguageCode)
				);
			this.langsPanel.add(languageButton);
		}		
		this.langsPanel.setSpacing(15);
		
		this.loadUsernameAndPassword();
		this.usernameTextbox.addKeyPressHandler(keyboardHandler);
		this.passwordTextbox.addKeyPressHandler(keyboardHandler);
		
		
		// TODO: This is not currently handled the same way. Consider alternatives.
//		this.usernameErrorLabel.setStyleName(DefaultTheme.Style.ERROR_MESSAGE);
//		this.passwordErrorLabel.setStyleName(DefaultTheme.Style.ERROR_MESSAGE);
		
		
		//this.waitingLabel = new WlWaitingLabel();
		//this.mainPanel.add(this.waitingLabel.getWidget());

		
		//this.generalErrorLabel = new Label("");
		//this.generalErrorLabel.setStyleName(DefaultTheme.Style.ERROR_MESSAGE);
		//this.mainPanel.add(this.generalErrorLabel);

		
		final boolean demoAvailable = this.configurationManager.getBoolProperty(
				LoginWindow.DEMO_AVAILABLE_PROPERTY,
				LoginWindow.DEFAULT_DEMO_AVAILABLE
			);
		
		if ( demoAvailable ) {
			final String demoUsername = this.configurationManager.getProperty(
					LoginWindow.DEMO_USERNAME_PROPERTY,
					LoginWindow.DEFAULT_DEMO_USERNAME
				);		
			final String demoPassword = this.configurationManager.getProperty(
					LoginWindow.DEMO_PASSWORD_PROPERTY,
					LoginWindow.DEFAULT_DEMO_PASSWORD
				);	
			
			this.demoAvailableHTML.setHTML("<br/><br/><p>" + this.i18nMessages.demoLoginDetails(demoUsername, demoPassword) + "</p>");
		}
		
		final String adminEmail = this.configurationManager.getProperty(
				LoginWindow.ADMIN_EMAIL_PROPERTY,
				LoginWindow.DEFAULT_ADMIN_EMAIL
			);	
		
		final String translatedSupportHTML = "<p>" + this.i18nMessages.ifYouHaveTechnicalProblems("<a href=\"mailto:" + WlUtil.escape(adminEmail) + "\" target=\"_blank\">" + WlUtil.escapeNotQuote(adminEmail) + "</a>") + "</p>";
		this.supportHTML.setHTML(translatedSupportHTML);
		
		if ( DESIGN_MODE )
		{
			this.mainPanel.setBorderWidth(1);
			this.langsPanel.setBorderWidth(1);
			this.grid.setBorderWidth(1);
		}
	}
	
	
	private void loadUsernameAndPassword() {
		final Element usernameField = DOM.getElementById("hiddenUsername");
		final Element passwordField = DOM.getElementById("hiddenPassword");
		
		if(usernameField == null || passwordField == null)
			return;
		
		if(usernameField instanceof InputElement)
			this.usernameTextbox.setText(((InputElement)usernameField).getValue());
		
		if(passwordField instanceof InputElement)
			this.passwordTextbox.setText(((InputElement)passwordField).getValue());
	}


	private class LanguageButtonClickHandler implements ClickHandler{
		private final String languageCode;
		
		public LanguageButtonClickHandler(String languageCode){
			this.languageCode = languageCode;
		}

		public void onClick(ClickEvent sender) {
			Cookies.setCookie(WebLabClient.LOCALE_COOKIE, this.languageCode);
			WebLabClient.refresh(this.languageCode);
		}
	}
	
	public void showWrongLoginOrPassword(){
		this.generalErrorLabel.setText(this.i18nMessages.invalidUsernameOrPassword());
		this.waitingLabel.stop();
		this.waitingLabel.setText("");
		this.loginButton.setEnabled(true);
	}


	public void showError(String message) {
		this.generalErrorLabel.setText(message);
		this.waitingLabel.stop();
		this.waitingLabel.setText("");
		this.loginButton.setEnabled(true);
	}
	
	
	@UiHandler("loginButton")
	@SuppressWarnings("unused")
	void onLoginButtonClicked(ClickEvent e) {
		System.out.println("Handing loginButton event");
		
		boolean errors = false;
		LoginWindow.this.generalErrorLabel.setText("");
		errors |= checkUsernameTextbox();
		errors |= checkPasswordTextbox();
		if(!errors){
			LoginWindow.this.waitingLabel.setText(LoginWindow.this.i18nMessages.loggingIn());
			LoginWindow.this.waitingLabel.start();
			LoginWindow.this.loginButton.setEnabled(false);
			LoginWindow.this.callback.onLoginButtonClicked(
					getUsername(), 
					getPassword()
				);
		}
	}
	

	public void showMessage(String message) {
		this.generalErrorLabel.setText(message);
		this.loginButton.setEnabled(true);
	}
	
	
	public String getUsername(){
		return this.usernameTextbox.getText();
	}
	
	public String getPassword(){
		return this.passwordTextbox.getText(); 
	}
	
	public boolean checkUsernameTextbox(){
		if(this.getUsername().length() == 0){
			this.usernameErrorLabel.setText(
					this.i18nMessages.thisFieldCantBeEmpty()
				);
			return true;
		}else{
			this.usernameErrorLabel.setText("");
			return false;
		}
	}
	
	public boolean checkPasswordTextbox() {
		if(this.getPassword().length() == 0){
			this.passwordErrorLabel.setText(
				this.i18nMessages.thisFieldCantBeEmpty()
				);
			return true;
		}else{
			this.passwordErrorLabel.setText("");
			this.i18nMessages.thisFieldCantBeEmpty();
			return false;
		}
	}
	
}
