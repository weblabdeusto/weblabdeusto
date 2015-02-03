#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#

import os
import sys
import datetime
import traceback
import random
import hashlib

import six
from sqlalchemy.orm import sessionmaker

from weblab.db.upgrade import DbRegularUpgrader, DbSchedulingUpgrader
import weblab.db.model as Model
import weblab.permissions as permissions



def _add_params(session, experiment):
    client_config = CONFIG_JS[experiment.client]

    experiment_config = {}
    for experiment_client in client_config:
        if (experiment_client['experiment.name'] == experiment.name and 
                experiment_client['experiment.category'] == experiment.category.name ):
                experiment_config = experiment_client
                break

    for key, value in experiment_config.iteritems():
        if key in ("experiment.name", "experiment.category"):
            continue

        if isinstance(value, bool):
            key_type = 'bool'
        elif isinstance(value, int):
            key_type = 'integer'
        elif isinstance(value, float):
            key_type = 'floating'
        else:
            key_type = 'string'

        param = Model.DbExperimentClientParameter(experiment, key, key_type, unicode(value))
        session.add(param)

    session.commit()

# 
# Original JavaScript configuration
# 
CONFIG_JS = { 
					"flash" : [
					           {
					        	   "experiment.name"     : "flashdummy",
					        	   "experiment.category" : "Dummy experiments",
					        	   "experiment.picture"	 : "/img/experiments/flash.jpg",
					        	   "page.footer"	 : "",
					        	   "flash.timeout"       : 20,
					        	   "width"               : 500,
					        	   "height"              : 350,
					        	   "swf.file"            : "WeblabFlashSample.swf",
					        	   "message"             : "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Adobe Flash in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible.",
	                       		   "experiment.info.link" : "http://code.google.com/p/weblabdeusto/wiki/Latest_Exp_Flash_Dummy",
	                        	   "experiment.info.description" : "description"
	                       		}
	                       ],
	                "java" : [
	                          {
	                        	  "experiment.name"      : "javadummy",
	                        	  "experiment.category"  : "Dummy experiments",
	                        	  "experiment.picture"   : "/img/experiments/java.jpg",
	                        	  "width"                : 500,
	                        	  "height"               : 350,
	                        	  "jar.file"             : "WeblabJavaSample.jar",
	                        	  "code"                 : "es.deusto.weblab.client.experiment.plugins.es.deusto.weblab.javadummy.JavaDummyApplet",
	                        	  "message"             : "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Java Applets in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible.",
	                          	  "experiment.info.link" : "http://code.google.com/p/weblabdeusto/wiki/Latest_Exp_Java_Dummy",
	                        	  "experiment.info.description" : "description"
	                          }
	                       ],
	                "js"	: [
	                    	   {
	                    		   "experiment.name"		: "jsdummy",
	                    		   "experiment.category"	: "Dummy experiments",
	                    		   "experiment.picture"		: "/img/experiments/java.jpg",
	                    		   "width"					: 500,
	                    		   "height"					: 350,
	                    		   "provide.file.upload"	: True,
	                    		   "html.file"				: "jstest.html"
	                    	   },
	                    	   {
	                    		   "experiment.name"		: "aquariumjs",
	                    		   "experiment.category"	: "Aquatic experiments",
	                    		   "experiment.picture"		: "/img/experiments/aquarium.png",
	                    		   "width"					: 1024,
	                    		   "height"					: 1000,
	                    		   "html.file"				: "jslabs/aquarium/aquarium.html",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
								   "experiment.info.description" : "description"
	                    	   },	
 				   {
					   "experiment.name"		: "archimedes",
					   "experiment.category"	: "Aquatic experiments",
					   "experiment.picture"         : "/img/experiments/aquarium.png",
                                           "cssWidth"                   : "1024",
                                           "cssHeight"                  : "1000",
                                           "html.file"                  : "jslabs/archimedes/archimedes.html"
				   },
								{
									"experiment.name"		: "elevator",
									"experiment.category"	: "FPGA experiments",
									"experiment.picture"	: "/img/experiments/elevator.png",
									"cssWidth"				: "1024",
									"cssHeight"				: "1000",
									"html.file"				: "jslabs/elevator/dist/index.html",
									"experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#elevator",
									"experiment.info.description" : "Experiment with an elevator"
								},
        	                   {
	                    		   "experiment.name"		: "submarinejs",
	                    		   "experiment.category"	: "Aquatic experiments",
	                    		   "experiment.picture"		: "/img/experiments/submarine.png",
	                    		   "cssWidth"					: "1024",
	                    		   "cssHeight"					: "1000",
	                    		   "html.file"				: "jslabs/submarine/submarine.html",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
								   "experiment.info.description" : "description"
	                    	   },
	                    	   {
	                    		   "experiment.name"		: "jsfpga",
	                    		   "experiment.category"	: "FPGA experiments",
	                    		   "experiment.picture"		: "/img/experiments/xilinx.jpg",
	                    		   "width"					: "800",
	                    		   "height"					: "600",
	                    		   "provide.file.upload"	: True,
	                    		   "html.file"				: "jsxilinx/watertank/watertank.html"
	                    	   },
							   {
								   "experiment.name"		: "visir-html5",
								   "experiment.category"	: "Visir experiments",
								   "experiment.picture"		: "/img/experiments/visir.jpg",
								   "cssWidth"				: "805",
								   "cssHeight"				: "520",
								   "provide.file.upload"	: False,
								   "html.file"				: "visir-html5/visir.html"
							   }
	                       ],
	                "vm"    : [
	                           {
	                        	   "experiment.picture"	 : "/img/experiments/virtualbox.jpg",
	                        	   "experiment.name"     : "vm",
	                        	   "experiment.category" : "Dummy experiments"
	                           },
	                           {
	                        	   "experiment.picture"	 : "/img/experiments/virtualbox.jpg",
	                        	   "experiment.name"     : "vm",
	                        	   "experiment.category" : "VM experiments"
	                           },
	                           {
	                        	   "experiment.picture"	 : "/img/experiments/virtualbox.jpg",
	                        	   "experiment.name"     : "ud-linux-vm",
	                        	   "experiment.category" : "VM experiments",
	                        	   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#virtual-machine-lab",
	                        	   "experiment.info.description" : "description"
	                           },
	                           {
	                        	   "experiment.picture"	 : "/img/experiments/virtualbox.jpg",
	                        	   "experiment.name"     : "ud-win-vm",
	                        	   "experiment.category" : "VM experiments"
	                           },
	                           {
	                        	   "experiment.picture"	 : "/img/experiments/virtualbox.jpg",
	                        	   "experiment.name"	 : "vm-win",
	                               "experiment.category" : "Dummy experiments"
	                           }
	                       ],
	                "labview": [
	                            {
		                        	"experiment.picture"  : "/img/experiments/labview.jpg",
	                            	"experiment.name"     : "testone",
	                            	"experiment.category" : "LabVIEW experiments"
	                            },
	                            {
		                        	"experiment.picture"  : "/img/experiments/labview.jpg",
	                            	"experiment.name"     : "blink-led",
	                            	"experiment.category" : "LabVIEW experiments"
	                            },
	                            {
		                        	"experiment.picture"  : "/img/experiments/labview.jpg",
	                            	"experiment.name"     : "prototyping-board-01",
	                            	"experiment.category" : "LabVIEW experiments"
	                            },
	                            {
		                        	"experiment.picture"  : "/img/experiments/labview.jpg",
	                            	"experiment.name"     : "fpga-board-config",
	                            	"experiment.category" : "LabVIEW experiments"
	                            },
	                            {
		                        	"experiment.picture"  : "/img/experiments/labview.jpg",
	                            	"experiment.name"     : "fpga-board-experiment",
	                            	"experiment.category" : "LabVIEW experiments",
	                            	"send.file"           : True
	                            },
	                            {
		                        	"experiment.picture"  : "/img/experiments/labview.jpg",
	                            	"experiment.name"     : "fpga-board-bit",
	                            	"experiment.category" : "LabVIEW experiments"
	                            }
	                       ],
	                "xilinx" : [
							  {
								   "experiment.name"     : "ud-test-pld1",
								   "experiment.category" : "PLD experiments",
								   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : True
							  },
							  {
								   "experiment.name"     : "ud-test-pld2",
								   "experiment.category" : "PLD experiments",
								   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : True
							  },
							  {
								   "experiment.name"     : "ud-demo-pld",
								   "experiment.category" : "PLD experiments",
								   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : True,
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#cpld",
								   "experiment.info.description" : "description"
							  },
							  {
								   "experiment.name"     : "ud-demo-fpga",
								   "experiment.category" : "FPGA experiments",
								   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : True,
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#fpga",
								   "experiment.info.description" : "description"
							  },
							  {
								   "experiment.name"     : "ud-demo-xilinx",
								   "experiment.category" : "Xilinx experiments",
								   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : True,
								   "is.multiresource.demo" : True,
								   "experiment.info.link" : "http://code.google.com/p/weblabdeusto/wiki/Latest_Exp_Demo_Xilinx",
								   "experiment.info.description" : "description"
							  },
							  {
								   "experiment.name"     : "ud-fpga",
								   "experiment.category" : "FPGA experiments",
								   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#fpga",
								   "experiment.info.description" : "description"
							  },
							  {
								  "experiment.name"      : "ud-pld",
								  "experiment.category"  : "PLD experiments",
								  "experiment.picture"   : "/img/experiments/xilinx.jpg"
							  },
							  {
								  "experiment.name"      : "ud-pld-1",
								  "experiment.category"  : "PLD experiments",
								  "experiment.picture"   : "/img/experiments/xilinx.jpg"
							  },
							  {
								  "experiment.name"      : "ud-pld-2",
								  "experiment.category"  : "PLD experiments",
								  "experiment.picture"   : "/img/experiments/xilinx.jpg"
							  }
						   ],
					"dummy" : [
							   {
								   "experiment.name"     : "ud-dummy",
								   "experiment.category" : "Dummy experiments"
							   },
							   {
								   "experiment.name"     : "dummy",
								   "experiment.category" : "Dummy experiments"
							   },
							   {
								   "experiment.name"     : "dummy1",
								   "experiment.category" : "Dummy experiments"
							   },
							   {
								   "experiment.name"     : "dummy2",
								   "experiment.category" : "Dummy experiments"
							   },
							   {
								   "experiment.name"     : "dummy3",
								   "experiment.category" : "Dummy experiments"
							   },
							   {
								   "experiment.name"     : "dummy4",
								   "experiment.category" : "Dummy experiments"
							   }
						   ],
					"dummybatch" : [
								   {
									   "experiment.name"     : "ud-dummy-batch",
									   "experiment.category" : "Dummy experiments"
								   }
						],
					"robot-standard" : [
								{
								   "experiment.name" : "robot-standard",
								   "experiment.category" : "Robot experiments",
								   "experiment.picture"	 : "/img/experiments/robot.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#robot",
								   "experiment.info.description" : "description"
								}
							],
					"robot-movement" : [
								{
									"experiment.name" : "robot-movement",
									"experiment.picture" : "/img/experiments/robot.jpg",
									"experiment.category" : "Robot experiments",
									"experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#robot",
									"experiment.info.description" : "description"
								}
							],
					"robot-maze" : [
										{
											"experiment.name" : "robot-maze",
											"experiment.picture" : "/img/experiments/robot.jpg",
											"experiment.category" : "Robot experiments"
										}
									],
					"submarine" : [
										{
											"experiment.name" : "submarine",
											"experiment.picture" : "/img/experiments/submarine.png",
											"experiment.category" : "Submarine experiments",
											"experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
											"experiment.info.description" : "description"
										},
										{
											"experiment.name" : "submarine",
											"experiment.picture" : "/img/experiments/submarine.png",
											"experiment.category" : "Aquatic experiments",
											"experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
											"experiment.info.description" : "description"
										}
									],
					"aquarium" : [
									{
										"experiment.name" : "aquarium",
										"experiment.picture" : "/img/experiments/aquarium.png",
										"experiment.category" : "Aquatic experiments",
										"experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#aquarium",
										"experiment.info.description" : "description"
									}
							 ],
					"robot-proglist" : [
								{
									"experiment.name" : "robot-proglist",
									"experiment.picture"  : "/img/experiments/robot.jpg",
									"experiment.category" : "Robot experiments",
									"experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#robot",
									"experiment.info.description" : "description"
								}
							],
					"robotarm" : [
										{
											"experiment.name" : "robotarm",
											"experiment.picture"  : "/img/experiments/robot.jpg",
											"experiment.category" : "Robot experiments",
											"experiment.info.description" : "description"
										}
									],
					"blank" : [
							   {
								   "experiment.name"     : "external-robot-movement",
								   "experiment.category" : "Robot experiments",
								   "experiment.picture"  : "/img/experiments/robot.jpg",
								   "html"                : "This is an experiment which we know that it is only in external systems. Therefore, unless we want to use the initialization API, we don't need to have the client installed in the consumer system. We can just use a blank client and whenever the experiment is reserved, we'll use the remote client."
							   }
							],
					"visir" : [
							   {
								   "experiment.name"      : "Fisica-1",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "Fisica-2",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "Fisica-3",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "Fisica-1-PXI",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "Fisica-2-PXI",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "Fisica-3-PXI",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "visirtest",
								   "experiment.category"  : "Dummy experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "visir-lesson2",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "lxi_visir",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "visir",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "visir-student",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "visir-uned",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "visir-fed-balance",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"      : "visir-fed-balance-multiple",
								   "experiment.category"  : "Visir experiments",
								   "experiment.picture"   : "/img/experiments/visir.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#visir",
								   "experiment.info.description" : "description"
							   }
						   ],
					"logic" : [
							   {
								   "experiment.name"     : "ud-logic",
								   "experiment.category" : "PIC experiments",
								   "experiment.picture"   : "/img/experiments/logic.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#ud-logic",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"     : "ud-logic",
								   "experiment.category" : "Dummy experiments",
								   "experiment.picture"   : "/img/experiments/logic.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#ud-logic",
								   "experiment.info.description" : "description"
							   },
							   {
								   "experiment.name"     : "logic",
								   "experiment.category" : "Games",
								   "experiment.picture"   : "/img/experiments/logic.jpg",
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#ud-logic",
								   "experiment.info.description" : "description"
							   }
						   ],
					"binary" : [
								{
								   "experiment.name"     : "ud-binary",
								   "experiment.category" : "PLD experiments",
								   "experiment.picture"   : "/img/experiments/binary.jpg"
								},
								{
								   "experiment.name"     : "binary",
								   "experiment.category" : "Games",
								   "experiment.picture"   : "/img/experiments/binary.jpg"
								}
						   ],
					"gpib"   : [
								{
								   "experiment.name"     : "ud-gpib",
								   "experiment.category" : "GPIB experiments"
								}
						   ],
					"gpib1" : [
								{
								   "experiment.name"     : "ud-gpib1",
								   "experiment.category" : "GPIB experiments"
								}
							],
					"gpib2" : [
							   {
								   "experiment.name"     : "ud-gpib2",
								   "experiment.category" : "GPIB experiments"
							   }
							],
					"pic18"	: [
								{
								   "experiment.name"	 : "ud-pic18",
								   "experiment.category" : "PIC experiments",
								   "experiment.picture"  : "/img/experiments/microchip.jpg"
								},
								{
								   "experiment.name"	 : "ud-test-pic18-1",
								   "experiment.category" : "PIC experiments",
								   "experiment.picture"  : "/img/experiments/microchip.jpg",
								   "is.demo"             : True
								},
								{
								   "experiment.name"	 : "ud-test-pic18-2",
								   "experiment.category" : "PIC experiments",
								   "experiment.picture"  : "/img/experiments/microchip.jpg",
								   "is.demo"             : True
								},
								{
								   "experiment.name"	 : "ud-test-pic18-3",
								   "experiment.category" : "PIC experiments",
								   "experiment.picture"  : "/img/experiments/microchip.jpg",
								   "is.demo"             : True
	                			}
	                		],
	                "unr-physics" : [
	                            {
		                			"experiment.name"	 : "unr-physics",
		                			"experiment.category" : "Physics experiments",
		                			"experiment.picture"  : "/img/experiments/unr.jpg"
	                            }
	                        ],
                    "ilab-batch" : [
                                {
                                	"experiment.reserve.button.shown" : False,
	                        	    "experiment.picture"              : "/img/experiments/MIT.jpg",
                                    "experiment.name"                 : "microelectronics",
                                    "experiment.category"             : "iLab experiments",
                                    "archive"                         : "http://weblab2.mit.edu/client/v7.0b5/signed_Weblab-client.jar",
                                    "code"                            : "weblab.client.graphicalUI.GraphicalApplet",
                                    "lab_server_id"                   : "microelectronics",
                                    "service_broker"                  : "http://www.weblab.deusto.es/weblab/web/ilab/"
                                }
                            ],
                     "control-app" : [
                                {
	                        	    "experiment.picture"              : "/img/experiments/bulb.png",
                                    "experiment.name"                 : "control-app",
                                    "experiment.category"             : "Control experiments"
                                }
                            ],
                    "redirect" : [
                                     {
                                         "experiment.name"                 : "http",
                                         "experiment.category"             : "HTTP experiments"
                                     }
                                 ],
                     "incubator" : [
                                {
	                        	    "experiment.picture"              : "/img/experiments/incubator.jpg",
                                	"experiment.name"                 : "incubator",
                                	"experiment.category"             : "Farm experiments",
                                    "experiment.reserve.button.shown" : False,
                                	"html"                            : "This lab is disabled at this moment. Go to <a target=\"_blank\" href=\"http://130.206.138.18/lastexp/\">the original site</a> to see the archived results."
                                }
                            ]
		}

