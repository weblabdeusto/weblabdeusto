package es.deusto.weblab.client.experiment.plugins.java;

import netscape.javascript.JSObject;

public class ConfigurationManager {
	
	private final JSObject jsobject; 
	
	ConfigurationManager(JSObject jsobject){
		this.jsobject = jsobject;
	}
		
	public int getIntProperty(String name){
		Object returnValue = this.jsobject.call("wl_getIntProperty", new Object[]{name});
		return ((Integer)returnValue).intValue();
	}
	
	public int getIntProperty(String name, String def){
		Object returnValue = this.jsobject.call("wl_getIntPropertyDef", new Object[]{name, def});
		return ((Integer)returnValue).intValue();
	}
	
	public String getProperty(String name){
		Object returnValue = this.jsobject.call("wl_getProperty", new Object[]{name});
		return (String)returnValue;
	}
	
	public String getProperty(String name, String def){
		Object returnValue = this.jsobject.call("wl_getPropertyDef", new Object[]{name, def});
		return (String)returnValue;
	}
}
