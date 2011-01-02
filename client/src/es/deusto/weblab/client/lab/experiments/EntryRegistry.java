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

import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.binary.WebLabBinaryEntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.dummy.WebLabDummyEntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.fpga.WebLabFpgaEntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib.WebLabGpibEntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib1.WebLabGpib1EntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib2.WebLabGpib2EntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.WebLabLogicEntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pic.WebLabPicEntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pld.WebLabPldEntryLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.visir.VisirLoader;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.vm.VMEntryLoader;
import es.deusto.weblab.client.lab.experiments.util.applets.flash.FlashAppEntryLoader;
import es.deusto.weblab.client.lab.experiments.util.applets.java.JavaAppletEntryLoader;

/**
 * This class acts as a registry of all the available entries for the currently known experiments.
 * In order to add a new experiment, just add another element to the list as the sample one (the one commented)
 */
class EntryRegistry {
	
	static final IExperimentEntryLoader [] entryLoaders = new IExperimentEntryLoader[]{
		new VisirLoader(),
		new FlashAppEntryLoader(),
		new JavaAppletEntryLoader(),
		new WebLabPldEntryLoader(),
		new WebLabFpgaEntryLoader(),
		new WebLabDummyEntryLoader(),
		new VMEntryLoader(),
		new WebLabLogicEntryLoader(),
		new WebLabBinaryEntryLoader(),
		new WebLabGpibEntryLoader(),
		new WebLabGpib1EntryLoader(),
		new WebLabGpib2EntryLoader(),
		new WebLabPicEntryLoader(),
	};
	
	static final List<ExperimentEntry> entries = new Vector<ExperimentEntry>();
}
