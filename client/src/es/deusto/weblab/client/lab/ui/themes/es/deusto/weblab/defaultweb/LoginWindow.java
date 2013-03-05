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
import com.google.gwt.user.client.Window.Location;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DecoratorPanel;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.WebLabClientLab;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.i18n.IWebLabI18N;
import es.deusto.weblab.client.ui.widgets.WlAHref;
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
	@UiField Button createAccountButton;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField HTML demoAvailableHTML;
	@UiField HTML supportHTML;
	@UiField Grid featuresGrid;
	@UiField VerticalPanel facebookPanel;
	@UiField HTML openSourceAddressHTML;
	@UiField HTML mobileHTML;
	@UiField DecoratorPanel createAccountPanel;
	@UiField Image hostEntityLogo;
	@UiField HTML introText;
	@UiField VerticalPanel guestPanel;
	@UiField VerticalPanel messagesPanel;
	@UiField WlAHref institutionLink;
	@UiField DecoratorPanel olarexPanel;
	
	// Callbacks
	private final ILoginWindowCallback callback;
	
	// Properties
	private static final String ADMIN_EMAIL_PROPERTY = "admin.email";
	private static final String DEFAULT_ADMIN_EMAIL = "<admin.email not set>";
	
	private static final String CREATE_ACCOUNT_VISIBLE_PROPERTY = "create.account.visible";
	private static final boolean DEFAULT_CREATE_ACCOUNT_VISIBLE = true;
	
	private static final String FACEBOOK_LIKE_BOX_VISIBLE_PROPERTY = "facebook.like.box.visible";
	private static final boolean DEFAULT_FACEBOOK_LIKE_BOX_VISIBLE = true;

	private static final String FACEBOOK_LIKE_BOX_ID_PROPERTY = "facebook.like.box.app.id";
	private static final String DEFAULT_FACEBOOK_LIKE_BOX_ID = "147077572014824";

	private static final String FACEBOOK_LIKE_BOX_WIDTH_PROPERTY = "facebook.like.box.width";
	private static final int DEFAULT_FACEBOOK_LIKE_BOX_WIDTH = 350;

	private static final String FACEBOOK_LIKE_BOX_HEIGHT_PROPERTY = "facebook.like.box.height";
	private static final int DEFAULT_FACEBOOK_LIKE_BOX_HEIGHT = 185;

	public LoginWindow(IConfigurationManager configurationManager, ILoginWindowCallback callback) {
	    super(configurationManager);
	    
	    this.callback = callback;

	    this.loadWidgets();
	}
	
	@Override
	public Widget getWidget(){
		return this.containerPanel;
	}
	
	private static native String getVersionName()/*-{
		return $wnd.wlVersionMessage;
	}-*/;
	
	protected void loadWidgets(){
	    LoginWindow.uiBinder.createAndBindUi(this);
		 
		final String hostEntityLink = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_LINK, "");
		this.institutionLink.setHref(hostEntityLink);
		
		final boolean olarexVisible = this.configurationManager.getBoolProperty("olarex", false);
		this.olarexPanel.setVisible(olarexVisible);
	    
		// If ENTER is pressed, login as if the button had been clicked.
		final KeyDownHandler keyboardHandler = new KeyDownHandler(){
			@Override
			public void onKeyDown(KeyDownEvent event) {
			    if(event.getNativeKeyCode() == KeyCodes.KEY_ENTER)
					LoginWindow.this.onLoginButtonClicked(null);   
			}
		};
		
		this.langsPanel.add(new HTML(getVersionName() + " | "));
		
		for(int i = 0; i < IWebLabI18N.LANGUAGES.length; ++i){
			final String curLanguage = IWebLabI18N.LANGUAGES[i];
			final String curLanguageCode = IWebLabI18N.LANGUAGE_CODES[i];
			final Anchor languageLink = new Anchor(curLanguage);
			languageLink.addClickHandler(
					new LanguageButtonClickHandler(curLanguageCode)
				);
			this.langsPanel.add(languageLink);
		}		
		
		this.loadUsernameAndPassword();
		this.usernameTextbox.addKeyDownHandler(keyboardHandler);
		this.passwordTextbox.addKeyDownHandler(keyboardHandler);
		
		String hostEntityImage = this.configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_LOGIN_IMAGE, "");
		if(!hostEntityImage.isEmpty()){
			if(hostEntityImage.startsWith("/"))
				hostEntityImage = GWT.getModuleBaseURL() + hostEntityImage;
			this.hostEntityLogo.setUrl(hostEntityImage);
		}
		
		this.introText.setHTML(this.i18nMessages.weblabDeustoIsARemote_long());
		
		final boolean demoAvailable = this.configurationManager.getBoolProperty(
				WebLabClientLab.DEMO_AVAILABLE_PROPERTY,
				WebLabClientLab.DEFAULT_DEMO_AVAILABLE
			);
		
		if ( demoAvailable ) {
			final String demoUsername = this.configurationManager.getProperty( WebLabClientLab.DEMO_USERNAME_PROPERTY, WebLabClientLab.DEFAULT_DEMO_USERNAME);		
			final String demoPassword = this.configurationManager.getProperty( WebLabClientLab.DEMO_PASSWORD_PROPERTY, WebLabClientLab.DEFAULT_DEMO_PASSWORD);	
			this.demoAvailableHTML.setHTML(this.i18nMessages.demoLoginDetails(demoUsername, demoPassword));
			
		}else{
			this.featuresGrid.removeRow(1);
		}
		this.guestPanel.setVisible(demoAvailable);
		
		final boolean createAccountVisible = this.configurationManager.getBoolProperty(CREATE_ACCOUNT_VISIBLE_PROPERTY, DEFAULT_CREATE_ACCOUNT_VISIBLE);
		if(!createAccountVisible)
			this.createAccountPanel.setVisible(false);
				
		final String adminEmail = this.configurationManager.getProperty(
				LoginWindow.ADMIN_EMAIL_PROPERTY,
				LoginWindow.DEFAULT_ADMIN_EMAIL
			);
		
		final String translatedSupportHTML = this.i18nMessages.ifYouHaveTechnicalProblems("<a href=\"mailto:" + WlUtil.escape(adminEmail) + "\" target=\"_blank\">" + WlUtil.escapeNotQuote(adminEmail) + "</a>");
		this.supportHTML.setHTML(translatedSupportHTML);
		
		final String translatedOpenSourceAddress = this.i18nMessages.weblabIsOpenSourceAvailable("<a href=\"https://github.com/weblabdeusto/weblabdeusto/\" target=\"_blank\">https://github.com/weblabdeusto/weblabdeusto/</a>");
		this.openSourceAddressHTML.setHTML(translatedOpenSourceAddress);
		
		final String mobileURL = WebLabClient.getNewUrl(WebLabClient.MOBILE_URL_PARAM, "true");
		this.mobileHTML.setHTML(this.i18nMessages.useMobileVersionClicking(mobileURL));

		final boolean facebookLikeBoxVisible = this.configurationManager.getBoolProperty(FACEBOOK_LIKE_BOX_VISIBLE_PROPERTY, DEFAULT_FACEBOOK_LIKE_BOX_VISIBLE);
		if(facebookLikeBoxVisible){
			final int facebookIFrameWidth  = this.configurationManager.getIntProperty(FACEBOOK_LIKE_BOX_WIDTH_PROPERTY, DEFAULT_FACEBOOK_LIKE_BOX_WIDTH);
			final int facebookIFrameHeight = this.configurationManager.getIntProperty(FACEBOOK_LIKE_BOX_HEIGHT_PROPERTY, DEFAULT_FACEBOOK_LIKE_BOX_HEIGHT);
			final String facebookIFrameAppID = this.configurationManager.getProperty(FACEBOOK_LIKE_BOX_ID_PROPERTY, DEFAULT_FACEBOOK_LIKE_BOX_ID);
			final String facebookIFrameCode = "<iframe src=\"https://www.facebook.com/plugins/likebox.php?href=http://www.facebook.com/apps/application.php%3Fid%3D" + facebookIFrameAppID  
												+ "&amp;width=" + facebookIFrameWidth + "&amp;colorscheme=light&amp;show_faces=true&amp;stream=false&amp;header=false&amp;height=" + facebookIFrameHeight
												+ "\" scrolling=\"no\" frameborder=\"0\" style=\"border:none; overflow:hidden; width:" + facebookIFrameWidth 
												+ "px; height:" + facebookIFrameHeight + "px; border-style:solid; border-color: #135cae\" allowTransparency=\"true\"></iframe>";
			final HTML facebookIframe = new HTML(facebookIFrameCode);
			this.facebookPanel.add(facebookIframe);
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

	public void showWrongLoginOrPassword(){
		this.messagesPanel.setVisible(true);
		this.generalErrorLabel.setText(this.i18nMessages.invalidUsernameOrPassword());
		this.generalErrorLabel.setVisible(true);
		this.waitingLabel.stop();
		this.waitingLabel.setText("");
		this.waitingLabel.setVisible(false);
		this.loginButton.setEnabled(true);
		this.usernameTextbox.setFocus(true);
	}


    @Override
	public void showError(String message) {
    	this.messagesPanel.setVisible(true);
		this.generalErrorLabel.setText(message);
		this.generalErrorLabel.setVisible(true);
		this.waitingLabel.stop();
		this.waitingLabel.setText("");
		this.waitingLabel.setVisible(false);
		this.loginButton.setEnabled(true);
		this.usernameTextbox.setFocus(true);
	}
	
	@UiHandler("loginButton")
	void onLoginButtonClicked(@SuppressWarnings("unused") ClickEvent e) {
		boolean errors = false;
		LoginWindow.this.generalErrorLabel.setText("");
		LoginWindow.this.generalErrorLabel.setVisible(false);
		errors |= this.checkUsernameTextbox();
		errors |= this.checkPasswordTextbox();
		if(!errors){
			startLoginProcess(getUsername(), getPassword());
		}
	}
	
	@UiHandler("guestButton")
	void onGuestButtonClicked(@SuppressWarnings("unused") ClickEvent e) {
		final String demoUsername = this.configurationManager.getProperty( WebLabClientLab.DEMO_USERNAME_PROPERTY, WebLabClientLab.DEFAULT_DEMO_USERNAME);		
		final String demoPassword = this.configurationManager.getProperty( WebLabClientLab.DEMO_PASSWORD_PROPERTY, WebLabClientLab.DEFAULT_DEMO_PASSWORD);	

		startLoginProcess(demoUsername, demoPassword);
	}

	private void startLoginProcess(String username, String password) {
		this.messagesPanel.setVisible(true);
		this.waitingLabel.setText(LoginWindow.this.i18nMessages.loggingIn());
		this.waitingLabel.start();
		this.waitingLabel.setVisible(true);
		this.loginButton.setEnabled(false);
		this.callback.onLoginButtonClicked(username, password);
	}
	
	@UiHandler("createAccountButton")
	void onCreateAccountClicked(@SuppressWarnings("unused") ClickEvent e){
		Location.replace("http://apps.facebook.com/weblab-deusto");
	}
	
    @Override
	public void showMessage(String message) {
    	this.messagesPanel.setVisible(true);
		this.generalErrorLabel.setText(message);
		this.generalErrorLabel.setVisible(true);
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

	void setUsernameFocus() {
		this.usernameTextbox.setFocus(true);
	}

	void setLoginFocus() {
		this.loginButton.setFocus(true);
	}	
}
