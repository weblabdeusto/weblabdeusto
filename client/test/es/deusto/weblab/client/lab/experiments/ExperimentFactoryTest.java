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
package es.deusto.weblab.client.lab.experiments;

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentNotFoundException;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.fpga.WebLabFpgaExperiment;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib.WebLabGpibExperiment;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib1.WebLabGpib1Experiment;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib2.WebLabGpib2Experiment;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pld.WebLabPldExperiment;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class ExperimentFactoryTest extends GWTTestCase {

	private static class ExperimentLoadedCallback implements IExperimentLoadedCallback{

		Throwable lastThrowable;
		ExperimentBase lastExperiment;
		
		@Override
		public void onExperimentLoaded(ExperimentBase experiment) {
			this.lastExperiment = experiment;
		}

		@Override
		public void onFailure(Throwable e) {
			this.lastThrowable = e;
		}
	}
	
	public final void testWrongExperimentID(){
		final ExperimentFactory factory = new ExperimentFactory(new IBoardBaseController(){
			@Override
			public void sendCommand(Command command) {
			}

			@Override
			public void onClean() {
				
			}

			@Override
			public void sendCommand(Command command, IResponseCommandCallback callback) {
			    
			}

			@Override
			public void sendFile(UploadStructure uploadStructure,
				IResponseCommandCallback callback) {
			    
			}
		});
		
		final ExperimentLoadedCallback callback = new ExperimentLoadedCallback();
		
		factory.experimentFactory(new ExperimentID(new Category("whatever"), "whatever"), callback, false);
		
		Assert.assertNotNull(callback.lastThrowable);
		Assert.assertTrue(callback.lastThrowable instanceof ExperimentNotFoundException);
	}

	public final void testRightExperimentID(){
		final ExperimentFactory factory = new ExperimentFactory(new IBoardBaseController(){
			@Override
			public void sendCommand(Command command) {
			}

			@Override
			public void onClean() {
			}

			@Override
			public void sendCommand(Command command, IResponseCommandCallback callback) {
			}

			@Override
			public void sendFile(UploadStructure uploadStructure,
				IResponseCommandCallback callback) {
			}
		});
		
		final ExperimentLoadedCallback callback = new ExperimentLoadedCallback();
		
		factory.experimentFactory(new ExperimentID(new Category("PLD experiments"), "ud-pld"), callback, false);
		Assert.assertTrue(callback.lastExperiment instanceof WebLabPldExperiment);
		
		factory.experimentFactory(new ExperimentID(new Category("FPGA experiments"), "ud-fpga"), callback, false);
		Assert.assertTrue(callback.lastExperiment instanceof WebLabFpgaExperiment);
		
		factory.experimentFactory(new ExperimentID(new Category("GPIB experiments"), "ud-gpib"), callback, false);
		Assert.assertTrue(callback.lastExperiment instanceof WebLabGpibExperiment);
		
		factory.experimentFactory(new ExperimentID(new Category("GPIB experiments"), "ud-gpib1"), callback, false);
		Assert.assertTrue(callback.lastExperiment instanceof WebLabGpib1Experiment);
	
		factory.experimentFactory(new ExperimentID(new Category("GPIB experiments"), "ud-gpib2"), callback, false);
		Assert.assertTrue(callback.lastExperiment instanceof WebLabGpib2Experiment);
	}

	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
