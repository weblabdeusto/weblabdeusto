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

package es.deusto.weblab.client;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.http.client.URL;
import com.google.gwt.user.client.History;

public class HistoryProperties {
	
	public static final String HEADER_VISIBLE      = "header.visible";
	public static final String WIDGET              = "widget";
	public static final String EXPERIMENT_NAME     = "exp.name";
	public static final String EXPERIMENT_CATEGORY = "exp.category";
	public static final String PAGE                = "page"; 
	
	public static final String HOME                = "home";
	public static final String EXPERIMENT          = "experiment";
	public static final String BACK                = "back_url";
	
	private static final Map<String, String []> values = new HashMap<String, String[]>();
	
	HistoryProperties(){
		reloadHistory();
	}
	
	public static void reloadHistory() {
		values.clear();
		String currentToken = History.getToken();
		for(String token : currentToken.split("&")){
			final String key = token.split("=")[0];
			final String value;
			if(!token.contains("="))
				value = "";
			else{
				value = URL.decode(token.substring(token.indexOf('=') + 1));
			}
			
			if(values.containsKey(key)){
				final String [] oldValue = values.get(key);
				final String [] newValue = new String[oldValue.length + 1];
				for(int i = 0; i < oldValue.length; ++i)
					newValue[i] = oldValue[i];
				newValue[newValue.length - 1] = key;
			}else if(!key.isEmpty())
				values.put(key, new String[]{ value });
		}
	}
	
	public static String encode(String text) {
		String encoded = URL.encode(text);
		encoded = encoded.replace(":", "%3A"); 
		encoded = encoded.replace("/", "%2F");
		encoded = encoded.replace("#", "%23");
		encoded = encoded.replace("&", "%26");
		encoded = encoded.replace("=", "%3D");
		return encoded;
	}
	
	public static String decode(String encoded) {
		String text = encoded.replace("%3A", ":"); 
		text = text.replace("%2F", "/");
		text = text.replace("%23", "#");
		text = text.replace("%26", "&");
		text = text.replace("%3D", "=");
		return URL.decode(text);
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

	public static boolean getBooleanValue(String key, boolean b) {
		final String value = getValue(key, b?"true":"false");
		return value.toLowerCase().equals("true") || value.toLowerCase().equals("yes"); 
	}
	
	private static String values2string() {
		final StringBuilder builder = new StringBuilder();
		for(String key : values.keySet())
			for(String value : values.get(key)) {
				builder.append(key);
				builder.append("=");
				builder.append(value);
				builder.append("&");
			}
		String finalString = builder.toString();
		if(finalString.endsWith("&"))
			finalString = finalString.substring(0, finalString.length() - 1);
		
		return finalString;
	}
	
	public static void setValue(String key, String value) {
		values.put(key, new String[]{ value });
		History.newItem(values2string(), false);
	}
	
	public static void setValues(Map<String, String> newValues) {
		for(String key : newValues.keySet())
			values.put(key, new String[]{ newValues.get(key) });
		History.newItem(values2string(), false);
	}
	
	public static void setValue(String key, boolean value) {
		setValue(key, Boolean.toString(value));
	}
	
	public static void removeValues(String ... keys) {
		removeValuesWithoutUpdating(keys);
		update();
	}
	
	public static void removeValuesWithoutUpdating(String ... keys) {
		for(String key : keys)
			values.remove(key);
	}
	
	public static void update(){
		History.newItem(values2string(), false);
	}
	
	public static void appendValue(String key, String value) {
		if(values.containsKey(key)) {
			String [] newValues = new String[values.get(key).length + 1];
			for(int i = 0; i < values.get(key).length; ++i) 
				newValues[i] = values.get(key)[i];
			newValues[values.get(key).length] = value;
			values.put(key, newValues);
		} else {
			values.put(key, new String[]{ value });
		}
		History.newItem(values2string(), false);
	}

}
