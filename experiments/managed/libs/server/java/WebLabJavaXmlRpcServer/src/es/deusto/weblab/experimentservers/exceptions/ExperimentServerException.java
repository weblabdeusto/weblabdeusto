package es.deusto.weblab.experimentservers.exceptions;

public class ExperimentServerException extends WebLabException {
	private static final long serialVersionUID = 3863429102493871235L;

	public ExperimentServerException() {}

	public ExperimentServerException(String message) {
		super(message);
	}

	public ExperimentServerException(Throwable cause) {
		super(cause);
	}

	public ExperimentServerException(String message, Throwable cause) {
		super(message, cause);
	}
}
