/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.configuration;

import java.util.HashMap;
import java.util.Map;

public class ConfigVariables {

	// private final static Object NO_DEFAULT = new Object();
	
	private final static Map<String, Argument> VALUES = new HashMap<String, ConfigVariables.Argument>();
	
	// Categories
	public final static String CORE        = "Core";	
	public final static String GENERAL     = "General";
	public final static String POLLING     = "Polling";
	public final static String EXPERIMENTS = "Experiments"; 
	
	private static final String ADMIN_EMAIL_PROPERTY = "admin.email";
	private static final String DEFAULT_ADMIN_EMAIL = "<admin.email not set>";
	
	private static final String CREATE_ACCOUNT_VISIBLE_PROPERTY = "create.account.visible";
	private static final boolean DEFAULT_CREATE_ACCOUNT_VISIBLE = true;
		
	
	static {
		VALUES.put(ADMIN_EMAIL_PROPERTY, new Argument(CORE, String.class, DEFAULT_ADMIN_EMAIL, "Administrator's e-mail address"));
		VALUES.put(CREATE_ACCOUNT_VISIBLE_PROPERTY, new Argument(CORE, Boolean.class, DEFAULT_CREATE_ACCOUNT_VISIBLE, "Show the link to create a new account"));
	}
	
	
	public static void main(String [] args) {
		
	}
	
	public static class Argument {
		
		private final String category;
		private final Class<?> type;
		private final Object def;
		private final String message;
		
		Argument(String category, Class<?> type, Object def, String message) {
			this.category = category;
			this.type = type;
			this.def = def;
			this.message = message;
		}

		public String getCategory() {
			return this.category;
		}

		public Class<?> getType() {
			return this.type;
		}

		public Object getDef() {
			return this.def;
		}

		public String getMessage() {
			return this.message;
		}
	}
}
