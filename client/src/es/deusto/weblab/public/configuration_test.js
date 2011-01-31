{
	"property1"        : "value1",
	"property2"        : "value2",
	"property3"        : "value3",
	"intproperty1"     : 15,
	"wrongintproperty" : "this.is.not.an.int",
	"experiments" : { 
		"flash" : [
		           {
		        	   "experiment.name"     : "flashdummy",
		        	   "experiment.category" : "Dummy experiments",
		        	   "width"               : 500,
		        	   "height"              : 350,
		        	   "swf.file"            : "WeblabFlashSample.swf",
		        	   "message"             : "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Adobe Flash in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible."
               		},
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
               ],
	}
}