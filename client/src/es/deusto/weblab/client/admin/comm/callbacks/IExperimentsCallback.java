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
* Author: FILLME
*
*/

package es.deusto.weblab.client.admin.comm.callbacks;

import java.util.ArrayList;

import es.deusto.weblab.client.comm.callbacks.IWlAsyncCallback;
import es.deusto.weblab.client.dto.experiments.Experiment;

public interface IExperimentsCallback extends IWlAsyncCallback {
	public void onSuccess(ArrayList<Experiment> experiments);	
}
