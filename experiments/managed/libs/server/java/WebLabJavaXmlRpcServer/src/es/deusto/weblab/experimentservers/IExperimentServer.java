package es.deusto.weblab.experimentservers;

import java.io.File;

public interface IExperimentServer{
	public void startExperiment() throws WebLabException;
	public String sendFile(File file, String fileInfo) throws WebLabException;
	public String sendCommand(String command) throws WebLabException;
	public void dispose();
}