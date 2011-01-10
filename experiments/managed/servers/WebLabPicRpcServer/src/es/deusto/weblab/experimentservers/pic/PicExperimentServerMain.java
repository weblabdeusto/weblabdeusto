package es.deusto.weblab.experimentservers.pic;

import es.deusto.weblab.experimentservers.Launcher;

public class PicExperimentServerMain {
	public static void main(String [] args) throws Exception{
		PicExperimentServer experimentServer = new PicExperimentServer();
		Launcher launcher = new Launcher(11039, experimentServer);
		launcher.start();
	}
}
