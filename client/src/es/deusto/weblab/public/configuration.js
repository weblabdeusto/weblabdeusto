{
	// IMPORTANT
	//
	// Internet Explorer can't parse dictionaries as:
	//  {
	//        'foo' : 'bar',
	//  }
	// 
	// Due to the last ',' after 'bar'. Same for lists
	//   [
	//      1,
	//      2,
	//      //3
	//   ]
	// Would produce an error since there is a ',' and then a ']'.
	// 
	// "weblab.service.fileupload.post.url" : "/weblab/fileUpload.php", 
	"development"                    : true, // To see the latest features, although they might not be working
	"demo.available"                 : true,
	"sound.enabled"					 : false,
	"admin.email"                    : "weblab@deusto.es",
	"google.analytics.tracking.code" : "UA-12576838-6",
	"experiments.default_picture"	 : "/img/experiments/default.jpg",
	"host.entity.image.login"        : "/img/udeusto-logo.jpg",
	"host.entity.image"              : "/img/udeusto-logo-main.jpg",
	"host.entity.image.mobile"       : "/img/udeusto-logo-mobile.jpg",
	"host.entity.link"               : "http://www.deusto.es/",
    "facebook.like.box.visible"      : false,
	"experiments" : { 
					// Experiments not developed in GWT (such as those developed in Flash or Java) don't require
					// recompiling the client to be loaded. Adding them to this configuration file is enough.
					// Also those experiments that are inherently reusable for different classes, such as 
					// those based in Virtual Machines (that will need to handle different experiment names 
					// and categories) can be added here.
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
	                       		// Other flash experiments could be added here
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
	                          // Other java experiments could be added here
	                       ],
	                "js"	: [
	                    	   {
	                    		   "experiment.name"		: "jsdummy",
	                    		   "experiment.category"	: "Dummy experiments",
	                    		   "experiment.picture"		: "/img/experiments/java.jpg",
	                    		   "width"					: 500,
	                    		   "height"					: 350,
	                    		   //"js.file"				: "test.js",
	                    		   "provide.file.upload"	: true,
	                    		   // If we use an html.file as base, we cannot use a js.file.
	                    		   // (Though of course, we may include that js file from our html file).
	                    		   "html.file"				: "jstest.html"
	                    	   },
	                    	   {
	                    		   "experiment.name"		: "jsfpga",
	                    		   "experiment.category"	: "FPGA experiments",
	                    		   "experiment.picture"		: "/img/experiments/xilinx.jpg",
	                    		   "width"					: 800,
	                    		   "height"					: 600,
	                    		   "provide.file.upload"	: true,
	                    		   "html.file"				: "jsxilinx/jsxilinx.html"
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
	                            	"send.file"           : true
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
								   "is.demo"             : true
							  },
							  {
								   "experiment.name"     : "ud-test-pld2",
								   "experiment.category" : "PLD experiments",
	                        	   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : true
							  },
							  {
								   "experiment.name"     : "ud-demo-pld",
								   "experiment.category" : "PLD experiments",
	                        	   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : true,
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#cpld",
	                        	   "experiment.info.description" : "description"
							  },
							  {
								   "experiment.name"     : "ud-demo-fpga",
								   "experiment.category" : "FPGA experiments",
	                        	   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : true,
								   "experiment.info.link" : "http://weblabdeusto.readthedocs.org/en/latest/sample_labs.html#fpga",
	                        	   "experiment.info.description" : "description"
						      },
						      {
							       "experiment.name"     : "ud-demo-xilinx",
							       "experiment.category" : "Xilinx experiments",
	                        	   "experiment.picture"   : "/img/experiments/xilinx.jpg",
							       "is.demo"             : true,
							       "is.multiresource.demo" : true,
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
								   "is.demo"             : true
	                			},
	                			{
	                			   "experiment.name"	 : "ud-test-pic18-2",
	                			   "experiment.category" : "PIC experiments",
	                			   "experiment.picture"  : "/img/experiments/microchip.jpg",
								   "is.demo"             : true
	                			},
	                			{
	                			   "experiment.name"	 : "ud-test-pic18-3",
	                			   "experiment.category" : "PIC experiments",
	                			   "experiment.picture"  : "/img/experiments/microchip.jpg",
								   "is.demo"             : true
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
                                	"experiment.reserve.button.shown" : false,
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
                                    "experiment.reserve.button.shown" : false,
                                	"html"                            : "This lab is disabled at this moment. Go to <a target=\"_blank\" href=\"http://130.206.138.18/lastexp/\">the original site</a> to see the archived results."
                                }
                            ]
		}
}
