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

package es.deusto.weblab.client.admin.controller;

import java.util.ArrayList;
import java.util.Date;

import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;

public class TemporalFakeData {
	
	ArrayList<ExperimentUse> allExperimentUses;
	ArrayList<Experiment> experiments;
	ArrayList<Group> groups;
	
	public TemporalFakeData() {

		Group telecomunications = new Group("Telecomunications");
		Group mechatronics = new Group("Mechatronics");
		Group course200910 = new Group("Course 2009/10");
		course200910.addChild(telecomunications);
		course200910.addChild(mechatronics);
		
		Role student = new Role("student");
		
		User jaime = new User("jaime.irurzun", "Jaime Irurzun", "jaime.irurzun@opendeusto.es", student);
		jaime.addToGroup(telecomunications);
		
		User pablo = new User("pablo.orduna", "Pablo Orduña", "pablo.ordunya@opendeusto.es", student);
		pablo.addToGroup(telecomunications);
		
		User luis = new User("luis.rodriguez", "Luis Rodríguez", "luis.rodriguez@opendeusto.es", student);
		luis.addToGroup(mechatronics);
		
		Category fpgaExp = new Category("FPGA experiments");
		Category pldExp = new Category("PLD experiments");
		
		Experiment fpga = new Experiment("ud-fpga", fpgaExp, new Date(), new Date());
		Experiment pld = new Experiment("ud-pld", pldExp, new Date(), new Date());
		Experiment binary = new Experiment("ud-binary", pldExp, new Date(), new Date());
		
		this.experiments = new ArrayList<Experiment>();
		this.experiments.add(fpga);
		this.experiments.add(pld);
		this.experiments.add(binary);	
		
		this.groups = new ArrayList<Group>();
		this.groups.add(course200910);
		
		this.allExperimentUses = new ArrayList<ExperimentUse>();		
		this.allExperimentUses.add(new ExperimentUse(jaime, fpga,  new Date(2010-1900, 04, 17, 15, 00, 00), new Date(2010-1900, 04, 17, 15, 00, 30)));
		this.allExperimentUses.add(new ExperimentUse(pablo, pld,   new Date(2010-1900, 04, 18, 15, 00, 00), new Date(2010-1900, 04, 18, 15, 00, 15)));
		this.allExperimentUses.add(new ExperimentUse(luis, binary, new Date(2010-1900, 04, 20, 15, 00, 00), new Date(2010-1900, 04, 20, 15, 00, 25)));		
	}
}
