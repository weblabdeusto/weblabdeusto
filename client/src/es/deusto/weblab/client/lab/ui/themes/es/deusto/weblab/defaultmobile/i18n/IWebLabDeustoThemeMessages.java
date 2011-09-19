package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.i18n;

import com.google.gwt.i18n.client.Messages;

public interface IWebLabDeustoThemeMessages extends Messages {
	
	public String [] LANGUAGES = {
			"english",
			"castellano",
			"euskara"
	};
	
	// Must use the same order
	public String [] LANGUAGE_CODES = {
			"en",
			"es",
			"eu"
	};
	
	public String moreLanguages();
	public String experimentName();
	public String experimentCategory();
	public String timeAllowed();
	public String username();
	public String password();
	public String invalidUsernameOrPassword();
	public String loggingIn();
	public String thisFieldCantBeEmpty();
	public String backToMyExperiments();
	public String reserve();
	public String reserving();
	public String welcomeToWebLabDeusto();
	public String finish();
	public String showExperiments();
	public String logOut();
	public String welcome();
	public String waitingForConfirmation();
	public String waitingInQueuePosition(int position);
	public String waitingForAnInstancePosition(String adminMail, int position);
	public String logIn();
	public String choose();
	public String myExperiments();
	public String reserveThisExperiment();
	public String ifYouHaveTechnicalProblems(String adminMail);
	public String demoLoginDetails(String demoUsername, String demoPassword);
	public String experimentInteractionFinishedGoBack();
}
