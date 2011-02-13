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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/

package es.deusto.weblab.client.util;

public class Base64 {
	// TODO
	public static String encode(String message){
		return message;
	}
	
	public static String encode(byte [] data){
		return data.toString();
	}
	
	public static byte [] decodeBinary(String value){
		return new byte[value.length()];
	}
	
	public static String decodeString(String value){
		return value;
	}
}
