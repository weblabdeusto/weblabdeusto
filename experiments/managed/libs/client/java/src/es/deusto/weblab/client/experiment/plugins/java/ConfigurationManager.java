package es.deusto.weblab.client.experiment.plugins.java;

import netscape.javascript.JSObject;

public class ConfigurationManager {
	
	public static final String GWT_HOST_PAGE_BASE_URL = "gwt.host.page.base.url";
	public static final String GWT_MODULE_BASE_URL    = "gwt.module.base.url";
	public static final String GWT_MODULE_NAME = "gwt.module.name";
	public static final String GWT_VERSION = "gwt.version";
	
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
