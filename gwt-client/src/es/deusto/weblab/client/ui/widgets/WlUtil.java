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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.ui.widgets;

public class WlUtil {
	public static String escape(String text){
		String returnValue = text;
		// Taken from the Python's cgi module (function "escape")
		returnValue = returnValue.replaceAll("&", "&amp;");
		returnValue = returnValue.replaceAll("<", "&lt;"); 
		returnValue = returnValue.replaceAll(">", "&gt;"); 
		returnValue = returnValue.replaceAll("\"", "&quot;");
		return returnValue;
	}
	public static String escapeNotQuote(String text){
		String returnValue = text;
		// Taken from the Python's cgi module (function "escape")
		returnValue = returnValue.replaceAll("&", "&amp;");
		returnValue = returnValue.replaceAll("<", "&lt;"); 
		returnValue = returnValue.replaceAll(">", "&gt;"); 
		return returnValue;
	}
}
