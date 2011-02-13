package es.deusto.weblab.client.dto.experiments.commands;

import com.google.gwt.json.client.JSONObject;

/**
 * Represents a file interchanged with the server. It is implemented
 * by {@link BinaryFileData} and {@link TextFileData}.
 */
public abstract class FileData extends InterchangedData {

	/**
	 * File description. Each file sent or received are described
	 * by a description, only processed by the experiment 
	 * dependent code. For instance, an experiment requiring some
	 * code and a data file might tag one file as "code", and other
	 * as "data". 
	 */
	private TextData fileDescription;
	
	/**
	 * @return the fileDescription
	 */
	public TextData getFileDescription() {
		return this.fileDescription;
	}
	
	/**
	 * @param fileDescription the fileDescription to set
	 */
	public void setFileDescription(TextData fileDescription) {
		this.fileDescription = fileDescription;
	}
	
	protected abstract InterchangedData getPayload();
	
	@Override
	public JSONObject toJSON(){
		final JSONObject obj = new JSONObject();
		obj.put("name", this.fileDescription.toJSON());
		obj.put("payload", getPayload().toJSON());
		return obj;
	}
}
