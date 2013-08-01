package es.deusto.weblab.client.i18n;

import com.google.gwt.i18n.client.Messages;
import com.google.gwt.safehtml.shared.SafeHtml;

public interface IWebLabI18N extends Messages {
	
	public String [] LANGUAGES = {
            "Čeština",
			"English",
			"Español",
			"Euskara",
            "Deutsch",
            "Français",
            "Magyar",
            "Nederlands",
            "Português",
            "Română",
            "Русский",
            "Slovenčina",
	};
	
	// Must use the same order
	public String [] LANGUAGE_CODES = {
            "cs",
			"en",
			"es",
			"eu",
            "de",
            "fr",
            "hu",
            "nl",
            "pt",
            "ro",
            "ru",
            "sk",
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
	public SafeHtml demoLoginDetails(String demoUsername, String demoPassword);
	public String support();
	public String demo();
	public String mobile();
	public String openSource();
	public String createAnAccount();
	public String dontHaveAnAccountFacebook();
	public String administrationPanel();
	public String weblabIsOpenSourceAvailable(String url);
	public String useMobileVersionClicking(String url);
	public SafeHtml weblabDeustoIsARemote_long();
	public String experimentInteractionFinishedGoBack();
	public String information();
	public String someExperimentsAreAvailableForDemo();
	public String loginAsGuest();
	public String poweredBy();
	public String experimentHostedBy();
	public String directLink();
	public String clickHere();
	public String back();


	public String moreLanguages();
	public String fieldCantBeEmpty();

	public String notAllowedToAccessAdminPanel();
	public String accesses();
	public String search();
	
	public String passwordsDoNotMatch();
	public String users();
	public String clearFilter();
	public String chooseAValue();
	public String group();
	public String to();
	public String from();
	public String filter();
	public String experiment();

	// VISIR
	public String visirExperiment();
	public String flashTimeout(String errorMessage);
	public String circuitsAvailable();
	public SafeHtml footerMessage();
	
	// XILINX
	public String selectProgramToSend();
	public String upload();
	public String thisDemoDemonstratesMultiresourceXilinx();
	public String thisDemoDoesNotAllowUpload();
	public String fileSent();
	public String deviceReady();
	public String deviceProgrammingFailed();
	public String fileNotAllowed();
	public String sendingFile();
	public String finishingProgramming();
	
	// VM
	public String yourVirtualMachineIsNotYetReady(String seconds);
	public String finishing();
	public String doneVMisReady();
	public String loadingPleaseWait(int seconds);
	public String yourVirtualMachineIsNowReady();
	public String vmAddress();
	public String loadJavaVNCApplet();

	// UNR
	public String redirectingTo();
	public String remoteSystem();
	
	// Submarine
	public String submarineIsOnlyAvailableFewTimes();
	public String activateSubmarineControlPanel();
	public String submarineIsProbablyOutOfBattery();
	public String yesActivateSubmarineControlPanel();
	public String fishFed();
	public String fishAlreadyFed(String hours);
	public String fishNotFed(String reason);
	public String youCanNowControlTheAquarium();
	
	// Robot
	public String theProgramIsBeingExecutedInTheBot();
	public String thereWasAnError(String message);
	public String failed(String message);
	public String selectWhatProgramShouldBeSent();
	public String youCanControlTheBot();
	public String programmingInteractiveDemo();

	// Logic
	public String welcomeToWebLabDeustoLogic();
	public String replaceTheUnknownGate();
	public String solveAsManyCircuitsAsPossible();
	public String youCanCheckYourScoreAt();
	public String finishedWaitingPunctuation();
	public String finishedYourPunctuation(String results);
	public String sendingSolution();
	public String wellDone1point();
	public String wrongOneGameOver(int points);
	public String chooseCorrectGate();
	public String checkTheRankingHere(String where);
	public String sendSolution();
	public String thisLaboratoryIsManagedByJavaAppletILAB();

	// Binary
	public String pureBCD();
	public String otherBCDs();
	public String selectACode();
	public String selectOtherCode();
	public String loading(String what);
}
