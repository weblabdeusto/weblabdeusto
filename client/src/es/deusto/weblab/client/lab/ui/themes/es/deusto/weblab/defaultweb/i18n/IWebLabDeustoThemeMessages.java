package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb.i18n;

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
	
	public String experimentPicture();
	public String experimentName();
	public String experimentCategory();
	public String timeAllowed();
	public String username();
	public String password();
	public String invalidUsernameOrPassword();
	public String loggingIn();
	public String thisFieldCantBeEmpty(String label);
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
	public String selectedExperiment();
	public String ifYouHaveTechnicalProblems(String adminMail);
	public String demoLoginDetails(String demoUsername, String demoPassword);
	public String support();
	public String demo();
	public String mobile();
	public String openSource();
	public String createAnAccount();
	public String dontHaveAnAccountFacebook();
	public String administrationPanel();
	public String weblabIsOpenSourceAvailable(String url);
	public String useMobileVersionClicking(String url);
	public String weblabDeustoIsARemote_long();
	public String experimentInteractionFinishedGoBack();
	public String information();
	public String clickHereToOpenExperiment();
}