def insert_required_initial_data(engine):
    session = sessionmaker(bind=engine)
    session = session()

    # Roles
    federated = Model.DbRole("federated")
    session.add(federated)

    administrator = Model.DbRole("administrator")
    session.add(administrator)

    instructor = Model.DbRole("instructor")
    session.add(instructor)

    student = Model.DbRole("student")
    session.add(student)

    db = Model.DbAuthType("DB")
    session.add(db)
    ldap = Model.DbAuthType("LDAP")
    session.add(ldap)
    iptrusted = Model.DbAuthType("TRUSTED-IP-ADDRESSES")
    session.add(iptrusted)
    facebook = Model.DbAuthType("FACEBOOK")
    session.add(facebook)
    openid = Model.DbAuthType("OPENID")
    session.add(openid)

    weblab_db = Model.DbAuth(db, "WebLab DB", 1)
    session.add(weblab_db)
    session.commit()

    weblab_openid = Model.DbAuth(openid, "OPENID", 7)
    session.add(weblab_openid)
    session.commit()

    federated_access_forward = Model.DbRolePermission(
        federated,
        permissions.ACCESS_FORWARD,
        "federated_role::access_forward",
        datetime.datetime.utcnow(),
        "Access to forward external accesses to all users with role 'federated'"
    )
    session.add(federated_access_forward)

    session.commit()

    administrator_admin_panel_access = Model.DbRolePermission(
        administrator,
        permissions.ADMIN_PANEL_ACCESS,
        "administrator_role::admin_panel_access",
        datetime.datetime.utcnow(),
        "Access to the admin panel for administrator role with full_privileges"
    )
    session.add(administrator_admin_panel_access)
    administrator_admin_panel_access_p1 = Model.DbRolePermissionParameter(administrator_admin_panel_access, permissions.FULL_PRIVILEGES, True)
    session.add(administrator_admin_panel_access_p1)

    upgrader = DbRegularUpgrader(str(engine.url))
    session.execute(
        Model.Base.metadata.tables['alembic_version'].insert().values(version_num = upgrader.head)
    )
    session.commit()

