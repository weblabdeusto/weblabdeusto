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
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.comm;

import es.deusto.weblab.client.comm.exceptions.CommException;

public class FileResponseException extends CommException {
	private static final long serialVersionUID = 5380785892632516904L;

	public FileResponseException() {
		super();
	}

	public FileResponseException(String message, Throwable cause) {
		super(message, cause);
	}

	public FileResponseException(String message) {
		super(message);
	}

	public FileResponseException(Throwable cause) {
		super(cause);
	}
}