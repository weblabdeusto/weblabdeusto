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

import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentException;

public abstract class ExperimentCreator {

	private final MobileSupport mobileSupport;
	private final String codeName;
	
	public ExperimentCreator(MobileSupport mobileSupport, String codeName){
		this.mobileSupport = mobileSupport;
		this.codeName      = codeName;
	}

	public MobileSupport getMobileSupport() {
		return this.mobileSupport;
	}
	
	public String getCodeName(){
		return this.codeName;
	}

	public abstract void createWeb(IBoardBaseController boardController, IExperimentLoadedCallback callback);

	public void createMobile(IBoardBaseController boardController, IExperimentLoadedCallback callback) {
		if(this.mobileSupport == MobileSupport.disabled)
			callback.onFailure(new ExperimentException("Couldn't create mobile version of experiment " + this.codeName + ": not supported"));
		else
			this.createWeb(boardController, callback);
	}

}
