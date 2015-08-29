package es.deusto.weblab.client.dto.experiments.commands;


/**
 * Represents a binary file data. It is different to a simple {@link BinaryData}
 * since it has a binary payload and a description of the file (which may or may 
 * not include the filename).
 */
public class BinaryFileData extends FileData {
	/**
	 * The data itself.
	 */
	private BinaryData fileData;

	/**
	 * @return the fileData
	 */
	public BinaryData getFileData() {
		return this.fileData;
	}
	
	/**
	 * @param fileData the fileData to set
	 */
	public void setFileData(BinaryData fileData) {
		this.fileData = fileData;
	}

	@Override
	protected InterchangedData getPayload() {
		return this.fileData;
	}	
}
