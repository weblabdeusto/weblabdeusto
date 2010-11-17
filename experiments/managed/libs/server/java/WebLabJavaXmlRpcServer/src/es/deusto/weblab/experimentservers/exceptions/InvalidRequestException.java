package es.deusto.weblab.experimentservers.exceptions;

public class InvalidRequestException extends WebLabException {
	private static final long serialVersionUID = 6886514695224958455L;

	public InvalidRequestException() {}

	public InvalidRequestException(String message) {
		super(message);
	}

	public InvalidRequestException(Throwable cause) {
		super(cause);
	}

	public InvalidRequestException(String message, Throwable cause) {
		super(message, cause);
	}
}
