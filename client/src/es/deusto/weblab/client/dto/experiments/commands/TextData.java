package es.deusto.weblab.client.dto.experiments.commands;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;

/**
 * Represents text information that will be interchanged. It contains
 * the string itself.
 * 
 */
public class TextData extends InterchangedData {
	/**
	 * The string itself. It will travel encoded in base64.
	 */
	private String data;
	
	/**
	 * @return the data
	 */
	public String getData() {
		return this.data;
	}

	/**
	 * @param data the data to set
	 */
	public void setData(String data) {
		this.data = data;
	}

	@Override
	public JSONObject toJSON(){
		final JSONObject obj = new JSONObject();
		obj.put("data", new JSONString(this.data));
		return obj;
	}
}
