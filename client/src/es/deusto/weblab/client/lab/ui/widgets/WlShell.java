package es.deusto.weblab.client.lab.ui.widgets;

import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyPressHandler;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.Widget;

public class WlShell implements IWlWidget {

    public class ShellTextArea extends TextArea {
	public ShellTextArea() {
	    super();
	    
	    this.addKeyPressHandler(new KeyPressHandler() {
		@Override
		public void onKeyPress(KeyPressEvent event) {
		    if ( WlShell.this.shellListener != null )
		    {
			WlShell.this.shellListener.onKeyPress(event);
		    }
		}
	    });
	}
    }

    private ShellTextArea shellTextArea;
    private IWlShellListener shellListener;
    
	public interface IWlShellListener{
		public void onKeyPress(KeyPressEvent event);
	}    
    
    public WlShell(int widthInCharacters, int heightInLines)
    {
	this.shellTextArea = new ShellTextArea();
	this.shellTextArea.setCharacterWidth(widthInCharacters);
	this.shellTextArea.setVisibleLines(heightInLines);
    }
    
    public void setStyleName(String styleName)
    {
	this.shellTextArea.setStyleName(styleName);
    }

    public void addKeyboardListener(IWlShellListener listener)
    {
	this.shellListener = listener;
    }
    
    @Override
    public Widget getWidget() {
	return this.shellTextArea;
    }

    public void dispose() {
	
    }

    public void print(String string) {
	String oldText = this.shellTextArea.getText();
	this.shellTextArea.setText(oldText+string);
    }
}