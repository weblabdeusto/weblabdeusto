package es.deusto.weblab.client.dto.experiments.commands;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;

import es.deusto.weblab.client.util.Base64;

/**
 * Represents binary information interchanged with the server. This
 * information will be binary information that should be decoded by
 * the experiment-dependent code. It will travel in base64.
 */
public class BinaryData extends InterchangedData{
	/**
	 * The information itself. It is represented as a byte [] here,
	 * but it will probably become a base64 string.
	 */
	private byte [] data;

	/**
	 * @return the data
	 */
	public byte[] getData() {
		return this.data;
	}

	/**
	 * @param data the data to set
	 */
	public void setData(byte[] data) {
		this.data = data;
	}

	@Override
	public JSONObject toJSON() {
		final JSONObject obj = new JSONObject();
		final String encodedBinary = Base64.encode(this.data);
		obj.put("binary", new JSONString(encodedBinary));
		return obj;
	}
}