def insert_required_initial_coord_data(engine):
    session = sessionmaker(bind=engine)
    session = session()

    upgrader = DbSchedulingUpgrader(str(engine.url))
    session.execute(
        Model.Base.metadata.tables['alembic_version'].insert().values(version_num = upgrader.head)
    )
    session.commit()

#####################################################################
#
# Populating tests database
#

def _create_user(session, login, role, full_name, email, password = 'password', invalid_password = None, other_auths = None):
    user = Model.DbUser(login, full_name, email, None, role)
    session.add(user)
    weblab_db = session.query(Model.DbAuth).filter_by(name = "WebLab DB").one()
    if not invalid_password:
        session.add(Model.DbUserAuth(user, weblab_db, _password2sha(password, 'aaaa')))
    else:
        session.add(Model.DbUserAuth(user, weblab_db, invalid_password))
    for (auth_type, value) in (other_auths or ()):
        session.add(Model.DbUserAuth(user, auth_type, value))
    return user

def _create_users(session, users_data):
    all_users = {}
    for login, data in six.iteritems(users_data):
        all_users[login] = _create_user(session, login, *data)
    return all_users

def _create_group(session, users_data, group_name, logins, parent):
    group = Model.DbGroup(group_name, parent)
    for login in logins:
        group.users.append(users_data[login])
    session.add(group)
    return group

