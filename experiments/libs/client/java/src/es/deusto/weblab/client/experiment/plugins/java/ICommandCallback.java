package es.deusto.weblab.client.experiment.plugins.java;

public interface ICommandCallback {
	public void onSuccess(ResponseCommand response);
	public void onFailure(String message);
}
