/*
* Copyright (C) 2005-2009 University of Deusto
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

package es.deusto.weblab.client;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.http.client.URL;
import com.google.gwt.user.client.History;

public class HistoryProperties {
	
	private static final Map<String, String []> values = new HashMap<String, String[]>(); 
	
	HistoryProperties(){
		String currentToken = History.getToken();
		for(String token : currentToken.split("&")){
			final String key = token.split("=")[0];
			final String value;
			if(!token.contains("="))
				value = "";
			else{
				value = URL.decode(token.substring(token.indexOf('=')));
			}
			
			if(values.containsKey(key)){
				final String [] oldValue = values.get(key);
				final String [] newValue = new String[oldValue.length + 1];
				for(int i = 0; i < oldValue.length; ++i)
					newValue[i] = oldValue[i];
				newValue[newValue.length - 1] = key;
			}else
				values.put(key, new String[]{ value });
		}
	}
	
	static void load(){
		new HistoryProperties();
	}
	
	public static String getValue(String key){
		final String [] valuesForKey = values.get(key);
		if(valuesForKey == null)
			return null;
		return valuesForKey[0];
	}
	
	public static String getValue(String key, String def){
		final String [] valuesForKey = values.get(key);
		if(valuesForKey == null)
			return def;
		return valuesForKey[0];
	}
	
	public static String [] getValues(String key){
		return values.get(key);
	}
}
