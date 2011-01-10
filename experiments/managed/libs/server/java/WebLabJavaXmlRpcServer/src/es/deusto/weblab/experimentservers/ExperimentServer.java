package es.deusto.weblab.experimentservers;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

import es.deusto.weblab.experimentservers.exceptions.ExperimentServerInstantiationException;

public abstract class ExperimentServer implements IExperimentServer {

	private static final boolean DEFAULT_DEBUGGING = false;
	private final boolean debugging;
	protected final Properties properties = new Properties();
	
	public ExperimentServer() throws ExperimentServerInstantiationException {
		this(DEFAULT_DEBUGGING);
	}
	
	public ExperimentServer(boolean debugging) throws ExperimentServerInstantiationException {
		this(debugging, null);
	}
	
	public ExperimentServer(String propertiesPath) throws ExperimentServerInstantiationException {
		this(DEFAULT_DEBUGGING, propertiesPath);
	}
	
	public ExperimentServer(boolean debugging, String propertiesPath) throws ExperimentServerInstantiationException {
		this.debugging = debugging;
		if(propertiesPath != null){
			try {
				properties.load(new FileInputStream(new File(propertiesPath)));
			} catch (IOException e) {
				throw new ExperimentServerInstantiationException("PIC properties file couldn't be loaded! " + e.getMessage(), e);
			}
		}
	}
	
	public boolean isDebugging(){
		return this.debugging;
	}
	
	public boolean isUpAndRunning() {
		return true;
	}
}