def _create_groups(session, users_data, groups_data):
    all_groups = {}
    for (group_name, parent_name), logins in six.iteritems(groups_data):
        if parent_name is None:
            all_groups[group_name] = _create_group(session, users_data, group_name, logins, None)

    for (group_name, parent_name), logins in six.iteritems(groups_data):
        if parent_name is not None:
            parent = all_groups[parent_name]
            all_groups[group_name] = _create_group(session, users_data, group_name, logins, parent)

    return all_groups

def _create_experiment(session, exp_name, cat_name, client):
    start_date = datetime.datetime.utcnow()
    end_date = start_date.replace(year=start_date.year+12) # So leap years are not a problem

    category = session.query(Model.DbExperimentCategory).filter_by(name = cat_name).first()
    if category is None:
        category = Model.DbExperimentCategory(cat_name)
        session.add(category)

    experiment = Model.DbExperiment(exp_name, category, start_date, end_date, client)
    session.add(experiment)
    _add_params(session, experiment)
    return experiment

def _create_experiments(session, experiment_data):
    all_experiments = {}
    for (exp_name, cat_name), client in six.iteritems(experiment_data):
        all_experiments[exp_name, cat_name] = _create_experiment(session, exp_name, cat_name, client)
    return all_experiments

def _grant_permission_to_group(session, groups_data, experiments_data, group_name, exp_name, cat_name, time):
    if (exp_name, cat_name) not in experiments_data:
        raise Exception("Error: %s@%s not previously registered" % (exp_name, cat_name))

    db_group = groups_data[group_name]

    gp_allowed = Model.DbGroupPermission(
        db_group,
        permissions.EXPERIMENT_ALLOWED,
        "%s::%s" % (group_name, exp_name),
        datetime.datetime.utcnow(),
        "Permission for group %s to use %s" % (group_name, exp_name)
    )
    session.add(gp_allowed)
    gp_allowed_p1 = Model.DbGroupPermissionParameter(gp_allowed, permissions.EXPERIMENT_PERMANENT_ID, exp_name)
    session.add(gp_allowed_p1)
    gp_allowed_p2 = Model.DbGroupPermissionParameter(gp_allowed, permissions.EXPERIMENT_CATEGORY_ID, cat_name)
    session.add(gp_allowed_p2)
    gp_allowed_p3 = Model.DbGroupPermissionParameter(gp_allowed, permissions.TIME_ALLOWED, six.text_type(time))
    session.add(gp_allowed_p3)

