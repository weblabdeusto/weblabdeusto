package es.deusto.weblab.experimentservers.exceptions;

public class ExperimentServerInternalException extends ExperimentServerException {
	private static final long serialVersionUID = -6060990951954695554L;

	public ExperimentServerInternalException() {}

	public ExperimentServerInternalException(String message) {
		super(message);
	}

	public ExperimentServerInternalException(Throwable cause) {
		super(cause);
	}

	public ExperimentServerInternalException(String message, Throwable cause) {
		super(message, cause);
	}
}
