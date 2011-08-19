package es.deusto.weblab.client.dto.experiments.commands;

import com.google.gwt.json.client.JSONObject;

/**
 * Data sent by the user to the experiment or received from the experiment to the user.
 * Interchanged data can be text data {@link TextData}, binary data {@link BinaryData} 
 * or a file (text file {@link TextFileData} or binary file {@link BinaryFileData}). 
 *
 */
public abstract class InterchangedData {
	public abstract JSONObject toJSON();
}
