package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.event.dom.client.KeyDownEvent;
import com.google.gwt.event.dom.client.KeyDownHandler;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.Widget;

public class WlShell implements IWlWidget {

    public class ShellTextArea extends TextArea {
	public ShellTextArea() {
	    super();
	    
	    this.addKeyDownHandler(new KeyDownHandler() {
		@Override
		public void onKeyDown(KeyDownEvent event) {
		    if ( WlShell.this.shellListener != null )
		    {
			WlShell.this.shellListener.onKeyDown(event);
		    }
		}
	    });
	}
    }

    private final ShellTextArea shellTextArea;
    private IWlShellListener shellListener;
    
	public interface IWlShellListener{
		public void onKeyDown(KeyDownEvent event);
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

    @Override
	public void dispose() {
	
    }

    public void print(String string) {
	final String oldText = this.shellTextArea.getText();
	this.shellTextArea.setText(oldText+string);
    }
}