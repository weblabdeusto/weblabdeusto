package es.deusto.weblab.client.experiments.visir.i18n;

import com.google.gwt.i18n.client.Messages;

public interface IVisirMessages extends Messages {
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
	

	public String visirExperiment();
	public String flashTimeout(String errorMessage);
	public String circuitsAvailable();
	public String footerMessage();
}
