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
* Author: FILLME
*
*/

package es.deusto.weblab.client.experiments.blank;

import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;

public class BlankNoMobileCreatorFactory extends BlankCreatorFactory {
	
	public BlankNoMobileCreatorFactory(){
		super(MobileSupport.disabled);
	}
	
	@Override
	public String getCodeName() {
		return "blank-no-mobile";
	}
}
