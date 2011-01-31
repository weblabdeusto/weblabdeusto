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

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyDownEvent;
import com.google.gwt.event.dom.client.KeyDownHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb.i18n.IWebLabDeustoThemeMessages;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

class LoginWindow extends BaseWindow {
	
	interface MyUiBinder extends UiBinder<Widget, LoginWindow> {}
	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);	

	public interface ILoginWindowCallback {
		public void onLoginButtonClicked(String username, String password);
	}
	
	// Widgets
	@UiField VerticalPanel containerPanel;
	@UiField HorizontalPanel langsPanel;
	@UiField Label usernameLabel;
	@UiField Label passwordLabel;
	@UiField TextBox usernameTextbox;
	@UiField PasswordTextBox passwordTextbox;
	@UiField Button loginButton;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField HTML demoAvailableHTML;
	@UiField HTML supportHTML;
	
	// Callbacks
	private final ILoginWindowCallback callback;
	
	// Properties
	private static final String ADMIN_EMAIL_PROPERTY = "admin.email";
	private static final String DEFAULT_ADMIN_EMAIL = "<admin.email not set>";
	private static final String DEMO_AVAILABLE_PROPERTY = "demo.available";
	private static final boolean DEFAULT_DEMO_AVAILABLE = false;
	private static final String DEMO_USERNAME_PROPERTY = "demo.username";
	private static final String DEFAULT_DEMO_USERNAME = "demo";
	private static final String DEMO_PASSWORD_PROPERTY = "demo.username";
	private static final String DEFAULT_DEMO_PASSWORD = "demo";

	public LoginWindow(IConfigurationManager configurationManager, ILoginWindowCallback callback) {
	    super(configurationManager);
	    
	    this.callback = callback;

	    this.loadWidgets();
	}
	
	@Override
	public Widget getWidget(){
		return this.containerPanel;
	}
	
	protected void loadWidgets(){
	    LoginWindow.uiBinder.createAndBindUi(this);
		 
		// If ENTER is pressed, login as if the button had been clicked.
		final KeyDownHandler keyboardHandler = new KeyDownHandler(){
			@Override
			public void onKeyDown(KeyDownEvent event) {
			    if(event.getNativeKeyCode() == KeyCodes.KEY_ENTER)
					LoginWindow.this.onLoginButtonClicked(null);   
			}
		};
		
		for(int i = 0; i < IWebLabDeustoThemeMessages.LANGUAGES.length; ++i){
			final String curLanguage = IWebLabDeustoThemeMessages.LANGUAGES[i];
			final String curLanguageCode = IWebLabDeustoThemeMessages.LANGUAGE_CODES[i];
			final Anchor languageLink = new Anchor(curLanguage);
			languageLink.addClickHandler(
					new LanguageButtonClickHandler(curLanguageCode)
				);
			this.langsPanel.add(languageLink);
		}		
		
		this.loadUsernameAndPassword();
		this.usernameTextbox.addKeyDownHandler(keyboardHandler);
		this.passwordTextbox.addKeyDownHandler(keyboardHandler);
		
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
			
			this.demoAvailableHTML.setHTML(this.i18nMessages.demoLoginDetails(demoUsername, demoPassword));
		}
		
		final String adminEmail = this.configurationManager.getProperty(
				LoginWindow.ADMIN_EMAIL_PROPERTY,
				LoginWindow.DEFAULT_ADMIN_EMAIL
			);	
		
		final String translatedSupportHTML = this.i18nMessages.ifYouHaveTechnicalProblems("<a href=\"mailto:" + WlUtil.escape(adminEmail) + "\" target=\"_blank\">" + WlUtil.escapeNotQuote(adminEmail) + "</a>");
		this.supportHTML.setHTML(translatedSupportHTML);
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

	public void showWrongLoginOrPassword(){
		this.generalErrorLabel.setText(this.i18nMessages.invalidUsernameOrPassword());
		this.waitingLabel.stop();
		this.waitingLabel.setText("");
		this.loginButton.setEnabled(true);
	}


    @Override
	public void showError(String message) {
		this.generalErrorLabel.setText(message);
		this.waitingLabel.stop();
		this.waitingLabel.setText("");
		this.loginButton.setEnabled(true);
	}
	
	@UiHandler("loginButton")
	void onLoginButtonClicked(@SuppressWarnings("unused") ClickEvent e) {
		boolean errors = false;
		LoginWindow.this.generalErrorLabel.setText("");
		errors |= this.checkUsernameTextbox();
		errors |= this.checkPasswordTextbox();
		if(!errors){
			LoginWindow.this.waitingLabel.setText(LoginWindow.this.i18nMessages.loggingIn());
			LoginWindow.this.waitingLabel.start();
			LoginWindow.this.loginButton.setEnabled(false);
			LoginWindow.this.callback.onLoginButtonClicked(this.getUsername(), this.getPassword());
		}
	}
	
    @Override
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
	
	private boolean checkUsernameTextbox(){
		if(this.getUsername().length() == 0){
			final String username = this.i18nMessages.username();
			this.showError(this.i18nMessages.thisFieldCantBeEmpty(username));
			return true;
		}else{
			return false;
		}
	}
	
	private boolean checkPasswordTextbox() {
		if(this.getPassword().length() == 0){
			final String password = this.i18nMessages.password();
			this.showError(this.i18nMessages.thisFieldCantBeEmpty(password));
			return true;
		}else{
			return false;
		}
	}	
	
	private class LanguageButtonClickHandler implements ClickHandler{
		private final String languageCode;
		
		public LanguageButtonClickHandler(String languageCode){
			this.languageCode = languageCode;
		}

		@Override
		public void onClick(ClickEvent sender) {
			Cookies.setCookie(WebLabClient.LOCALE_COOKIE, this.languageCode);
			WebLabClient.refresh(this.languageCode);
		}
	}	
}