def _grant_permissions_to_groups(session, groups_data, experiments_data, permissions_data):
    for args in permissions_data:
        _grant_permission_to_group(session, groups_data, experiments_data, *args)

def _grant_permission_to_user(session, users_data, experiments_data, login, exp_name, cat_name, time):
    if (exp_name, cat_name) not in experiments_data:
        raise Exception("Error: %s@%s not previously registered" % (exp_name, cat_name))

    db_user = users_data[login]

    up_allowed = Model.DbUserPermission(
        db_user,
        permissions.EXPERIMENT_ALLOWED,
        "%s::%s" % (login, exp_name),
        datetime.datetime.utcnow(),
        "Permission for user %s to use %s" % (login, exp_name)
    )
    session.add(up_allowed)
    up_allowed_p1 = Model.DbUserPermissionParameter(up_allowed, permissions.EXPERIMENT_PERMANENT_ID, exp_name)
    session.add(up_allowed_p1)
    up_allowed_p2 = Model.DbUserPermissionParameter(up_allowed, permissions.EXPERIMENT_CATEGORY_ID, cat_name)
    session.add(up_allowed_p2)
    up_allowed_p3 = Model.DbUserPermissionParameter(up_allowed, permissions.TIME_ALLOWED, six.text_type(time))
    session.add(up_allowed_p3)        

def _grant_permissions_to_users(session, users_data, experiments_data, permissions_data):
    for args in permissions_data:
        _grant_permission_to_user(session, users_data, experiments_data, *args)

