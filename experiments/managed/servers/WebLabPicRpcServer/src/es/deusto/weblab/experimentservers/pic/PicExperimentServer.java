package es.deusto.weblab.experimentservers.pic;

import java.io.File;

import es.deusto.weblab.experimentservers.ExperimentServer;
import es.deusto.weblab.experimentservers.exceptions.ExperimentServerInstantiationException;
import es.deusto.weblab.experimentservers.exceptions.WebLabException;

public class PicExperimentServer extends ExperimentServer {
	
	private static final String PROPERTIES_FILENAME = "pic.properties";
	private static final boolean DEBUG = false;
	
	private final String webcamUrl; 
	
	public PicExperimentServer() throws ExperimentServerInstantiationException{
		super(DEBUG, PROPERTIES_FILENAME);
		
		this.webcamUrl = this.properties.getProperty("webcamurl");
		if(this.webcamUrl == null)
			throw new ExperimentServerInstantiationException("webcamurl property not found in " + PROPERTIES_FILENAME);
	}

	@Override
	public void startExperiment() throws WebLabException {
		
	}
	
	@Override
	public String sendCommand(String command) throws WebLabException {
		System.out.println(command);
		if(command.equals("WEBCAMURL")){
			return "WEBCAMURL=" + this.webcamUrl;
		}
		return "ok: " + command;
	}

	@Override
	public String sendFile(File file, String fileInfo) throws WebLabException {
		System.out.println("El fichero está en: " + file.getAbsolutePath());
		return "ok";
	}

	@Override
	public void dispose() {
	}
	
}
