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

import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyPressHandler;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme.i18n.IWebLabDeustoThemeMessages;
import es.deusto.weblab.client.ui.widgets.WlHorizontalPanel;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class LoginWindow extends BaseWindow {

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

	// Widgets
	private TextBox usernameTextbox;
	private PasswordTextBox passwordTextbox;
	private Label usernameErrorLabel;
	private Label passwordErrorLabel;
	private WlWaitingLabel waitingLabel;
	private Button loginButton;
	private Label generalErrorLabel;

	public LoginWindow(IConfigurationManager configurationManager, ILoginWindowCallback callback) {
	    super(configurationManager);
	    this.callback = callback;

	    this.loadWidgets();
	}
	
	@Override
	protected void loadWidgets(){
		super.loadWidgets();
	    
		// If true, all the panels have a border,
		// in order to design the layout easily.
		final boolean DESIGN_MODE = false;
		
		final LoginClickHandler buttonListener = new LoginClickHandler();
		final KeyPressHandler keyboardHandler = new KeyPressHandler(){
			@Override
			public void onKeyPress(KeyPressEvent event) {
			    if(event.getCharCode() == KeyCodes.KEY_ENTER)
				buttonListener.onClick(null);
			    
			}
		};
		
		final WlHorizontalPanel languagesPanel = new WlHorizontalPanel();
		for(int i = 0; i < IWebLabDeustoThemeMessages.LANGUAGES.length; ++i){
			final String curLanguage = IWebLabDeustoThemeMessages.LANGUAGES[i];
			final String curLanguageCode = IWebLabDeustoThemeMessages.LANGUAGE_CODES[i];
			final Anchor languageButton = new Anchor(curLanguage);
			languageButton.addClickHandler(
					new LanguageButtonClickHandler(curLanguageCode)
				);
			languagesPanel.add(languageButton);
		}		
		languagesPanel.setSpacing(15);
		
		this.mainPanel.add(languagesPanel);

		final Grid grid = new Grid(2,3);
		grid.setWidget(0,0, new Label(this.i18nMessages.username() + ": "));
		grid.setWidget(1,0, new Label(this.i18nMessages.password() + ": "));
		grid.setCellSpacing(5);
		
		this.usernameTextbox = new TextBox();
		this.passwordTextbox = new PasswordTextBox();
		this.loadUsernameAndPassword();
		this.usernameTextbox.addKeyPressHandler(keyboardHandler);
		this.passwordTextbox.addKeyPressHandler(keyboardHandler);

		grid.setWidget(0,1, this.usernameTextbox);
		grid.setWidget(1,1, this.passwordTextbox);

		this.usernameErrorLabel = new Label(" ");
		this.passwordErrorLabel = new Label(" ");
		this.usernameErrorLabel.setStyleName(DefaultTheme.Style.ERROR_MESSAGE);
		this.passwordErrorLabel.setStyleName(DefaultTheme.Style.ERROR_MESSAGE);

		grid.setWidget(0, 2, this.usernameErrorLabel);
		grid.setWidget(1, 2, this.passwordErrorLabel);

		this.mainPanel.add(grid);
			
		this.loginButton = new Button(this.i18nMessages.logIn());
		this.loginButton.addClickHandler(buttonListener);
		this.mainPanel.add(this.loginButton);
		this.mainPanel.setCellHeight(this.loginButton, "40px");
		
		this.waitingLabel = new WlWaitingLabel();
		this.mainPanel.add(this.waitingLabel.getWidget());
		this.mainPanel.setCellHeight(this.waitingLabel.getWidget(), "30px");
		
		this.generalErrorLabel = new Label("");
		this.generalErrorLabel.setStyleName(DefaultTheme.Style.ERROR_MESSAGE);
		this.mainPanel.add(this.generalErrorLabel);
		this.mainPanel.setCellHeight(this.generalErrorLabel, "30px");
		
		boolean demoAvailable = this.configurationManager.getBoolProperty(
				LoginWindow.DEMO_AVAILABLE_PROPERTY,
				LoginWindow.DEFAULT_DEMO_AVAILABLE
			);
		if ( demoAvailable ) {
			String demoUsername = this.configurationManager.getProperty(
					LoginWindow.DEMO_USERNAME_PROPERTY,
					LoginWindow.DEFAULT_DEMO_USERNAME
				);		
			String demoPassword = this.configurationManager.getProperty(
					LoginWindow.DEMO_PASSWORD_PROPERTY,
					LoginWindow.DEFAULT_DEMO_PASSWORD
				);			
			HTML demoAvailableHTML = new HTML(this.i18nMessages.demoLoginDetails(demoUsername, demoPassword));
			this.mainPanel.add(demoAvailableHTML);
			this.mainPanel.setCellHeight(demoAvailableHTML, "40px");
		}
		
		String adminEmail = this.configurationManager.getProperty(
				LoginWindow.ADMIN_EMAIL_PROPERTY,
				LoginWindow.DEFAULT_ADMIN_EMAIL
			);		
		HTML supportHTML = new HTML(this.i18nMessages.ifYouHaveTechnicalProblems("<a href=\"mailto:" + WlUtil.escape(adminEmail) + "\" target=\"_blank\">" + WlUtil.escapeNotQuote(adminEmail) + "</a>"));
		this.mainPanel.add(supportHTML);
		
		if ( DESIGN_MODE )
		{
			this.mainPanel.setBorderWidth(1);
			languagesPanel.setBorderWidth(1);
			grid.setBorderWidth(1);
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
	
	private class LoginClickHandler implements ClickHandler{
		
		public void onClick(ClickEvent sender) {
			boolean errors = false;
			LoginWindow.this.generalErrorLabel.setText("");
			errors |= this.checkUsernameTextbox();
			errors |= this.checkPasswordTextbox();
			if(!errors){
				LoginWindow.this.waitingLabel.setText(LoginWindow.this.i18nMessages.loggingIn());
				LoginWindow.this.waitingLabel.start();
				LoginWindow.this.loginButton.setEnabled(false);
				LoginWindow.this.callback.onLoginButtonClicked(
						this.getUsername(), 
						this.getPassword()
					);
			}
		}
		
		private String getUsername(){
			return LoginWindow.this.usernameTextbox.getText();
		}
		
		private String getPassword(){
			return LoginWindow.this.passwordTextbox.getText(); 
		}
		
		private boolean checkUsernameTextbox(){
			if(this.getUsername().length() == 0){
				LoginWindow.this.usernameErrorLabel.setText(
						LoginWindow.this.i18nMessages.thisFieldCantBeEmpty()
					);
				return true;
			}else{
				LoginWindow.this.usernameErrorLabel.setText("");
				return false;
			}
		}
		private boolean checkPasswordTextbox(){
			if(this.getPassword().length() == 0){
				LoginWindow.this.passwordErrorLabel.setText(
						LoginWindow.this.i18nMessages.thisFieldCantBeEmpty()
					);
				return true;
			}else{
				LoginWindow.this.passwordErrorLabel.setText("");
				return false;
			}
		}
	}

	public void showMessage(String message) {
		this.generalErrorLabel.setText(message);
		this.loginButton.setEnabled(true);
	}
}
