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
	"admin.email"                    : "weblab@deusto.es",
	"demo.available"                 : true,
	"google.analytics.tracking.code" : "UA-12576838-6",
	"sound.enabled"					 : false,
	"experiments.default_picture"	 : "/img/experiments/default.jpg",
	"host.entity.image"              : "/img/udeusto-logo.jpg",
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
					        	   "message"             : "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Adobe Flash in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible."
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
	                        	  "message"             : "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Java Applets in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible."
	                          }
	                          // Other java experiments could be added here
	                       ],
	                "vm"    : [
	                           {
	                        	   "experiment.name"     : "vm",
	                        	   "experiment.category" : "Dummy experiments"
	                           },
	                           {
	                        	   "experiment.name"     : "ud-linux-vm",
	                        	   "experiment.category" : "VM experiments"
	                           },
	                           {
	                        	   "experiment.name"     : "ud-win-vm",
	                        	   "experiment.category" : "VM experiments"
	                           },
	                           {   "experiment.name"	 : "vm-win",
	                               "experiment.category" : "Dummy experiments"
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
								   "is.demo"             : true
							  },
							  {
								   "experiment.name"     : "ud-demo-fpga",
								   "experiment.category" : "FPGA experiments",
	                        	   "experiment.picture"   : "/img/experiments/xilinx.jpg",
								   "is.demo"             : true
						      },
						      {
							       "experiment.name"     : "ud-demo-xilinx",
							       "experiment.category" : "Xilinx experiments",
	                        	   "experiment.picture"   : "/img/experiments/xilinx.jpg",
							       "is.demo"             : true,
							       "is.multiresource.demo" : true
						      },
							  {
								   "experiment.name"     : "ud-fpga",
								   "experiment.category" : "FPGA experiments",
	                        	   "experiment.picture"   : "/img/experiments/xilinx.jpg"
							  },
	                          {
	                        	  "experiment.name"      : "ud-pld",
	                        	  "experiment.category"  : "PLD experiments",
	                        	  "experiment.picture"   : "/img/experiments/xilinx.jpg"
	                          }
	                       ],
	                "dummy" : [
	                           {
	                        	   "experiment.name"     : "ud-dummy",
	                        	   "experiment.category" : "Dummy experiments"
	                           }
	                       ],
	                "visir" : [
	                           {
	                        	   "experiment.name"     : "visirtest",
	                        	   "experiment.category" : "Dummy experiments",
	                        	   "experiment.picture"  : "/img/experiments/visir.jpg",
	                        	   "page.timer"          : true,
	                        	   "page.footer"         : "Powered by the wonderful <a href='http://openlabs.bth.se/index.php?page=ElectroLab'>VISIR</a> <a href='http://svn.openlabs.bth.se/'>Open Source</a> project developed at the <a href='http://www.bth.se/'>BTH</a>"
	                           },
	                           {
	                        	   "experiment.name"     : "lxi_visir",
	                        	   "experiment.category" : "Visir experiments",
	                        	   "experiment.picture"  : "/img/experiments/visir.jpg",
	                        	   "page.timer"          : true,
	                        	   "page.footer"         : "Powered by the wonderful <a href='http://openlabs.bth.se/index.php?page=ElectroLab'>VISIR</a> <a href='http://svn.openlabs.bth.se/'>Open Source</a> project developed at the <a href='http://www.bth.se/'>BTH</a>"
	                           },
                                   {
	                        	   "experiment.name"     : "visir",
	                        	   "experiment.category" : "Visir experiments",
	                        	   "experiment.picture"  : "/img/experiments/visir.jpg",
	                        	   "page.timer"          : true,
	                        	   "page.footer"         : "Powered by the wonderful <a href='http://openlabs.bth.se/index.php?page=ElectroLab'>VISIR</a> <a href='http://svn.openlabs.bth.se/'>Open Source</a> project developed at the <a href='http://www.bth.se/'>BTH</a>"
	                           }
	                       ],
	                "logic" : [
	                           {
	                        	   "experiment.name"     : "ud-logic",
	                        	   "experiment.category" : "PIC experiments",
	                        	  "experiment.picture"   : "/img/experiments/logic.jpg"
	                           }
	                       ],
	                "binary" : [
	                            {
	                               "experiment.name"     : "ud-binary",
	                               "experiment.category" : "PLD experiments"
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
	                "pic"   : [
	                           {
	                        	   "experiment.name"     : "ud-pic",
	                        	   "experiment.category" : "PIC experiments",
	                        	   "experiment.picture"  : "/img/experiments/microchip.jpg"
	                           }
	                        ],
	                "pic2"  : [
	                           {
	                        	   "experiment.name"     : "ud-pic2",
	                        	   "experiment.category" : "PIC experiments",
	                        	   "experiment.picture"  : "/img/experiments/microchip.jpg"
	                           }
	                        ]
		}
}
