package es.deusto.weblab.experimentservers.pic;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;

import es.deusto.weblab.experimentservers.ExperimentServer;
import es.deusto.weblab.experimentservers.exceptions.ExperimentServerInstantiationException;
import es.deusto.weblab.experimentservers.exceptions.WebLabException;

public class PicExperimentServer extends ExperimentServer {
	
	private static final String PROPERTIES_FILENAME = "pic.properties";
	private static final boolean DEBUG = false;
	
	private final String webcamUrl;
	private final String picServer;
	
	public PicExperimentServer() throws ExperimentServerInstantiationException{
		super(DEBUG, PROPERTIES_FILENAME);
		
		this.webcamUrl = this.properties.getProperty("webcamurl");
		if(this.webcamUrl == null)
			throw new ExperimentServerInstantiationException("webcamurl property not found in " + PROPERTIES_FILENAME);
		
		this.picServer = this.properties.getProperty("picserver");
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
		
		
		URLConnection con;
		try {
			URL url = new URL(this.picServer);
			con = url.openConnection();
			OutputStream os = con.getOutputStream();
			
		} catch (MalformedURLException e) {
			e.printStackTrace();
			throw new WebLabException("IOException sending command: " + e.getMessage(), e);
		} catch (IOException e) {
			e.printStackTrace();
			throw new WebLabException("IOException sending command: " + e.getMessage(), e);
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
