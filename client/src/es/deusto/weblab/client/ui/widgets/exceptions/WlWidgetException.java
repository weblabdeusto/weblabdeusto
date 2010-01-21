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
package es.deusto.weblab.client.ui.widgets.exceptions;

import es.deusto.weblab.client.exceptions.WlClientException;

public class WlWidgetException extends WlClientException {
	private static final long serialVersionUID = 7797395269457146776L;

	public WlWidgetException() {
	}

	public WlWidgetException(String arg0) {
		super(arg0);
	}

	public WlWidgetException(Throwable arg0) {
		super(arg0);
	}

	public WlWidgetException(String arg0, Throwable arg1) {
		super(arg0, arg1);
	}

}
