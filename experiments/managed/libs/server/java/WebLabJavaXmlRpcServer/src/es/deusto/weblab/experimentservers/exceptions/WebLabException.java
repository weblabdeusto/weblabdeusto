package es.deusto.weblab.experimentservers.exceptions;

public class WebLabException extends Exception {
	private static final long serialVersionUID = 3007058296396828608L;

	public WebLabException() {}

	public WebLabException(String message) {
		super(message);
	}

	public WebLabException(Throwable cause) {
		super(cause);
	}

	public WebLabException(String message, Throwable cause) {
		super(message, cause);
	}
}
