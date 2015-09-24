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

package es.deusto.weblab.client.experiments.controlapp;

import es.deusto.weblab.client.experiments.redirect.RedirectCreatorFactory;

/**
 * Maintain compatibility with STUBA labs. Should use Redirect instead of control-app
 */
public class ControlAppCreatorFactory extends RedirectCreatorFactory {

	@Override
	public String getCodeName() {
		return "control-app";
	}
}