def populate_weblab_tests(engine, tests):
    Session = sessionmaker(bind=engine)
    session = Session()

    ldap = session.query(Model.DbAuthType).filter_by(name="LDAP").one()
    iptrusted = session.query(Model.DbAuthType).filter_by(name="TRUSTED-IP-ADDRESSES").one()
    facebook = session.query(Model.DbAuthType).filter_by(name="FACEBOOK").one()

    # Auths
    weblab_db = session.query(Model.DbAuth).filter_by(name = "WebLab DB").one()

    cdk_ldap = Model.DbAuth(ldap, "Configuration of CDK at Deusto", 2, "ldap_uri=ldaps://castor.cdk.deusto.es;domain=cdk.deusto.es;base=dc=cdk,dc=deusto,dc=es")
    session.add(cdk_ldap)

    deusto_ldap = Model.DbAuth(ldap, "Configuration of DEUSTO at Deusto", 3, "ldap_uri=ldaps://altair.cdk.deusto.es;domain=deusto.es;base=dc=deusto,dc=es")
    session.add(deusto_ldap)

    localhost_ip = Model.DbAuth(iptrusted, "trusting in localhost", 4, "127.0.0.1")
    session.add(localhost_ip)

    auth_facebook = Model.DbAuth(facebook, "Facebook", 5)
    session.add(auth_facebook)

    administrator = session.query(Model.DbRole).filter_by(name='administrator').one()
    instructor    = session.query(Model.DbRole).filter_by(name='instructor').one()
    student       = session.query(Model.DbRole).filter_by(name='student').one()
    federated     = session.query(Model.DbRole).filter_by(name='federated').one()

    # Users
    all_users = _create_users(session, {
        'admin1'       : (administrator, "Name of administrator 1",       "weblab@deusto.es"),
        'admin2'       : (administrator, "Name of administrator 2",       "weblab@deusto.es"),
        'admin3'       : (administrator, "Name of administrator 3",       "weblab@deusto.es"),
        'archimedes'   : (student,       "Usuario de prueba para Splash", "weblab@deusto.es",  "archimedes"),
        'any'          : (student,       "Name of any",                   "weblab@deusto.es",  "password", None, [(auth_facebook, "1168497114")]),
        'prof1'        : (instructor,    "Name of instructor 1",          "weblab@deusto.es"),
        'prof2'        : (instructor,    "Name of instructor 2",          "weblab@deusto.es"),
        'prof3'        : (instructor,    "Name of instructor 3",          "weblab@deusto.es"),
        'student1'     : (student,       "Name of student 1",             "weblab@deusto.es"),
        'student2'     : (student,       "Name of student 2",             "weblab@deusto.es"),
        'student3'     : (student,       "Name of student 3",             "weblab@deusto.es"),
        'student4'     : (student,       "Name of student 4",             "weblab@deusto.es"),
        'student5'     : (student,       "Name of student 5",             "weblab@deusto.es"),
        'student6'     : (student,       "Name of student 6",             "weblab@deusto.es"),
        'student7'     : (student,       "Name of student 7",             "weblab@deusto.es", None, "aaaa{thishashdoesnotexist}a776159c8c7ff8b73e43aa54d081979e72511474"),
        'student8'     : (student,       "Name of student 8",             "weblab@deusto.es", None, "this.format.is.not.valid.for.the.password"),
        'studentILAB'  : (student,       "Name of student ILAB",          "weblab@deusto.es"),
        'studentLDAP1' : (student,       "Name of student LDAP1",         "weblab@deusto.es", "password", None, [(cdk_ldap, None)]),
        'studentLDAP2' : (student,       "Name of student LDAP2",         "weblab@deusto.es", "password", None, [(cdk_ldap, None)]),
        'studentLDAP3' : (student,       "Name of student LDAP3",         "weblab@deusto.es", "password", None, [(deusto_ldap, None)]),
        'fedstudent1'  : (federated,     "Name of federated user 1",      "weblab@deusto.es"),
        'fedstudent2'  : (federated,     "Name of federated user 2",      "weblab@deusto.es"),
        'fedstudent3'  : (federated,     "Name of federated user 3",      "weblab@deusto.es"),
        'fedstudent4'  : (federated,     "Name of federated user 4",      "weblab@deusto.es"),
        'consumer1'    : (federated,     "Consumer University 1",         "weblab@deusto.es"),
        'provider1'    : (federated,     "Provider University 1",         "weblab@deusto.es"),
        'provider2'    : (federated,     "Provider University 2",         "weblab@deusto.es"),
    })

    all_groups = _create_groups(session, all_users, {
        ("Federated users",   None)              : ('fedstudent1', 'fedstudent2', 'fedstudent3', 'fedstudent4'),
        ("Course 2008/09",    None)              : ('student1', 'student2'),
        ("Mechatronics",      "Course 2008/09")  : ('student3', 'student4'),
        ("Telecomunications", "Course 2008/09")  : ('student5', 'student6'),
        ("Course 2009/10",    None)              : ('student1', 'student2', 'student3', 'student4', 'student5', 'student6'),
    })

    # Experiments
    all_experiments = _create_experiments(session, {
        ('ud-dummy',                'Dummy experiments')     : 'dummy',
        ('ud-dummy-batch',          'Dummy experiments')     : 'dummybatch',
        ('archimedes',              'Aquatic experiments')   : 'js',
        ('elevator',                'FPGA experiments')      : 'js',
        ('dummy1',                  'Dummy experiments')     : 'dummy',
        ('dummy2',                  'Dummy experiments')     : 'dummy',
        ('dummy4',                  'Dummy experiments')     : 'dummy',
        ('flashdummy',              'Dummy experiments')     : 'flash',
        ('javadummy',               'Dummy experiments')     : 'java',
        ('jsdummy',                 'Dummy experiments')     : 'js',
        ('jsfpga',                  'FPGA experiments')      : 'js',
        ('visir-html5',             'Visir experiments')     : 'js',
        ('ud-logic',                'PIC experiments')       : 'logic',
        ('binary',                  'Games')                 : 'binary',
        ('unr-physics',             'Physics experiments')   : 'unr-physics',
        ('control-app',             'Control experiments')   : 'control-app',
        ('incubator',               'Farm experiments')      : 'incubator',
        ('ud-pld',                  'PLD experiments')       : 'xilinx',
        ('ud-pld2',                 'PLD experiments')       : 'xilinx',
        ('ud-demo-pld',             'PLD experiments')       : 'xilinx',
        ('ud-fpga',                 'FPGA experiments')      : 'xilinx',
        ('ud-demo-fpga',            'FPGA experiments')      : 'xilinx',
        ('ud-demo-xilinx',          'Xilinx experiments')    : 'xilinx',
        ('ud-gpib',                 'GPIB experiments')      : 'gpib',
        ('visirtest',               'Dummy experiments')     : 'visir',
        ('visir',                   'Visir experiments')     : 'visir',
        ('vm',                      'Dummy experiments')     : 'vm',
        ('vm-win',                  'Dummy experiments')     : 'vm',
        ('blink-led',               'LabVIEW experiments')   : 'labview',
        ('submarine',               'Submarine experiments') : 'submarine',
        ('http',                    'HTTP experiments')      : 'redirect',
        ('aquarium',                'Aquatic experiments')   : 'aquarium',
        ('aquariumjs',              'Aquatic experiments')   : 'js',
        ('submarinejs',             'Aquatic experiments')   : 'js',
        ('robotarm',                'Robot experiments')     : 'robotarm',
        ('robot-maze',              'Robot experiments')     : 'robot-maze',
        ('robot-standard',          'Robot experiments')     : 'robot-standard',
        ('robot-movement',          'Robot experiments')     : 'robot-movement',
        ('robot-proglist',          'Robot experiments')     : 'robot-proglist',
        ('external-robot-movement', 'Robot experiments')     : 'blank',
        ('microelectronics',        'iLab experiments')      : 'ilab-batch',
        ('ud-pic18',                'PIC experiments')       : 'pic18',
    })

    if tests != '2':
        all_experiments['dummy3', 'Dummy experiments'] = _create_experiment(session, 'dummy3', 'Dummy experiments', 'dummy')
    else:
        all_experiments['dummy3_with_other_name', 'Dummy experiments'] = _create_experiment(session, 'dummy3_with_other_name', 'Dummy experiments', 'dummy')


    _grant_permissions_to_groups(session, all_groups, all_experiments, [
        ("Course 2008/09",  "ud-fpga",     "FPGA experiments",  300),
        ("Federated users", "dummy1",      "Dummy experiments", 300),
        ("Federated users", "dummy2",      "Dummy experiments", 300),
        ("Federated users", "dummy4",      "Dummy experiments", 300),
        ("Course 2008/09",  "flashdummy",  "Dummy experiments",  30),
        ("Course 2008/09",  "javadummy",   "Dummy experiments",  30),
        ("Course 2008/09",  "ud-logic",    "PIC experiments",   150),
        ("Course 2008/09",  "ud-dummy",    "Dummy experiments", 150),
        ("Course 2009/10",  "ud-fpga",     "FPGA experiments",  300),
    ])

    if tests != '2':
        _grant_permissions_to_groups(session, all_groups, all_experiments, [
            ("Federated users", "dummy3",  "Dummy experiments", 300),
        ])
    else:
        _grant_permissions_to_groups(session, all_groups, all_experiments, [
            ("Federated users", "dummy3_with_other_name",  "Dummy experiments", 300),
        ])


    _grant_permissions_to_users(session, all_users, all_experiments, [
        ("student2",   "ud-pld",                  "PLD experiments",        100),
        ("student6",   "ud-pld",                  "PLD experiments",        140),
        ("archimedes", "archimedes",              "Aquatic experiments",   1400),
        ("any",        "elevator",                "FPGA experiments",      1400),
        ("any",        "jsdummy",                 "Dummy experiments",     1400),
        ("any",        "jsfpga",                  "FPGA experiments",      1400),
        ("any",        "visir-html5",             "Visir experiments",     3600),
        ("any",        "ud-fpga",                 "FPGA experiments",      1400),
        ("any",        "visirtest",               "Dummy experiments",     3600),
        ("any",        "visir",                   "Visir experiments",     3600),
        ("any",        "ud-logic",                "PIC experiments",        200),
        ("any",        "binary",                  "Games",                  200),
        ("any",        "unr-physics",             "Physics experiments",    200),
        ("any",        "control-app",             "Control experiments",    200),
        ("any",        "incubator",               "Farm experiments",       200),
        ("any",        "ud-dummy",                "Dummy experiments",      200),
        ("any",        "ud-pic18",                "PIC experiments",        200),
        ("any",        "vm",                      "Dummy experiments",      200),
        ("any",        "vm-win",                  "Dummy experiments",      200),
        ("any",        "submarine",               "Submarine experiments",  200),
        ("any",        "http",                    "HTTP experiments",       200),
        ("any",        "aquarium",                "Aquatic experiments",    200),
        ("any",        "aquariumjs",              "Aquatic experiments",    200),
        ("any",        "submarinejs",             "Aquatic experiments",    200),
        ("any",        "robot-maze",              "Robot experiments",      200),
        ("any",        "robotarm",                "Robot experiments",      200),
        ("any",        "robot-standard",          "Robot experiments",      200),
        ("any",        "robot-movement",          "Robot experiments",      200),
        ("any",        "external-robot-movement", "Robot experiments",      200),
        ("any",        "microelectronics",        "iLab experiments",       200),
        ("any",        "blink-led",               "LabVIEW experiments",    200),
        ("any",        "robot-proglist",          "Robot experiments",      200),
        ("any",        "ud-dummy-batch",          "Dummy experiments",      200),
        ("any",        "ud-demo-pld",             "PLD experiments",        200),
        ("any",        "ud-demo-fpga",            "FPGA experiments",       200),
        ("any",        "ud-demo-xilinx",          "Xilinx experiments",     200),
        ("any",        "ud-gpib",                 "GPIB experiments",       150),
    ])

    up_student1_admin_panel_access = Model.DbUserPermission(
        all_users['student1'],
        permissions.ADMIN_PANEL_ACCESS,
        "student1::admin_panel_access",
        datetime.datetime.utcnow(),
        "Access to the admin panel for student1 with full_privileges"
    )
    session.add(up_student1_admin_panel_access)
    up_student1_admin_panel_access_p1 = Model.DbUserPermissionParameter(up_student1_admin_panel_access, permissions.FULL_PRIVILEGES, True)
    session.add(up_student1_admin_panel_access_p1)

    up_any_access_forward = Model.DbUserPermission(
        all_users['any'],
        permissions.ACCESS_FORWARD,
        "any::access_forward",
        datetime.datetime.utcnow(),
        "Access to forward external accesses"
    )

    session.add(up_any_access_forward)

    session.commit()

