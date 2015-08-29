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
* Author: FILLME
*
*/

package es.deusto.weblab.client.dto.experiments.commands;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;

public class ArrayOfInterchangedData extends InterchangedData {

	private final InterchangedData [] interchangedData;
	
	public ArrayOfInterchangedData(InterchangedData [] interchangedData){
		this.interchangedData = interchangedData;
	}
	
	@Override
	public JSONObject toJSON() {
		final JSONArray array = new JSONArray();
		for(int i = 0; i < this.interchangedData.length; ++i)
			array.set(i, this.interchangedData[i].toJSON());
		final JSONObject obj = new JSONObject();
		obj.put("elements", array);
		return obj;
	}

}
