package es.deusto.weblab.experimentservers;

import java.io.File;

import es.deusto.weblab.experimentservers.exceptions.WebLabException;

public interface IExperimentServer{
	public String startExperiment(String clientInitialData, String serverInitialData) throws WebLabException;
	public int shouldFinish();
	public String sendFile(File file, String fileInfo) throws WebLabException;
	public String sendCommand(String command) throws WebLabException;
	public String dispose();
	public boolean isUpAndRunning();
	public boolean isDebugging();
}