def generate_create_database(engine_str):
    "Generate a create_database function that creates the database"

    if engine_str == 'sqlite':

        import sqlite3
        dbi = sqlite3
        def create_database_sqlite(admin_username, admin_password, database_name, new_user, new_password, host = "localhost", port = None, db_dir = '.'):
            fname = os.path.join(db_dir, '%s.db' % database_name)
            if os.path.exists(fname):
                os.remove(fname)
            sqlite3.connect(database = fname).close()
        return create_database_sqlite

    elif engine_str == 'mysql':

        try:
            import MySQLdb
            dbi = MySQLdb
        except ImportError:
            try:
                import pymysql_sa
            except ImportError:
                raise Exception("Neither MySQLdb nor pymysql have been installed. First install them by running 'pip install pymysql' or 'pip install python-mysql'")
            pymysql_sa.make_default_mysql_dialect()
            import pymysql
            dbi = pymysql

        def create_database_mysql(error_message, admin_username, admin_password, database_name, new_user, new_password, host = "localhost", port = None, db_dir = '.'):
            args = {
                    'DATABASE_NAME' : database_name,
                    'USER'          : new_user,
                    'PASSWORD'      : new_password,
                }


            sentence1 = "DROP DATABASE IF EXISTS %(DATABASE_NAME)s;" % args
            sentence2 = "CREATE DATABASE %(DATABASE_NAME)s;" % args
            sentence3 = "GRANT ALL ON %(DATABASE_NAME)s.* TO '%(USER)s'@'%%' IDENTIFIED BY '%(PASSWORD)s';" % args
            sentence4 = "GRANT ALL ON %(DATABASE_NAME)s.* TO '%(USER)s'@'localhost' IDENTIFIED BY '%(PASSWORD)s';" % args
            sentence5 = "FLUSH PRIVILEGES;" % args

            try:
                kwargs = dict(db=database_name, user = admin_username, passwd = admin_password, host = host)
                if port is not None:
                    kwargs['port'] = port
                dbi.connect(**kwargs).close()
            except Exception, e:
                if e[1].startswith("Unknown database"):
                    sentence1 = "SELECT 1"

            for sentence in (sentence1, sentence2, sentence3, sentence4, sentence5):
                try:
                    kwargs = dict(user = admin_username, passwd = admin_password, host = host)
                    if port is not None:
                        kwargs['port'] = port
                    connection = dbi.connect(**kwargs)
                except dbi.OperationalError:
                    traceback.print_exc()
                    print >> sys.stderr, ""
                    print >> sys.stderr, "    %s" % error_message
                    print >> sys.stderr, ""
                    sys.exit(-1)
                else:
                    cursor = connection.cursor()
                    cursor.execute(sentence)
                    connection.commit()
                    connection.close()
        return create_database_mysql

    else:
        return None

