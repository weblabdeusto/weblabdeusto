package es.deusto.weblab.experimentservers;

import java.io.File;

import es.deusto.weblab.experimentservers.exceptions.WebLabException;

public interface IExperimentServer{
	public void startExperiment() throws WebLabException;
	public String sendFile(File file, String fileInfo) throws WebLabException;
	public String sendCommand(String command) throws WebLabException;
	public void dispose();
	public boolean isUpAndRunning();
	public boolean isDebugging();
}