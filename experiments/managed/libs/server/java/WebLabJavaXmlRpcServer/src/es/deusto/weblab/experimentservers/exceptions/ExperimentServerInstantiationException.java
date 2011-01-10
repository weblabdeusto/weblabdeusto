package es.deusto.weblab.experimentservers.exceptions;

public class ExperimentServerInstantiationException extends WebLabException {
	private static final long serialVersionUID = -6252463598543622421L;

	public ExperimentServerInstantiationException() {
	}

	public ExperimentServerInstantiationException(String message) {
		super(message);
	}

	public ExperimentServerInstantiationException(Throwable cause) {
		super(cause);
	}

	public ExperimentServerInstantiationException(String message,
			Throwable cause) {
		super(message, cause);
	}
}
