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

import java.util.List;
import java.util.Vector;

import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.binary.WebLabBinaryCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.dummy.WebLabDummyCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.dummybatch.WebLabDummyBatchCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.WebLabXilinxCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib.WebLabGpibCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib1.WebLabGpib1CreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib2.WebLabGpib2CreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.WebLabLogicCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pic.WebLabPicCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pic2.WebLabPic2CreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.visir.VisirCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.vm.VMCreatorFactory;
import es.deusto.weblab.client.lab.experiments.util.applets.flash.FlashAppCreatorFactory;
import es.deusto.weblab.client.lab.experiments.util.applets.java.JavaAppletCreatorFactory;

/**
 * This class acts as a registry of all the available entries for the currently known experiments.
 * In order to add a new experiment, just add another element to the list as the sample one (the one commented)
 */
class EntryRegistry {
	
	static final IExperimentCreatorFactory [] creatorFactories = new IExperimentCreatorFactory[]{
		new VisirCreatorFactory(),
		new FlashAppCreatorFactory(),
		new JavaAppletCreatorFactory(),
		new WebLabXilinxCreatorFactory(),
		new WebLabDummyCreatorFactory(),
		new WebLabDummyBatchCreatorFactory(),
		new VMCreatorFactory(),
		new WebLabLogicCreatorFactory(),
		new WebLabBinaryCreatorFactory(),
		new WebLabGpibCreatorFactory(),
		new WebLabGpib1CreatorFactory(),
		new WebLabGpib2CreatorFactory(),
		new WebLabPicCreatorFactory(),
		new WebLabPic2CreatorFactory()
	};
	
	static final List<ExperimentEntry> entries = new Vector<ExperimentEntry>();
}
