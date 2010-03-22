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

package es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyPressHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile.widgets.EasyGrid;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

class LoginWindow extends BaseWindow {

	interface LoginWindowUiBinder extends UiBinder<Widget, LoginWindow> {
	}

	public interface ILoginWindowCallback {
		public void onLoginButtonClicked(String username, String password);
	}

	private final LoginWindowUiBinder uiBinder = GWT.create(LoginWindowUiBinder.class);

	@UiField Label usernameLabel;
	@UiField Label passwordLabel;
	@UiField TextBox usernameTextbox;
	@UiField PasswordTextBox passwordTextbox;
	@UiField WlWaitingLabel waitingLabel;
	
	@UiField Anchor languages;

	@UiField Label messages;

	@UiField Label usernameErrorLabel;
	@UiField Label passwordErrorLabel;
	
	@UiField Button loginButton;
	@UiField EasyGrid grid;

	private final ILoginWindowCallback callback;

	LoginWindow(IConfigurationManager configurationManager, ILoginWindowCallback callback) {
		super(configurationManager);
		
		this.callback = callback;
		
		super.loadWidgets();
		
		final Widget wid = this.uiBinder.createAndBindUi(this);
		this.applyI18n();
		
		// If ENTER is pressed, login as if the button had been clicked.
		final KeyPressHandler keyboardHandler = new KeyPressHandler(){
			@Override
			public void onKeyPress(KeyPressEvent event) {
			    if(event.getCharCode() == KeyCodes.KEY_ENTER)
					LoginWindow.this.onLoginButtonClicked(null);   
			}
		};
		this.usernameTextbox.addKeyPressHandler(keyboardHandler);
		this.passwordTextbox.addKeyPressHandler(keyboardHandler);
		
		
		this.mainPanel.add(wid);
	}

	@UiHandler("loginButton")
	@SuppressWarnings("unused")
	void onLoginButtonClicked(ClickEvent e) {
		boolean errors = false;
		hideMessage();
		errors |= checkUsernameTextbox();
		errors |= checkPasswordTextbox();
		if(!errors){
			this.waitingLabel.setStyleName(".visible-message");
			this.waitingLabel.setText(LoginWindow.this.i18nMessages.loggingIn());
			this.waitingLabel.start();
			this.loginButton.setEnabled(false);
			this.callback.onLoginButtonClicked(
					this.usernameTextbox.getText(), 
					this.passwordTextbox.getText()
				);
		}
	}
	
	private boolean checkUsernameTextbox(){
		if(this.usernameTextbox.getText().length() == 0){
			showError(this.usernameErrorLabel, this.i18nMessages.thisFieldCantBeEmpty());
			return true;
		}
		
		hideError(this.usernameErrorLabel);
		return false;
	}
	
	private boolean checkPasswordTextbox() {
		if(this.passwordTextbox.getText().length() == 0){
			showError(this.passwordErrorLabel, this.i18nMessages.thisFieldCantBeEmpty());
			return true;
		}
		
		hideError(this.passwordErrorLabel);
		return false;
	}
	
	private void applyI18n() {
		this.usernameLabel.setText(this.i18nMessages.username() + ":");
		this.passwordLabel.setText(this.i18nMessages.password() + ":");
		this.loginButton.setText(this.i18nMessages.logIn());
		this.languages.setText(this.i18nMessages.moreLanguages());
	}
	
	@Override
	void showError(String message) {
		showError(this.messages, message);
	}

	private void showError(Label where, String message) {
		where.setStyleName(".visible-error"); // TODO: the color doesn't work :-S
		where.setText(message);
	}

	private void hideError(Label where) {
		where.setText("");
		where.setStyleName(".invisible");
	}

	private void hideMessage() {
		hideError(this.messages);
	}
	
	@Override
	void showMessage(String message) {
		this.messages.setText(message);
		this.messages.setStyleName(".visible-message");
	}
}
