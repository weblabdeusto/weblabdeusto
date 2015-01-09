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

package es.deusto.weblab.client.lab.experiments.util.applets;

import es.deusto.weblab.client.lab.experiments.ExperimentParameter;
import es.deusto.weblab.client.lab.experiments.ExperimentParameterDefault;

public class AbstractCreatorFactory {
	public static final ExperimentParameterDefault PAGE_FOOTER = new ExperimentParameterDefault("page.footer", "Footer of the application (below the application loaded, defaultValue)", "");
	public static final ExperimentParameter HEIGHT = new ExperimentParameter("height", ExperimentParameter.Type.integer, "Application height");
	public static final ExperimentParameter WIDTH = new ExperimentParameter("width", ExperimentParameter.Type.integer, "Application width");
	public static final ExperimentParameter MESSAGE = new ExperimentParameter("message", ExperimentParameter.Type.string, "Message to be displayed");
}