def add_user(sessionmaker, login, password, user_name, mail, randomstuff = None, role = 'student'):
    session = sessionmaker()

    role = session.query(Model.DbRole).filter_by(name=role).one()
    weblab_db = session.query(Model.DbAuth).filter_by(name = "WebLab DB").one()

    user    = Model.DbUser(login, user_name, mail, None, role)
    session.add(user)

    user_auth = Model.DbUserAuth(user, weblab_db, _password2sha(password, randomstuff))
    session.add(user_auth)

    session.commit()
    session.close()

def add_group(sessionmaker, group_name):
    session = sessionmaker()
    group = Model.DbGroup(group_name)
    session.add(group)
    session.commit()
    session.close()

def add_users_to_group(sessionmaker, group_name, *user_logins):
    session = sessionmaker()
    group = session.query(Model.DbGroup).filter_by(name = group_name).one()
    users = session.query(Model.DbUser).filter(Model.DbUser.login.in_(user_logins)).all()
    for user in users:
        group.users.append(user)
    session.commit()
    session.close()

def add_experiment(sessionmaker, category_name, experiment_name, client):
    session = sessionmaker()
    existing_category = session.query(Model.DbExperimentCategory).filter_by(name = category_name).first()
    if existing_category is None:
        category = Model.DbExperimentCategory(category_name)
        session.add(category)
    else:
        category = existing_category

    start_date = datetime.datetime.utcnow()
    # So leap years are not a problem
    end_date = start_date.replace(year=start_date.year+12)

    experiment = Model.DbExperiment(experiment_name, category, start_date, end_date, client)
    _add_params(session, experiment)
    session.add(experiment)
    session.commit()
    session.close()

def grant_experiment_on_group(sessionmaker, category_name, experiment_name, group_name, time_allowed):
    session = sessionmaker()

    group = session.query(Model.DbGroup).filter_by(name = group_name).one()

    experiment_allowed = permissions.EXPERIMENT_ALLOWED

    experiment_allowed_p1 = permissions.EXPERIMENT_PERMANENT_ID
    experiment_allowed_p2 = permissions.EXPERIMENT_CATEGORY_ID
    experiment_allowed_p3 = permissions.TIME_ALLOWED

    group_permission = Model.DbGroupPermission(
        group, experiment_allowed,
        "%s users::%s@%s" % (group_name, experiment_name, category_name),
        datetime.datetime.utcnow(),
        "Permission for group %s users to use %s@%s" % (group_name, experiment_name, category_name))

    session.add(group_permission)

    group_permission_p1 = Model.DbGroupPermissionParameter(group_permission, experiment_allowed_p1, experiment_name)
    session.add(group_permission_p1)

    group_permission_p2 = Model.DbGroupPermissionParameter(group_permission, experiment_allowed_p2, category_name)
    session.add(group_permission_p2)

    group_permission_p3 = Model.DbGroupPermissionParameter(group_permission, experiment_allowed_p3, str(time_allowed))
    session.add(group_permission_p3)

    session.commit()
    session.close()

def grant_admin_panel_on_group(sessionmaker, group_name):
    session = sessionmaker()

    permission_type = permissions.ADMIN_PANEL_ACCESS
    group = session.query(Model.DbGroup).filter_by(name = group_name).one()
    group_permission = Model.DbGroupPermission(
                                    group,
                                    permission_type,
                                    'Administrators:admin-panel', datetime.datetime.now(), ''
                                )
    session.add(group_permission)
    group_permission_p1 = Model.DbGroupPermissionParameter(
                                    group_permission,
                                    permissions.FULL_PRIVILEGES,
                                    True
                                )
    session.add(group_permission_p1)
    session.commit()
    session.close()


def add_experiment_and_grant_on_group(sessionmaker, category_name, experiment_name, client, group_name, time_allowed):
    add_experiment(sessionmaker, category_name, experiment_name, client)
    grant_experiment_on_group(sessionmaker, category_name, experiment_name, group_name, time_allowed)

def _password2sha(password, randomstuff = None):
    if randomstuff is None:
        randomstuff = ""
        for _ in range(4):
            c = chr(ord('a') + random.randint(0,25))
            randomstuff += c
    password = password if password is not None else ''
    return randomstuff + "{sha}" + hashlib.new('sha1', randomstuff + password).hexdigest()
