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

import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.binary.BinaryCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.dummy.DummyCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.dummybatch.DummyBatchCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib.GpibCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib1.Gpib1CreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.gpib2.Gpib2CreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.labview.LabVIEWCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.LogicCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pic.PicCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pic2.Pic2CreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.robot_movement.RobotMovementCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.robot_proglist.RobotProglistCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.robot_standard.RobotStandardCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.visir.VisirCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.vm.VMCreatorFactory;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.XilinxCreatorFactory;
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
		new XilinxCreatorFactory(),
		new DummyCreatorFactory(),
		new DummyBatchCreatorFactory(),
		new VMCreatorFactory(),
		new LabVIEWCreatorFactory(),
		new LogicCreatorFactory(),
		new BinaryCreatorFactory(),
		new GpibCreatorFactory(),
		new Gpib1CreatorFactory(),
		new Gpib2CreatorFactory(),
		new PicCreatorFactory(),
		new Pic2CreatorFactory(),
		new RobotStandardCreatorFactory(),
		new RobotMovementCreatorFactory(),
		new RobotProglistCreatorFactory()
	};
	
	static final List<ExperimentEntry> entries = new Vector<ExperimentEntry>();
}
