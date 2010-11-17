package es.deusto.weblab.experimentservers.exceptions;

public class InvalidContentException extends WebLabException {
	private static final long serialVersionUID = -7195769272072683196L;

	public InvalidContentException() {}

	public InvalidContentException(String message) {
		super(message);
	}

	public InvalidContentException(Throwable cause) {
		super(cause);
	}

	public InvalidContentException(String message, Throwable cause) {
		super(message, cause);
	}
}
