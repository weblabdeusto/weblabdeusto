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

package es.deusto.weblab.client.experiments;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.binary.WebLabBinaryExperiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.dummy.WebLabDummyExperiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.fpga.WebLabFpgaExperiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib.WebLabGpibExperiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib1.WebLabGpib1Experiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib2.WebLabGpib2Experiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.WebLabLogicExperiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.pic.WebLabPicExperiment;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.pld.WebLabPldExperiment;
import es.deusto.weblab.client.experiments.util.applets.flash.FlashAppExperimentBase;
import es.deusto.weblab.client.experiments.util.applets.java.JavaAppletExperimentBase;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;

/**
 * This class acts as a registry of all the available entries for the currently known experiments.
 * In order to add a new experiment, just add another element to the list as the sample one (the one commented)
 */
class EntryRegistry {
	static final ExperimentEntry [] entries = {
		
		//
		// Example of new entry
		// 
		/*
		
		   new ExperimentEntry("Here write the category name", "Here write the experiment name of this category"){
		 		@Override
		 		public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
		 			// Here write down a constructor of something that implements ExperimentBase if you are using GWT
		  			// In the case of Java Applets and Flash, use FlashAppExperimentBase and JavaAppletExperimentBase, as seen below (flashdummy and javadummy)
		  			return new HereTheClassThatInheritsFromExperimentBase(arguments);
		  		}
		   }
		   
		 */
		
		
		new ExperimentEntry("Dummy experiments", "flashdummy"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				final int width      = 500;
				final int height     = 350;
				final String swfFile = "WeblabFlashSample.swf";
				final String message = "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Adobe Flash in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible.";

				return new FlashAppExperimentBase(configurationManager, boardController, width, height, swfFile, message);
			}
		},
		
		
		
		new ExperimentEntry("Dummy experiments", "javadummy"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				final int width      = 500;
				final int height     = 350;
				final String archive = "WeblabJavaSample.jar";
				final String code    = "es.deusto.weblab.client.experiment.plugins.es.deusto.weblab.javadummy.JavaDummyApplet";
				final String message = "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Java Applets in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible."; 
				
				return new JavaAppletExperimentBase(configurationManager, boardController, width, height, archive, code, message);
			}
		},
		
		
		
		new ExperimentEntry("PLD experiments", "ud-pld"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabPldExperiment(configurationManager, boardController);
			}
		},
		
		
		
		new ExperimentEntry("FPGA experiments", "ud-fpga"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabFpgaExperiment(configurationManager, boardController);
			}
		},
		
		
		
		new ExperimentEntry("Dummy experiments", "ud-dummy"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabDummyExperiment(configurationManager, boardController);
			}
		},
		
		
		
		new ExperimentEntry("Dummy experiments", "ud-logic"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabLogicExperiment(configurationManager, boardController);
			}
		},
		
		
		
		new ExperimentEntry("PLD experiments", "ud-binary"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabBinaryExperiment(configurationManager, boardController);
			}
		},
		
		
		
		new ExperimentEntry("GPIB experiments", "ud-gpib"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabGpibExperiment(configurationManager, boardController);
			}
		},
		
		
		
		new ExperimentEntry("GPIB experiments", "ud-gpib1"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabGpib1Experiment(configurationManager, boardController);
			}
		},
		
		
		
		new ExperimentEntry("GPIB experiments", "ud-gpib2"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabGpib2Experiment(configurationManager, boardController);
			}
		},
		
		
		
		new ExperimentEntry("PIC experiments", "ud-pic"){
			@Override
			public ExperimentBase create( IConfigurationManager configurationManager, IBoardBaseController boardController) {
				return new WebLabPicExperiment(configurationManager, boardController);
			}
		},
	};
}
