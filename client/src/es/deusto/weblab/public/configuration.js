{
	// "weblab.service.fileupload.post.url" : "/weblab/fileUpload.php", 
	"admin.email"    : "weblab@deusto.es",
	"demo.available" : "true",
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
					        	   "width"               : 500,
					        	   "height"              : 350,
					        	   "swf.file"            : "WeblabFlashSample.swf",
					        	   "message"             : "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Adobe Flash in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible."
	                       		},
	                       		// Other flash experiments could be added here
	                       ],
	                "java" : [
	                          {
	                        	  "experiment.name"      : "javadummy",
	                        	  "experiment.category"  : "Dummy experiments",
	                        	  "width"                : 500,
	                        	  "height"               : 350,
	                        	  "jar.file"             : "WeblabJavaSample.jar",
	                        	  "code"                 : "es.deusto.weblab.client.experiment.plugins.es.deusto.weblab.javadummy.JavaDummyApplet",
	                          },
	                          // Other java experiments could be added here
	                       ],
	                "vm"    : [
	                           {
	                        	   "experiment.name"     : "vm",
	                        	   "experiment.category" : "Dummy experiments",
	                           }
	                       ],
	                "cpld" : [
	                          {
	                        	  "experiment.name"      : "ud-pld",
	                        	  "experiment.category"  : "PLD experiments",
	                          }
	                       ],
	                "fpga" : [
	                          {
	                        	  "experiment.name"      : "ud-fpga",
	                        	  "experiment.category"  : "FPGA experiments",
	                          }
	                       ],
	                "dummy" : [
	                           {
	                        	   "experiment.name"     : "ud-dummy",
	                        	   "experiment.category" : "Dummy experiments",
	                           }
	                       ],
	                "visir" : [
	                           {
	                        	   "experiment.name"     : "visirtest",
	                        	   "experiment.category" : "Dummy experiments",
	                           }
	                       ],
	                "logic" : [
	                           {
	                        	   "experiment.name"     : "ud-logic",
	                        	   "experiment.category" : "PIC experiments",
	                           }
	                       ],
	                "binary" : [
	                            {
	                               "experiment.name"     : "ud-binary",
	                               "experiment.category" : "PLD experiments",
	                            }
	                       ],
	                "gpib"   : [
	                            {
	                               "experiment.name"     : "ud-gpib",
	                               "experiment.category" : "GPIB experiments",
	                            }
	                       ],
	                "gpib1" : [
	                            {
	                               "experiment.name"     : "ud-gpib1",
	                               "experiment.category" : "GPIB experiments",
	                            }
	                        ],
	                "gpib2" : [
	                           {
	                        	   "experiment.name"     : "ud-gpib2",
	                        	   "experiment.category" : "GPIB experiments",
	                           }   
	                        ],
	                "pic"   : [
	                           {
	                        	   "experiment.name"     : "ud-pic",
	                        	   "experiment.category" : "PIC experiments",
	                           }
	                        ]
		}
}
