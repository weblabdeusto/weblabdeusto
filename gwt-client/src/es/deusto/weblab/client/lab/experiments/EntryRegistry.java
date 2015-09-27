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

import es.deusto.weblab.client.experiments.aquarium.AquariumCreatorFactory;
import es.deusto.weblab.client.experiments.binary.BinaryCreatorFactory;
import es.deusto.weblab.client.experiments.blank.BlankCreatorFactory;
import es.deusto.weblab.client.experiments.blank.BlankLimitedMobileCreatorFactory;
import es.deusto.weblab.client.experiments.blank.BlankNoMobileCreatorFactory;
import es.deusto.weblab.client.experiments.dummy.DummyCreatorFactory;
import es.deusto.weblab.client.experiments.dummybatch.DummyBatchCreatorFactory;
import es.deusto.weblab.client.experiments.gpib.GpibCreatorFactory;
import es.deusto.weblab.client.experiments.gpib1.Gpib1CreatorFactory;
import es.deusto.weblab.client.experiments.gpib2.Gpib2CreatorFactory;
import es.deusto.weblab.client.experiments.ilab_batch.ILabBatchCreatorFactory;
import es.deusto.weblab.client.experiments.incubator.IncubatorCreatorFactory;
import es.deusto.weblab.client.experiments.labview.LabVIEWCreatorFactory;
import es.deusto.weblab.client.experiments.logic.LogicCreatorFactory;
import es.deusto.weblab.client.experiments.pic18.Pic18CreatorFactory;
import es.deusto.weblab.client.experiments.robot_maze.RobotMazeCreatorFactory;
import es.deusto.weblab.client.experiments.robot_movement.RobotMovementCreatorFactory;
import es.deusto.weblab.client.experiments.robot_proglist.RobotProglistCreatorFactory;
import es.deusto.weblab.client.experiments.robot_standard.RobotStandardCreatorFactory;
import es.deusto.weblab.client.experiments.robotarm.RobotArmCreatorFactory;
import es.deusto.weblab.client.experiments.submarine.SubmarineCreatorFactory;
import es.deusto.weblab.client.experiments.unr_physics.UnrCreatorFactory;
import es.deusto.weblab.client.experiments.visir.VisirCreatorFactory;
import es.deusto.weblab.client.experiments.vm.VMCreatorFactory;
import es.deusto.weblab.client.experiments.xilinx.XilinxCreatorFactory;
import es.deusto.weblab.client.lab.experiments.util.applets.flash.FlashAppCreatorFactory;
import es.deusto.weblab.client.lab.experiments.util.applets.java.JavaAppletCreatorFactory;
import es.deusto.weblab.client.lab.experiments.util.applets.js.JSAppCreatorFactory;

/**
 * This class acts as a registry of all the available entries for the currently known experiments.
 * In order to add a new experiment, just add another element to the list as the sample one (the one commented)
 */
public class EntryRegistry {
	
	public static final IExperimentCreatorFactory [] creatorFactories = new IExperimentCreatorFactory[]{
		new BlankCreatorFactory(),
		new BlankLimitedMobileCreatorFactory(),
		new BlankNoMobileCreatorFactory(),
		new VisirCreatorFactory(),
		new FlashAppCreatorFactory(),
		new JavaAppletCreatorFactory(),
		new JSAppCreatorFactory(),
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
		new Pic18CreatorFactory(),
		new RobotStandardCreatorFactory(),
		new RobotMovementCreatorFactory(),
		new RobotProglistCreatorFactory(),
		new RobotArmCreatorFactory(),
		new SubmarineCreatorFactory(),
		new ILabBatchCreatorFactory(),
		new UnrCreatorFactory(),
		new IncubatorCreatorFactory(),
		new AquariumCreatorFactory(),
		new RobotMazeCreatorFactory(),
	};
}
