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
package es.deusto.weblab.client.lab.experiments;


public class ExperimentFactory {

	public static enum MobileSupport{
		full,
		limited,
		disabled
	}
	
	public interface IExperimentLoadedCallback{
		public void onExperimentLoaded(ExperimentBase experiment);
		public void onFailure(Throwable e);
	}	
}
