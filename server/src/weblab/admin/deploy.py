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

from sqlalchemy.orm import sessionmaker

from weblab.db.upgrade import DbRegularUpgrader
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
								   "experiment.name"		: "romie",
								   "experiment.category"	: "Dummy experiments",
								   "cssWidth"				: "1024",
								   "cssHeight"				: "680",
								   "provide.file.upload"	: False,
								   "html.file"				: "romie/romie.html"
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


#####################################################################
#
# Populating tests database
#

def populate_weblab_tests(engine, tests):
    Session = sessionmaker(bind=engine)
    session = Session()

    ldap = session.query(Model.DbAuthType).filter_by(name="LDAP").one()
    iptrusted = session.query(Model.DbAuthType).filter_by(name="TRUSTED-IP-ADDRESSES").one()
    facebook = session.query(Model.DbAuthType).filter_by(name="FACEBOOK").one()

    experiment_allowed = permissions.EXPERIMENT_ALLOWED
    experiment_allowed_p1 = permissions.EXPERIMENT_PERMANENT_ID
    experiment_allowed_p2 = permissions.EXPERIMENT_CATEGORY_ID
    experiment_allowed_p3 = permissions.TIME_ALLOWED

    admin_panel_access = permissions.ADMIN_PANEL_ACCESS
    admin_panel_access_p1 = permissions.FULL_PRIVILEGES

    access_forward = permissions.ACCESS_FORWARD

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
    admin1 = Model.DbUser("admin1", "Name of administrator 1", "weblab@deusto.es", None, administrator)
    session.add(admin1)

    archimedes_user = Model.DbUser("archimedes", "Usuario de prueba para Splash", "weblab@deusto.es", None, student)
    session.add(archimedes_user)

    admin2 = Model.DbUser("admin2", "Name of administrator 2", "weblab@deusto.es", None, administrator)
    session.add(admin2)

    admin3 = Model.DbUser("admin3", "Name of administrator 3", "weblab@deusto.es", None, administrator)
    session.add(admin3)

    any = Model.DbUser("any", "Name of any", "weblab@deusto.es", None, student)
    session.add(any)

    prof1 = Model.DbUser("prof1", "Name of instructor 1", "weblab@deusto.es", None, instructor)
    session.add(prof1)

    prof2 = Model.DbUser("prof2", "Name of instructor 2", "weblab@deusto.es", None, instructor)
    session.add(prof2)

    prof3 = Model.DbUser("prof3", "Name of instructor 3", "weblab@deusto.es", None, instructor)
    session.add(prof3)

    student1 = Model.DbUser("student1", "Name of student 1", "weblab@deusto.es", None, student)
    session.add(student1)

    student2 = Model.DbUser("student2", "Name of student 2", "weblab@deusto.es", None, student)
    session.add(student2)

    student3 = Model.DbUser("student3", "Name of student 3", "weblab@deusto.es", None, student)
    session.add(student3)

    student4 = Model.DbUser("student4", "Name of student 4", "weblab@deusto.es", None, student)
    session.add(student4)

    student5 = Model.DbUser("student5", "Name of student 5", "weblab@deusto.es", None, student)
    session.add(student5)

    student6 = Model.DbUser("student6", "Name of student 6", "weblab@deusto.es", None, student)
    session.add(student6)

    student7 = Model.DbUser("student7", "Name of student 7", "weblab@deusto.es", None, student)
    session.add(student7)

    student8 = Model.DbUser("student8", "Name of student 8", "weblab@deusto.es", None, student)
    session.add(student8)

    studentILAB = Model.DbUser("studentILAB", "Name of student ILAB", "weblab@deusto.es", None, student)
    session.add(studentILAB)

    studentLDAP1 = Model.DbUser("studentLDAP1", "Name of student LDAP1", "weblab@deusto.es", None, student)
    session.add(studentLDAP1)

    studentLDAP2 = Model.DbUser("studentLDAP2", "Name of student LDAP2", "weblab@deusto.es", None, student)
    session.add(studentLDAP2)

    studentLDAP3 = Model.DbUser("studentLDAP3", "Name of student LDAP3", "weblab@deusto.es", None, student)
    session.add(studentLDAP3)

    studentLDAPwithoutUserAuth = Model.DbUser("studentLDAPwithoutUserAuth", "Name of student LDAPwithoutUserAuth", "weblab@deusto.es", None, student)
    session.add(studentLDAPwithoutUserAuth)

    fed_student1 = Model.DbUser("fedstudent1", "Name of federated student 1", "weblab@deusto.es", None, federated)
    session.add(fed_student1)

    fed_student2 = Model.DbUser("fedstudent2", "Name of federated student 2", "weblab@deusto.es", None, federated)
    session.add(fed_student2)

    fed_student3 = Model.DbUser("fedstudent3", "Name of federated student 3", "weblab@deusto.es", None, federated)
    session.add(fed_student3)

    fed_student4 = Model.DbUser("fedstudent4", "Name of federated student 4", "weblab@deusto.es", None, federated)
    session.add(fed_student4)

    consumer_university1 = Model.DbUser("consumer1", "Consumer University 1", "weblab@deusto.es", None, federated)
    session.add(consumer_university1)

    provider_university1 = Model.DbUser("provider1", "Provider University 1", "weblab@deusto.es", None, federated)
    session.add(provider_university1)

    provider_university2 = Model.DbUser("provider2", "Provider University 2", "weblab@deusto.es", None, federated)
    session.add(provider_university2)

    # Authentication
    session.add(Model.DbUserAuth(archimedes_user,   weblab_db, _password2sha("archimedes", 'aaaa')))
    session.add(Model.DbUserAuth(admin1,   weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(admin2,   weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(admin3,   weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(any,      weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(prof1,    weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(prof2,    weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(prof3,    weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(student1, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(student2, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(student3, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(student4, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(student5, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(student6, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(student7, weblab_db, "aaaa{thishashdoesnotexist}a776159c8c7ff8b73e43aa54d081979e72511474"))
    session.add(Model.DbUserAuth(student8, weblab_db, "this.format.is.not.valid.for.the.password"))
    session.add(Model.DbUserAuth(studentILAB, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(fed_student1, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(fed_student2, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(fed_student3, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(fed_student4, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(consumer_university1, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(provider_university1, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(provider_university2, weblab_db, _password2sha("password", 'aaaa')))
    session.add(Model.DbUserAuth(any,      auth_facebook, "1168497114"))
    session.add(Model.DbUserAuth(studentLDAP1, cdk_ldap))
    session.add(Model.DbUserAuth(studentLDAP2, cdk_ldap))
    session.add(Model.DbUserAuth(studentLDAP3, deusto_ldap))

    # Groups
    group_federated = Model.DbGroup("Federated users")
    group_federated.users.append(fed_student1)
    group_federated.users.append(fed_student2)
    group_federated.users.append(fed_student3)
    group_federated.users.append(fed_student4)
    group_federated.users.append(consumer_university1)
    group_federated.users.append(provider_university1)
    group_federated.users.append(provider_university2)
    session.add(group_federated)

    groupCourse0809 = Model.DbGroup("Course 2008/09")
    groupCourse0809.users.append(student1)
    groupCourse0809.users.append(student2)
    session.add(groupCourse0809)

    groupMechatronics = Model.DbGroup("Mechatronics", groupCourse0809)
    groupMechatronics.users.append(student3)
    groupMechatronics.users.append(student4)
    session.add(groupMechatronics)

    groupTelecomunications = Model.DbGroup("Telecomunications", groupCourse0809)
    groupTelecomunications.users.append(student5)
    groupTelecomunications.users.append(student6)
    session.add(groupTelecomunications)

    groupCourse0910 = Model.DbGroup("Course 2009/10")
    groupCourse0910.users.append(student1)
    groupCourse0910.users.append(student2)
    groupCourse0910.users.append(student3)
    groupCourse0910.users.append(student4)
    groupCourse0910.users.append(student5)
    groupCourse0910.users.append(student6)
    session.add(groupCourse0910)

    # Experiment Categories
    cat_dummy = Model.DbExperimentCategory("Dummy experiments")
    session.add(cat_dummy)

    cat_games = Model.DbExperimentCategory("Games")
    session.add(cat_games)

    cat_physics = Model.DbExperimentCategory("Physics experiments")
    session.add(cat_physics)

    cat_pld = Model.DbExperimentCategory("PLD experiments")
    session.add(cat_pld)

    cat_fpga = Model.DbExperimentCategory("FPGA experiments")
    session.add(cat_fpga)

    cat_xilinx = Model.DbExperimentCategory("Xilinx experiments")
    session.add(cat_pld)

    cat_gpib = Model.DbExperimentCategory("GPIB experiments")
    session.add(cat_gpib)

    cat_pic = Model.DbExperimentCategory("PIC experiments")
    session.add(cat_pic)

    cat_robot = Model.DbExperimentCategory("Robot experiments")
    session.add(cat_robot)

    cat_submarine = Model.DbExperimentCategory("Submarine experiments")
    session.add(cat_submarine)

    cat_http = Model.DbExperimentCategory("HTTP experiments")
    session.add(cat_http)

    cat_aquatic = Model.DbExperimentCategory("Aquatic experiments")
    session.add(cat_aquatic)

    cat_labview = Model.DbExperimentCategory("LabVIEW experiments")
    session.add(cat_labview)

    cat_ilab = Model.DbExperimentCategory("iLab experiments")
    session.add(cat_ilab)

    cat_visir = Model.DbExperimentCategory("Visir experiments")
    session.add(cat_visir)

    cat_control = Model.DbExperimentCategory("Control experiments")
    session.add(cat_control)

    cat_farm = Model.DbExperimentCategory("Farm experiments")
    session.add(cat_farm)

    # Experiments
    start_date = datetime.datetime.utcnow()
    end_date = start_date.replace(year=start_date.year+12) # So leap years are not a problem

    dummy = Model.DbExperiment("ud-dummy", cat_dummy, start_date, end_date, 'dummy')
    session.add(dummy)
    _add_params(session, dummy)

    dummy_batch = Model.DbExperiment("ud-dummy-batch", cat_dummy, start_date, end_date, 'dummybatch')
    session.add(dummy_batch)
    _add_params(session, dummy_batch)

    archimedes = Model.DbExperiment("archimedes", cat_aquatic, start_date, end_date, 'js')
    session.add(archimedes)
    _add_params(session, archimedes)

    elevator = Model.DbExperiment("elevator", cat_fpga, start_date, end_date, 'js')
    session.add(elevator)
    _add_params(session, elevator)

    dummy1 = Model.DbExperiment("dummy1", cat_dummy, start_date, end_date, 'dummy')
    session.add(dummy1)
    _add_params(session, dummy1)

    dummy2 = Model.DbExperiment("dummy2", cat_dummy, start_date, end_date, 'dummy')
    session.add(dummy2)
    _add_params(session, dummy2)

    if tests != '2':
        dummy3 = Model.DbExperiment("dummy3", cat_dummy, start_date, end_date, 'dummy')
        session.add(dummy3)
        _add_params(session, dummy3)
    else:
        dummy3_with_other_name = Model.DbExperiment("dummy3_with_other_name", cat_dummy, start_date, end_date, 'dummy')
        session.add(dummy3_with_other_name)
        _add_params(session, dummy3_with_other_name)

    dummy4 = Model.DbExperiment("dummy4", cat_dummy, start_date, end_date, 'dummy')
    session.add(dummy4)
    _add_params(session, dummy4)

    flashdummy = Model.DbExperiment("flashdummy", cat_dummy, start_date, end_date, 'flash')
    session.add(flashdummy)
    _add_params(session, flashdummy)

    javadummy = Model.DbExperiment("javadummy", cat_dummy, start_date, end_date, 'java')
    session.add(javadummy)
    _add_params(session, javadummy)

    jsdummy = Model.DbExperiment("jsdummy", cat_dummy, start_date, end_date, 'js')
    session.add(jsdummy)
    _add_params(session, jsdummy)

    jsfpga = Model.DbExperiment("jsfpga", cat_fpga, start_date, end_date, 'js')
    session.add(jsfpga)
    _add_params(session, jsfpga)

    romie = Model.DbExperiment("romie", cat_dummy, start_date, end_date, 'js')
    session.add(romie)
    _add_params(session, romie)

    visir_html5 = Model.DbExperiment("visir-html5", cat_visir, start_date, end_date, 'js')
    session.add(visir_html5)
    _add_params(session, visir_html5)

    logic = Model.DbExperiment("ud-logic", cat_pic, start_date, end_date, 'logic')
    session.add(logic)
    _add_params(session, logic)

    binary = Model.DbExperiment("binary", cat_games, start_date, end_date, 'binary')
    session.add(binary)
    _add_params(session, binary)

    unr_physics = Model.DbExperiment("unr-physics", cat_physics, start_date, end_date, 'unr-physics')
    session.add(unr_physics)
    _add_params(session, unr_physics)

    controlapp = Model.DbExperiment("control-app", cat_control, start_date, end_date, 'control-app')
    session.add(controlapp)
    _add_params(session, controlapp)

    incubator = Model.DbExperiment("incubator", cat_farm, start_date, end_date, 'incubator')
    session.add(incubator)
    _add_params(session, incubator)

    pld = Model.DbExperiment("ud-pld", cat_pld, start_date, end_date, 'xilinx')
    session.add(pld)
    _add_params(session, pld)

    demo_pld = Model.DbExperiment("ud-demo-pld", cat_pld, start_date, end_date, 'xilinx')
    session.add(demo_pld)
    _add_params(session, demo_pld)

    pld2 = Model.DbExperiment("ud-pld2", cat_pld, start_date, end_date, 'xilinx')
    session.add(pld2)
    _add_params(session, pld2)

    fpga = Model.DbExperiment("ud-fpga", cat_fpga, start_date, end_date, 'xilinx')
    session.add(fpga)
    _add_params(session, fpga)

    demo_fpga = Model.DbExperiment("ud-demo-fpga", cat_fpga, start_date, end_date, 'xilinx')
    session.add(demo_fpga)
    _add_params(session, demo_fpga)

    demo_xilinx = Model.DbExperiment("ud-demo-xilinx", cat_xilinx, start_date, end_date, 'xilinx')
    session.add(demo_xilinx)
    _add_params(session, demo_xilinx)

    gpib = Model.DbExperiment("ud-gpib", cat_gpib, start_date, end_date, 'gpib')
    session.add(gpib)
    _add_params(session, gpib)

    visirtest = Model.DbExperiment("visirtest", cat_dummy, start_date, end_date, 'visir')
    session.add(visirtest)
    _add_params(session, visirtest)

    visir = Model.DbExperiment("visir", cat_visir, start_date, end_date, 'visir')
    session.add(visir)
    _add_params(session, visir)

    vm = Model.DbExperiment("vm", cat_dummy, start_date, end_date, 'vm')
    session.add(vm)
    _add_params(session, vm)

    vm_win = Model.DbExperiment("vm-win", cat_dummy, start_date, end_date, 'vm')
    session.add(vm_win)
    _add_params(session, vm_win)

    blink_led = Model.DbExperiment("blink-led", cat_labview, start_date, end_date, 'labview')
    session.add(blink_led)
    _add_params(session, blink_led)

    submarine = Model.DbExperiment("submarine", cat_submarine, start_date, end_date, 'submarine')
    session.add(submarine)
    _add_params(session, submarine)

    http = Model.DbExperiment("http", cat_http, start_date, end_date, 'redirect')
    session.add(http)
    _add_params(session, http)

    aquarium = Model.DbExperiment("aquarium", cat_aquatic, start_date, end_date, 'aquarium')
    session.add(aquarium)
    _add_params(session, aquarium)

    aquariumjs = Model.DbExperiment("aquariumjs", cat_aquatic, start_date, end_date, 'js')
    session.add(aquariumjs)
    _add_params(session, aquariumjs)

    submarinejs = Model.DbExperiment("submarinejs", cat_aquatic, start_date, end_date, 'js')
    _add_params(session, submarinejs)
    session.add(submarinejs)
    _add_params(session, submarinejs)

    rob_arm = Model.DbExperiment("robotarm", cat_robot, start_date, end_date, 'robotarm')
    session.add(rob_arm)
    _add_params(session, rob_arm)

    rob_maz = Model.DbExperiment("robot-maze", cat_robot, start_date, end_date, 'robot-maze')
    session.add(rob_maz)
    _add_params(session, rob_maz)

    rob_std = Model.DbExperiment("robot-standard", cat_robot, start_date, end_date, 'robot-standard')
    session.add(rob_std)
    _add_params(session, rob_std)

    rob_mov = Model.DbExperiment("robot-movement", cat_robot, start_date, end_date, 'robot-movement')
    session.add(rob_mov)
    _add_params(session, rob_mov)

    ext_rob_mov = Model.DbExperiment("external-robot-movement", cat_robot, start_date, end_date, 'blank')
    session.add(ext_rob_mov)
    _add_params(session, ext_rob_mov)

    rob_proglist = Model.DbExperiment("robot-proglist", cat_robot, start_date, end_date, 'robot-proglist')
    session.add(rob_proglist)
    _add_params(session, rob_proglist)

    microelectronics = Model.DbExperiment("microelectronics", cat_ilab, start_date, end_date, 'ilab-batch')
    session.add(microelectronics)
    _add_params(session, microelectronics)

    pic18 = Model.DbExperiment("ud-pic18", cat_pic, start_date, end_date, 'pic18')
    session.add(pic18)
    _add_params(session, pic18)

    # Permissions

    gp_course0809_fpga_allowed = Model.DbGroupPermission(
        groupCourse0809,
        experiment_allowed,
        "Course 2008/09::weblab-fpga",
        datetime.datetime.utcnow(),
        "Permission for group Course 2008/09 to use WebLab-FPGA"
    )
    session.add(gp_course0809_fpga_allowed)
    gp_course0809_fpga_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_fpga_allowed, experiment_allowed_p1, fpga.name)
    session.add(gp_course0809_fpga_allowed_p1)
    gp_course0809_fpga_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_fpga_allowed, experiment_allowed_p2, cat_fpga.name)
    session.add(gp_course0809_fpga_allowed_p2)
    gp_course0809_fpga_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_fpga_allowed, experiment_allowed_p3, "300")
    session.add(gp_course0809_fpga_allowed_p3)

    gp_federated_dummy1_allowed = Model.DbGroupPermission(
        group_federated,
        experiment_allowed,
        "Federated users::dummy1",
        datetime.datetime.utcnow(),
        "Permission for group Federated users to use dummy1"
    )
    session.add(gp_federated_dummy1_allowed)
    gp_federated_dummy1_allowed_p1 = Model.DbGroupPermissionParameter(gp_federated_dummy1_allowed, experiment_allowed_p1, "dummy1")
    session.add(gp_federated_dummy1_allowed_p1)
    gp_federated_dummy1_allowed_p2 = Model.DbGroupPermissionParameter(gp_federated_dummy1_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(gp_federated_dummy1_allowed_p2)
    gp_federated_dummy1_allowed_p3 = Model.DbGroupPermissionParameter(gp_federated_dummy1_allowed, experiment_allowed_p3, "300")
    session.add(gp_federated_dummy1_allowed_p3)

    gp_federated_dummy2_allowed = Model.DbGroupPermission(
        group_federated,
        experiment_allowed,
        "Federated users::dummy2",
        datetime.datetime.utcnow(),
        "Permission for group Federated users to use dummy2"
    )
    session.add(gp_federated_dummy2_allowed)
    gp_federated_dummy2_allowed_p1 = Model.DbGroupPermissionParameter(gp_federated_dummy2_allowed, experiment_allowed_p1, "dummy2")
    session.add(gp_federated_dummy2_allowed_p1)
    gp_federated_dummy2_allowed_p2 = Model.DbGroupPermissionParameter(gp_federated_dummy2_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(gp_federated_dummy2_allowed_p2)
    gp_federated_dummy2_allowed_p3 = Model.DbGroupPermissionParameter(gp_federated_dummy2_allowed, experiment_allowed_p3, "300")
    session.add(gp_federated_dummy2_allowed_p3)

    if tests != '2':
        gp_federated_dummy3_allowed = Model.DbGroupPermission(
            group_federated,
            experiment_allowed,
            "Federated users::dummy3",
            datetime.datetime.utcnow(),
            "Permission for group Federated users to use dummy3"
        )
        session.add(gp_federated_dummy3_allowed)
        gp_federated_dummy3_allowed_p1 = Model.DbGroupPermissionParameter(gp_federated_dummy3_allowed, experiment_allowed_p1, "dummy3")
        session.add(gp_federated_dummy3_allowed_p1)
        gp_federated_dummy3_allowed_p2 = Model.DbGroupPermissionParameter(gp_federated_dummy3_allowed, experiment_allowed_p2, "Dummy experiments")
        session.add(gp_federated_dummy3_allowed_p2)
        gp_federated_dummy3_allowed_p3 = Model.DbGroupPermissionParameter(gp_federated_dummy3_allowed, experiment_allowed_p3, "300")
        session.add(gp_federated_dummy3_allowed_p3)
    else:
        gp_federated_dummy3_with_other_name_allowed = Model.DbGroupPermission(
            group_federated,
            experiment_allowed,
            "Federated users::dummy3_with_other_name",
            datetime.datetime.utcnow(),
            "Permission for group Federated users to use dummy3_with_other_name"
        )
        session.add(gp_federated_dummy3_with_other_name_allowed)
        gp_federated_dummy3_with_other_name_allowed_p1 = Model.DbGroupPermissionParameter(gp_federated_dummy3_with_other_name_allowed, experiment_allowed_p1, "dummy3_with_other_name")
        session.add(gp_federated_dummy3_with_other_name_allowed_p1)
        gp_federated_dummy3_with_other_name_allowed_p2 = Model.DbGroupPermissionParameter(gp_federated_dummy3_with_other_name_allowed, experiment_allowed_p2, "Dummy experiments")
        session.add(gp_federated_dummy3_with_other_name_allowed_p2)
        gp_federated_dummy3_with_other_name_allowed_p3 = Model.DbGroupPermissionParameter(gp_federated_dummy3_with_other_name_allowed, experiment_allowed_p3, "300")
        session.add(gp_federated_dummy3_with_other_name_allowed_p3)

    gp_federated_dummy4_allowed = Model.DbGroupPermission(
        group_federated,
        experiment_allowed,
        "Federated users::dummy4",
        datetime.datetime.utcnow(),
        "Permission for group Federated users to use dummy4"
    )
    session.add(gp_federated_dummy4_allowed)
    gp_federated_dummy4_allowed_p1 = Model.DbGroupPermissionParameter(gp_federated_dummy4_allowed, experiment_allowed_p1, "dummy4")
    session.add(gp_federated_dummy4_allowed_p1)
    gp_federated_dummy4_allowed_p2 = Model.DbGroupPermissionParameter(gp_federated_dummy4_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(gp_federated_dummy4_allowed_p2)
    gp_federated_dummy4_allowed_p3 = Model.DbGroupPermissionParameter(gp_federated_dummy4_allowed, experiment_allowed_p3, "300")
    session.add(gp_federated_dummy4_allowed_p3)


    gp_course0809_flashdummy_allowed = Model.DbGroupPermission(
        groupCourse0809,
        experiment_allowed,
        "Course 2008/09::weblab-flashdummy",
        datetime.datetime.utcnow(),
        "Permission for group Course 2008/09 to use WebLab-FlashDummy"
    )
    session.add(gp_course0809_flashdummy_allowed)
    gp_course0809_flashdummy_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_flashdummy_allowed, experiment_allowed_p1, "flashdummy")
    session.add(gp_course0809_flashdummy_allowed_p1)
    gp_course0809_flashdummy_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_flashdummy_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(gp_course0809_flashdummy_allowed_p2)
    gp_course0809_flashdummy_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_flashdummy_allowed, experiment_allowed_p3, "30")
    session.add(gp_course0809_flashdummy_allowed_p3)

    gp_course0809_javadummy_allowed = Model.DbGroupPermission(
        groupCourse0809,
        experiment_allowed,
        "Course 2008/09::weblab-javadummy",
        datetime.datetime.utcnow(),
        "Permission for group Course 2008/09 to use WebLab-JavaDummy"
    )
    session.add(gp_course0809_javadummy_allowed)
    gp_course0809_javadummy_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_javadummy_allowed, experiment_allowed_p1, "javadummy")
    session.add(gp_course0809_javadummy_allowed_p1)
    gp_course0809_javadummy_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_javadummy_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(gp_course0809_javadummy_allowed_p2)
    gp_course0809_javadummy_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_javadummy_allowed, experiment_allowed_p3, "30")
    session.add(gp_course0809_javadummy_allowed_p3)

    gp_course0809_logic_allowed = Model.DbGroupPermission(
        groupCourse0809,
        experiment_allowed,
        "Course 2008/09::weblab-logic",
        datetime.datetime.utcnow(),
        "Permission for group Course 2008/09 to use WebLab-Logic"
    )
    session.add(gp_course0809_logic_allowed)
    gp_course0809_logic_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_logic_allowed, experiment_allowed_p1, "ud-logic")
    session.add(gp_course0809_logic_allowed_p1)
    gp_course0809_logic_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_logic_allowed, experiment_allowed_p2, "PIC experiments")
    session.add(gp_course0809_logic_allowed_p2)
    gp_course0809_logic_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_logic_allowed, experiment_allowed_p3, "150")
    session.add(gp_course0809_logic_allowed_p3)

    gp_course0809_dummy_allowed = Model.DbGroupPermission(
        groupCourse0809,
        experiment_allowed,
        "Course 2008/09::weblab-dummy",
        datetime.datetime.utcnow(),
        "Permission for group Course 2008/09 to use WebLab-Dummy"
    )
    session.add(gp_course0809_dummy_allowed)
    gp_course0809_dummy_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0809_dummy_allowed, experiment_allowed_p1, "ud-dummy")
    session.add(gp_course0809_dummy_allowed_p1)
    gp_course0809_dummy_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0809_dummy_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(gp_course0809_dummy_allowed_p2)
    gp_course0809_dummy_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0809_dummy_allowed, experiment_allowed_p3, "150")
    session.add(gp_course0809_dummy_allowed_p3)

    gp_course0910_fpga_allowed = Model.DbGroupPermission(
        groupCourse0910,
        experiment_allowed,
        "Course 2009/10::weblab-fpga",
        datetime.datetime.utcnow(),
        "Permission for group Course 2009/10 to use WebLab-FPGA"
    )
    session.add(gp_course0910_fpga_allowed)
    gp_course0910_fpga_allowed_p1 = Model.DbGroupPermissionParameter(gp_course0910_fpga_allowed, experiment_allowed_p1, fpga.name)
    session.add(gp_course0910_fpga_allowed_p1)
    gp_course0910_fpga_allowed_p2 = Model.DbGroupPermissionParameter(gp_course0910_fpga_allowed, experiment_allowed_p2, cat_fpga.name)
    session.add(gp_course0910_fpga_allowed_p2)
    gp_course0910_fpga_allowed_p3 = Model.DbGroupPermissionParameter(gp_course0910_fpga_allowed, experiment_allowed_p3, "300")
    session.add(gp_course0910_fpga_allowed_p3)

    up_student2_pld_allowed = Model.DbUserPermission(
        student2,
        experiment_allowed,
        "student2::weblab-pld",
        datetime.datetime.utcnow(),
        "Permission for student2 to use WebLab-PLD"
    )
    session.add(up_student2_pld_allowed)
    up_student2_pld_allowed_p1 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p1, "ud-pld")
    session.add(up_student2_pld_allowed_p1)
    up_student2_pld_allowed_p2 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p2, "PLD experiments")
    session.add(up_student2_pld_allowed_p2)
    up_student2_pld_allowed_p3 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p3, "100")
    session.add(up_student2_pld_allowed_p3)

    up_student6_pld_allowed = Model.DbUserPermission(
        student6,
        experiment_allowed,
        "student6::weblab-pld",
        datetime.datetime.utcnow(),
        "Permission for student6 to use WebLab-PLD"
    )
    session.add(up_student6_pld_allowed)
    up_student6_pld_allowed_p1 = Model.DbUserPermissionParameter(up_student6_pld_allowed, experiment_allowed_p1, "ud-pld")
    session.add(up_student6_pld_allowed_p1)
    up_student6_pld_allowed_p2 = Model.DbUserPermissionParameter(up_student6_pld_allowed, experiment_allowed_p2, "PLD experiments")
    session.add(up_student6_pld_allowed_p2)
    up_student6_pld_allowed_p3 = Model.DbUserPermissionParameter(up_student6_pld_allowed, experiment_allowed_p3, "140")
    session.add(up_student6_pld_allowed_p3)


    up_any_elevator_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::elevator",
        datetime.datetime.utcnow(),
        "Permission for any to use elevator"
    )
    session.add(up_any_elevator_allowed)
    up_any_elevator_allowed_p1 = Model.DbUserPermissionParameter(up_any_elevator_allowed, experiment_allowed_p1, "elevator")
    session.add(up_any_elevator_allowed_p1)
    up_any_elevator_allowed_p2 = Model.DbUserPermissionParameter(up_any_elevator_allowed, experiment_allowed_p2, "FPGA experiments")
    session.add(up_any_elevator_allowed_p2)
    up_any_elevator_allowed_p3 = Model.DbUserPermissionParameter(up_any_elevator_allowed, experiment_allowed_p3, "1400")
    session.add(up_any_elevator_allowed_p3)



    up_arch_archimedes_allowed = Model.DbUserPermission(
        archimedes_user,
        experiment_allowed,
        "arch::archimedes",
        datetime.datetime.utcnow(),
        "Permission for any to use archimedes"
    )
    session.add(up_arch_archimedes_allowed)
    up_arch_archimedes_allowed_p1 = Model.DbUserPermissionParameter(up_arch_archimedes_allowed, experiment_allowed_p1, "archimedes")
    session.add(up_arch_archimedes_allowed_p1)
    up_arch_archimedes_allowed_p2 = Model.DbUserPermissionParameter(up_arch_archimedes_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(up_arch_archimedes_allowed_p2)
    up_arch_archimedes_allowed_p3 = Model.DbUserPermissionParameter(up_arch_archimedes_allowed, experiment_allowed_p3, "1400")
    session.add(up_arch_archimedes_allowed_p3)


    up_any_jsdummy_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::jsdummy",
        datetime.datetime.utcnow(),
        "Permission for any to use jsdummy"
    )
    session.add(up_any_jsdummy_allowed)
    up_any_jsdummy_allowed_p1 = Model.DbUserPermissionParameter(up_any_jsdummy_allowed, experiment_allowed_p1, "jsdummy")
    session.add(up_any_jsdummy_allowed_p1)
    up_any_jsdummy_allowed_p2 = Model.DbUserPermissionParameter(up_any_jsdummy_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(up_any_jsdummy_allowed_p2)
    up_any_jsdummy_allowed_p3 = Model.DbUserPermissionParameter(up_any_jsdummy_allowed, experiment_allowed_p3, "1400")
    session.add(up_any_jsdummy_allowed_p3)

    up_any_jsfpga_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::jsfpga",
        datetime.datetime.utcnow(),
        "Permission for any to use jsfpga"
    )
    session.add(up_any_jsfpga_allowed)
    up_any_jsfpga_allowed_p1 = Model.DbUserPermissionParameter(up_any_jsfpga_allowed, experiment_allowed_p1, "jsfpga")
    session.add(up_any_jsfpga_allowed_p1)
    up_any_jsfpga_allowed_p2 = Model.DbUserPermissionParameter(up_any_jsfpga_allowed, experiment_allowed_p2, "FPGA experiments")
    session.add(up_any_jsfpga_allowed_p2)
    up_any_jsfpga_allowed_p3 = Model.DbUserPermissionParameter(up_any_jsfpga_allowed, experiment_allowed_p3, "1400")
    session.add(up_any_jsfpga_allowed_p3)

    up_any_romie_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::romie",
        datetime.datetime.utcnow(),
        "Permission for any to use romie"
    )
    session.add(up_any_romie_allowed)
    up_any_romie_allowed_p1 = Model.DbUserPermissionParameter(up_any_romie_allowed, experiment_allowed_p1, "romie")
    session.add(up_any_romie_allowed_p1)
    up_any_romie_allowed_p2 = Model.DbUserPermissionParameter(up_any_romie_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(up_any_romie_allowed_p2)
    up_any_romie_allowed_p3 = Model.DbUserPermissionParameter(up_any_romie_allowed, experiment_allowed_p3, "900")
    session.add(up_any_romie_allowed_p3)

    up_any_visir_html5_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::visir-html5",
        datetime.datetime.utcnow(),
        "Permission for any to use visir-html5"
    )
    session.add(up_any_visir_html5_allowed)
    up_any_visir_html5_allowed_p1 = Model.DbUserPermissionParameter(up_any_visir_html5_allowed, experiment_allowed_p1, "visir-html5")
    session.add(up_any_visir_html5_allowed_p1)
    up_any_visir_html5_allowed_p2 = Model.DbUserPermissionParameter(up_any_visir_html5_allowed, experiment_allowed_p2, "Visir experiments")
    session.add(up_any_visir_html5_allowed_p2)
    up_any_visir_html5_allowed_p3 = Model.DbUserPermissionParameter(up_any_visir_html5_allowed, experiment_allowed_p3, "3600")
    session.add(up_any_visir_html5_allowed_p3)


    up_any_fpga_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-fpga",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-FPGA"
    )
    session.add(up_any_fpga_allowed)
    up_any_fpga_allowed_p1 = Model.DbUserPermissionParameter(up_any_fpga_allowed, experiment_allowed_p1, fpga.name)
    session.add(up_any_fpga_allowed_p1)
    up_any_fpga_allowed_p2 = Model.DbUserPermissionParameter(up_any_fpga_allowed, experiment_allowed_p2, cat_fpga.name)
    session.add(up_any_fpga_allowed_p2)
    up_any_fpga_allowed_p3 = Model.DbUserPermissionParameter(up_any_fpga_allowed, experiment_allowed_p3, "1400")
    session.add(up_any_fpga_allowed_p3)


    up_any_visirtest_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-visirtest",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-VisirTest"
    )

    session.add(up_any_visirtest_allowed)
    up_any_visirtest_allowed_p1 = Model.DbUserPermissionParameter(up_any_visirtest_allowed, experiment_allowed_p1, "visirtest")
    session.add(up_any_visirtest_allowed_p1)
    up_any_visirtest_allowed_p2 = Model.DbUserPermissionParameter(up_any_visirtest_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(up_any_visirtest_allowed_p2)
    up_any_visirtest_allowed_p3 = Model.DbUserPermissionParameter(up_any_visirtest_allowed, experiment_allowed_p3, "3600")
    session.add(up_any_visirtest_allowed_p3)

    up_any_visir_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-visir",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-VisirTest"
    )

    session.add(up_any_visir_allowed)
    up_any_visir_allowed_p1 = Model.DbUserPermissionParameter(up_any_visir_allowed, experiment_allowed_p1, "visir")
    session.add(up_any_visir_allowed_p1)
    up_any_visir_allowed_p2 = Model.DbUserPermissionParameter(up_any_visir_allowed, experiment_allowed_p2, "Visir experiments")
    session.add(up_any_visir_allowed_p2)
    up_any_visir_allowed_p3 = Model.DbUserPermissionParameter(up_any_visir_allowed, experiment_allowed_p3, "3600")
    session.add(up_any_visir_allowed_p3)

    up_any_logic_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-logic",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-Logic"
    )

    session.add(up_any_logic_allowed)
    up_any_logic_allowed_p1 = Model.DbUserPermissionParameter(up_any_logic_allowed, experiment_allowed_p1, "ud-logic")
    session.add(up_any_logic_allowed_p1)
    up_any_logic_allowed_p2 = Model.DbUserPermissionParameter(up_any_logic_allowed, experiment_allowed_p2, "PIC experiments")
    session.add(up_any_logic_allowed_p2)
    up_any_logic_allowed_p3 = Model.DbUserPermissionParameter(up_any_logic_allowed, experiment_allowed_p3, "200")
    session.add(up_any_logic_allowed_p3)

    up_any_binary_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-binary",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-Logic"
    )

    session.add(up_any_binary_allowed)
    up_any_binary_allowed_p1 = Model.DbUserPermissionParameter(up_any_binary_allowed, experiment_allowed_p1, "binary")
    session.add(up_any_binary_allowed_p1)
    up_any_binary_allowed_p2 = Model.DbUserPermissionParameter(up_any_binary_allowed, experiment_allowed_p2, "Games")
    session.add(up_any_binary_allowed_p2)
    up_any_binary_allowed_p3 = Model.DbUserPermissionParameter(up_any_binary_allowed, experiment_allowed_p3, "200")
    session.add(up_any_binary_allowed_p3)

    up_any_unr_physics_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-unr_physics",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-Logic"
    )

    session.add(up_any_unr_physics_allowed)
    up_any_unr_physics_allowed_p1 = Model.DbUserPermissionParameter(up_any_unr_physics_allowed, experiment_allowed_p1, "unr-physics")
    session.add(up_any_unr_physics_allowed_p1)
    up_any_unr_physics_allowed_p2 = Model.DbUserPermissionParameter(up_any_unr_physics_allowed, experiment_allowed_p2, "Physics experiments")
    session.add(up_any_unr_physics_allowed_p2)
    up_any_unr_physics_allowed_p3 = Model.DbUserPermissionParameter(up_any_unr_physics_allowed, experiment_allowed_p3, "200")
    session.add(up_any_unr_physics_allowed_p3)


    up_any_controlapp_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-controlapp",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-Logic"
    )

    session.add(up_any_controlapp_allowed)
    up_any_controlapp_allowed_p1 = Model.DbUserPermissionParameter(up_any_controlapp_allowed, experiment_allowed_p1, "control-app")
    session.add(up_any_controlapp_allowed_p1)
    up_any_controlapp_allowed_p2 = Model.DbUserPermissionParameter(up_any_controlapp_allowed, experiment_allowed_p2, "Control experiments")
    session.add(up_any_controlapp_allowed_p2)
    up_any_controlapp_allowed_p3 = Model.DbUserPermissionParameter(up_any_controlapp_allowed, experiment_allowed_p3, "200")
    session.add(up_any_controlapp_allowed_p3)

    up_any_incubator_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-incubator",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-Logic"
    )

    session.add(up_any_incubator_allowed)
    up_any_incubator_allowed_p1 = Model.DbUserPermissionParameter(up_any_incubator_allowed, experiment_allowed_p1, "incubator")
    session.add(up_any_incubator_allowed_p1)
    up_any_incubator_allowed_p2 = Model.DbUserPermissionParameter(up_any_incubator_allowed, experiment_allowed_p2, "Farm experiments")
    session.add(up_any_incubator_allowed_p2)
    up_any_incubator_allowed_p3 = Model.DbUserPermissionParameter(up_any_incubator_allowed, experiment_allowed_p3, "200")
    session.add(up_any_incubator_allowed_p3)

    up_any_dummy_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::dummy",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-Dummy"
    )

    session.add(up_any_dummy_allowed)
    up_any_dummy_allowed_p1 = Model.DbUserPermissionParameter(up_any_dummy_allowed, experiment_allowed_p1, "ud-dummy")
    session.add(up_any_dummy_allowed_p1)
    up_any_dummy_allowed_p2 = Model.DbUserPermissionParameter(up_any_dummy_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(up_any_dummy_allowed_p2)
    up_any_dummy_allowed_p3 = Model.DbUserPermissionParameter(up_any_dummy_allowed, experiment_allowed_p3, "200")
    session.add(up_any_dummy_allowed_p3)



    up_any_pic18_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::pic18",
        datetime.datetime.utcnow(),
        "Permission for any to use ud-pic18"
    )

    session.add(up_any_pic18_allowed)
    up_any_pic18_allowed_p1 = Model.DbUserPermissionParameter(up_any_pic18_allowed, experiment_allowed_p1, "ud-pic18")
    session.add(up_any_pic18_allowed_p1)
    up_any_pic18_allowed_p2 = Model.DbUserPermissionParameter(up_any_pic18_allowed, experiment_allowed_p2, "pic experiments")
    session.add(up_any_pic18_allowed_p2)
    up_any_pic18_allowed_p3 = Model.DbUserPermissionParameter(up_any_pic18_allowed, experiment_allowed_p3, "200")
    session.add(up_any_pic18_allowed_p3)


    up_any_vm_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-vm",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-vm"
    )

    session.add(up_any_vm_allowed)
    up_any_vm_allowed_p1 = Model.DbUserPermissionParameter(up_any_vm_allowed, experiment_allowed_p1, "vm")
    session.add(up_any_vm_allowed_p1)
    up_any_vm_allowed_p2 = Model.DbUserPermissionParameter(up_any_vm_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(up_any_vm_allowed_p2)
    up_any_vm_allowed_p3 = Model.DbUserPermissionParameter(up_any_vm_allowed, experiment_allowed_p3, "200")
    session.add(up_any_vm_allowed_p3)



    up_any_vm_win_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-vm-win",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-vm-win"
    )


    session.add(up_any_vm_win_allowed)
    up_any_vm_win_allowed_p1 = Model.DbUserPermissionParameter(up_any_vm_win_allowed, experiment_allowed_p1, "vm-win")
    session.add(up_any_vm_win_allowed_p1)
    up_any_vm_win_allowed_p2 = Model.DbUserPermissionParameter(up_any_vm_win_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(up_any_vm_win_allowed_p2)
    up_any_vm_win_allowed_p3 = Model.DbUserPermissionParameter(up_any_vm_win_allowed, experiment_allowed_p3, "200")
    session.add(up_any_vm_win_allowed_p3)

    up_any_submarine_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-submarine",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-robot-standard"
    )

    session.add(up_any_submarine_allowed)
    up_any_submarine_allowed_p1 = Model.DbUserPermissionParameter(up_any_submarine_allowed, experiment_allowed_p1, "submarine")
    session.add(up_any_submarine_allowed_p1)
    up_any_submarine_allowed_p2 = Model.DbUserPermissionParameter(up_any_submarine_allowed, experiment_allowed_p2, "Submarine experiments")
    session.add(up_any_submarine_allowed_p2)
    up_any_submarine_allowed_p3 = Model.DbUserPermissionParameter(up_any_submarine_allowed, experiment_allowed_p3, "200")
    session.add(up_any_submarine_allowed_p3)

    up_any_http_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-http",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-http"
    )

    session.add(up_any_http_allowed)
    up_any_http_allowed_p1 = Model.DbUserPermissionParameter(up_any_http_allowed, experiment_allowed_p1, "http")
    session.add(up_any_http_allowed_p1)
    up_any_http_allowed_p2 = Model.DbUserPermissionParameter(up_any_http_allowed, experiment_allowed_p2, "HTTP experiments")
    session.add(up_any_http_allowed_p2)
    up_any_http_allowed_p3 = Model.DbUserPermissionParameter(up_any_http_allowed, experiment_allowed_p3, "200")
    session.add(up_any_http_allowed_p3)

    up_any_aquarium_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-aquarium",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-aquarium"
    )

    session.add(up_any_aquarium_allowed)
    up_any_aquarium_allowed_p1 = Model.DbUserPermissionParameter(up_any_aquarium_allowed, experiment_allowed_p1, "aquarium")
    session.add(up_any_aquarium_allowed_p1)
    up_any_aquarium_allowed_p2 = Model.DbUserPermissionParameter(up_any_aquarium_allowed, experiment_allowed_p2, "Aquatic experiments")
    session.add(up_any_aquarium_allowed_p2)
    up_any_aquarium_allowed_p3 = Model.DbUserPermissionParameter(up_any_aquarium_allowed, experiment_allowed_p3, "200")
    session.add(up_any_aquarium_allowed_p3)

    up_any_aquariumjs_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-aquariumjs",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-aquariumjs"
    )

    session.add(up_any_aquariumjs_allowed)
    up_any_aquariumjs_allowed_p1 = Model.DbUserPermissionParameter(up_any_aquariumjs_allowed, experiment_allowed_p1, "aquariumjs")
    session.add(up_any_aquariumjs_allowed_p1)
    up_any_aquariumjs_allowed_p2 = Model.DbUserPermissionParameter(up_any_aquariumjs_allowed, experiment_allowed_p2, "Aquatic experiments")
    session.add(up_any_aquariumjs_allowed_p2)
    up_any_aquariumjs_allowed_p3 = Model.DbUserPermissionParameter(up_any_aquariumjs_allowed, experiment_allowed_p3, "200")
    session.add(up_any_aquariumjs_allowed_p3)



    up_any_submarinejs_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-submarinejs",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-submarinejs"
    )

    session.add(up_any_submarinejs_allowed)
    up_any_submarinejs_allowed_p1 = Model.DbUserPermissionParameter(up_any_submarinejs_allowed, experiment_allowed_p1, "submarinejs")
    session.add(up_any_submarinejs_allowed_p1)
    up_any_submarinejs_allowed_p2 = Model.DbUserPermissionParameter(up_any_submarinejs_allowed, experiment_allowed_p2, "Aquatic experiments")
    session.add(up_any_submarinejs_allowed_p2)
    up_any_submarinejs_allowed_p3 = Model.DbUserPermissionParameter(up_any_submarinejs_allowed, experiment_allowed_p3, "200")
    session.add(up_any_submarinejs_allowed_p3)


    up_any_rob_maz_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-maz",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-maz"
    )

    session.add(up_any_rob_maz_allowed)
    up_any_rob_maz_allowed_p1 = Model.DbUserPermissionParameter(up_any_rob_maz_allowed, experiment_allowed_p1, "robot-maze")
    session.add(up_any_rob_maz_allowed_p1)
    up_any_rob_maz_allowed_p2 = Model.DbUserPermissionParameter(up_any_rob_maz_allowed, experiment_allowed_p2, "Robot experiments")
    session.add(up_any_rob_maz_allowed_p2)
    up_any_rob_maz_allowed_p3 = Model.DbUserPermissionParameter(up_any_rob_maz_allowed, experiment_allowed_p3, "200")
    session.add(up_any_rob_maz_allowed_p3)


    up_any_rob_robotarm_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-robotarm",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-robotarm"
    )

    session.add(up_any_rob_robotarm_allowed)
    up_any_rob_robotarm_allowed_p1 = Model.DbUserPermissionParameter(up_any_rob_robotarm_allowed, experiment_allowed_p1, "robotarm")
    session.add(up_any_rob_robotarm_allowed_p1)
    up_any_rob_robotarm_allowed_p2 = Model.DbUserPermissionParameter(up_any_rob_robotarm_allowed, experiment_allowed_p2, "Robot experiments")
    session.add(up_any_rob_robotarm_allowed_p2)
    up_any_rob_robotarm_allowed_p3 = Model.DbUserPermissionParameter(up_any_rob_robotarm_allowed, experiment_allowed_p3, "200")
    session.add(up_any_rob_robotarm_allowed_p3)


    up_any_rob_std_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-robot-standard",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-robot-standard"
    )

    session.add(up_any_rob_std_allowed)
    up_any_rob_std_allowed_p1 = Model.DbUserPermissionParameter(up_any_rob_std_allowed, experiment_allowed_p1, "robot-standard")
    session.add(up_any_rob_std_allowed_p1)
    up_any_rob_std_allowed_p2 = Model.DbUserPermissionParameter(up_any_rob_std_allowed, experiment_allowed_p2, "Robot experiments")
    session.add(up_any_rob_std_allowed_p2)
    up_any_rob_std_allowed_p3 = Model.DbUserPermissionParameter(up_any_rob_std_allowed, experiment_allowed_p3, "200")
    session.add(up_any_rob_std_allowed_p3)


    up_any_rob_mov_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-robot-movement",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-robot-movement"
    )

    session.add(up_any_rob_mov_allowed)
    up_any_rob_mov_allowed_p1 = Model.DbUserPermissionParameter(up_any_rob_mov_allowed, experiment_allowed_p1, "robot-movement")
    session.add(up_any_rob_mov_allowed_p1)
    up_any_rob_mov_allowed_p2 = Model.DbUserPermissionParameter(up_any_rob_mov_allowed, experiment_allowed_p2, "Robot experiments")
    session.add(up_any_rob_mov_allowed_p2)
    up_any_rob_mov_allowed_p3 = Model.DbUserPermissionParameter(up_any_rob_mov_allowed, experiment_allowed_p3, "200")
    session.add(up_any_rob_mov_allowed_p3)

    up_any_ext_rob_mov_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-external-robot-movement",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-external-robot-movement"
    )

    session.add(up_any_ext_rob_mov_allowed)
    up_any_ext_rob_mov_allowed_p1 = Model.DbUserPermissionParameter(up_any_ext_rob_mov_allowed, experiment_allowed_p1, "external-robot-movement")
    session.add(up_any_ext_rob_mov_allowed_p1)
    up_any_ext_rob_mov_allowed_p2 = Model.DbUserPermissionParameter(up_any_ext_rob_mov_allowed, experiment_allowed_p2, "Robot experiments")
    session.add(up_any_ext_rob_mov_allowed_p2)
    up_any_ext_rob_mov_allowed_p3 = Model.DbUserPermissionParameter(up_any_ext_rob_mov_allowed, experiment_allowed_p3, "200")
    session.add(up_any_ext_rob_mov_allowed_p3)

    up_studentILAB_microelectronics_allowed = Model.DbUserPermission(
        studentILAB,
        experiment_allowed,
        "studentILAB::weblab-microelectronics",
        datetime.datetime.utcnow(),
        "Permission for studentILAB to use WebLab-microelectronics"
    )

    session.add(up_studentILAB_microelectronics_allowed)
    up_studentILAB_microelectronics_allowed_p1 = Model.DbUserPermissionParameter(up_studentILAB_microelectronics_allowed, experiment_allowed_p1, "microelectronics")
    session.add(up_studentILAB_microelectronics_allowed_p1)
    up_studentILAB_microelectronics_allowed_p2 = Model.DbUserPermissionParameter(up_studentILAB_microelectronics_allowed, experiment_allowed_p2, "iLab experiments")
    session.add(up_studentILAB_microelectronics_allowed_p2)
    up_studentILAB_microelectronics_allowed_p3 = Model.DbUserPermissionParameter(up_studentILAB_microelectronics_allowed, experiment_allowed_p3, "200")
    session.add(up_studentILAB_microelectronics_allowed_p3)


    up_any_blink_led_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-blink-led",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-blink-led"
    )

    session.add(up_any_blink_led_allowed)
    up_any_blink_led_allowed_p1 = Model.DbUserPermissionParameter(up_any_blink_led_allowed, experiment_allowed_p1, "blink-led")
    session.add(up_any_blink_led_allowed_p1)
    up_any_blink_led_allowed_p2 = Model.DbUserPermissionParameter(up_any_blink_led_allowed, experiment_allowed_p2, "LabVIEW experiments")
    session.add(up_any_blink_led_allowed_p2)
    up_any_blink_led_allowed_p3 = Model.DbUserPermissionParameter(up_any_blink_led_allowed, experiment_allowed_p3, "200")
    session.add(up_any_blink_led_allowed_p3)

    up_any_rob_proglist_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-robot-proglist",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-robot-proglist"
    )

    session.add(up_any_rob_proglist_allowed)
    up_any_rob_proglist_allowed_p1 = Model.DbUserPermissionParameter(up_any_rob_proglist_allowed, experiment_allowed_p1, "robot-proglist")
    session.add(up_any_rob_proglist_allowed_p1)
    up_any_rob_proglist_allowed_p2 = Model.DbUserPermissionParameter(up_any_rob_proglist_allowed, experiment_allowed_p2, "Robot experiments")
    session.add(up_any_rob_proglist_allowed_p2)
    up_any_rob_proglist_allowed_p3 = Model.DbUserPermissionParameter(up_any_rob_proglist_allowed, experiment_allowed_p3, "200")
    session.add(up_any_rob_proglist_allowed_p3)




    up_any_dummy_batch_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-dummy-batch",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-dummy-batch"
    )


    session.add(up_any_dummy_batch_allowed)
    up_any_dummy_batch_allowed_p1 = Model.DbUserPermissionParameter(up_any_dummy_batch_allowed, experiment_allowed_p1, "ud-dummy-batch")
    session.add(up_any_dummy_batch_allowed_p1)
    up_any_dummy_batch_allowed_p2 = Model.DbUserPermissionParameter(up_any_dummy_batch_allowed, experiment_allowed_p2, "Dummy experiments")
    session.add(up_any_dummy_batch_allowed_p2)
    up_any_dummy_batch_allowed_p3 = Model.DbUserPermissionParameter(up_any_dummy_batch_allowed, experiment_allowed_p3, "200")
    session.add(up_any_dummy_batch_allowed_p3)


    up_any_pld_demo_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-pld-demo",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-pld-demo"
    )


    session.add(up_any_pld_demo_allowed)
    up_any_pld_demo_allowed_p1 = Model.DbUserPermissionParameter(up_any_pld_demo_allowed, experiment_allowed_p1, "ud-demo-pld")
    session.add(up_any_pld_demo_allowed_p1)
    up_any_pld_demo_allowed_p2 = Model.DbUserPermissionParameter(up_any_pld_demo_allowed, experiment_allowed_p2, "PLD experiments")
    session.add(up_any_pld_demo_allowed_p2)
    up_any_pld_demo_allowed_p3 = Model.DbUserPermissionParameter(up_any_pld_demo_allowed, experiment_allowed_p3, "200")
    session.add(up_any_pld_demo_allowed_p3)

    up_any_fpga_demo_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-fpga-demo",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-fpga-demo"
    )

    session.add(up_any_fpga_demo_allowed)
    up_any_fpga_demo_allowed_p1 = Model.DbUserPermissionParameter(up_any_fpga_demo_allowed, experiment_allowed_p1, "ud-demo-fpga")
    session.add(up_any_fpga_demo_allowed_p1)
    up_any_fpga_demo_allowed_p2 = Model.DbUserPermissionParameter(up_any_fpga_demo_allowed, experiment_allowed_p2, cat_fpga.name)
    session.add(up_any_fpga_demo_allowed_p2)
    up_any_fpga_demo_allowed_p3 = Model.DbUserPermissionParameter(up_any_fpga_demo_allowed, experiment_allowed_p3, "200")
    session.add(up_any_fpga_demo_allowed_p3)

    up_any_xilinx_demo_allowed = Model.DbUserPermission(
        any,
        experiment_allowed,
        "any::weblab-xilinx-demo",
        datetime.datetime.utcnow(),
        "Permission for any to use WebLab-xilinx-demo"
    )

    session.add(up_any_xilinx_demo_allowed)
    up_any_xilinx_demo_allowed_p1 = Model.DbUserPermissionParameter(up_any_xilinx_demo_allowed, experiment_allowed_p1, "ud-demo-xilinx")
    session.add(up_any_xilinx_demo_allowed_p1)
    up_any_xilinx_demo_allowed_p2 = Model.DbUserPermissionParameter(up_any_xilinx_demo_allowed, experiment_allowed_p2, "Xilinx experiments")
    session.add(up_any_xilinx_demo_allowed_p2)
    up_any_xilinx_demo_allowed_p3 = Model.DbUserPermissionParameter(up_any_xilinx_demo_allowed, experiment_allowed_p3, "200")
    session.add(up_any_xilinx_demo_allowed_p3)

    up_student2_gpib_allowed = Model.DbUserPermission(
        student2,
        experiment_allowed,
        "student2::weblab-gpib",
        datetime.datetime.utcnow(),
        "Permission for student2 to use WebLab-GPIB"
    )
    session.add(up_student2_gpib_allowed)
    up_student2_gpib_allowed_p1 = Model.DbUserPermissionParameter(up_student2_gpib_allowed, experiment_allowed_p1, "ud-gpib")
    session.add(up_student2_gpib_allowed_p1)
    up_student2_gpib_allowed_p2 = Model.DbUserPermissionParameter(up_student2_gpib_allowed, experiment_allowed_p2, "GPIB experiments")
    session.add(up_student2_gpib_allowed_p2)
    up_student2_gpib_allowed_p3 = Model.DbUserPermissionParameter(up_student2_gpib_allowed, experiment_allowed_p3, "150")
    session.add(up_student2_gpib_allowed_p3)

    up_student1_admin_panel_access = Model.DbUserPermission(
        student1,
        admin_panel_access,
        "student1::admin_panel_access",
        datetime.datetime.utcnow(),
        "Access to the admin panel for student1 with full_privileges"
    )
    session.add(up_student1_admin_panel_access)
    up_student1_admin_panel_access_p1 = Model.DbUserPermissionParameter(up_student1_admin_panel_access, admin_panel_access_p1, True)
    session.add(up_student1_admin_panel_access_p1)

    up_any_access_forward = Model.DbUserPermission(
        any,
        access_forward,
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
