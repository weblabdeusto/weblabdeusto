package es.deusto.weblab.client.dto.experiments.commands;

/**
 * Represents a text file data. It is different to a simple {@link TextData}
 * since it has a text payload and a description of the file (which may or may 
 * not include the filename).
 */
public class TextFileData extends FileData {
	/**
	 * The data itself.
	 */
	private TextData fileData;

	/**
	 * @return the fileData
	 */
	public TextData getFileData() {
		return this.fileData;
	}

	/**
	 * @param fileData the fileData to set
	 */
	public void setFileData(TextData fileData) {
		this.fileData = fileData;
	}
	
	@Override
	protected InterchangedData getPayload(){
		return this.fileData;
	}
}
