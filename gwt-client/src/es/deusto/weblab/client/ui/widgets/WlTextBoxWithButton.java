package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyDownEvent;
import com.google.gwt.event.dom.client.KeyDownHandler;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class WlTextBoxWithButton extends VerticalPanel implements IWlWidget{

	private final TextBox textbox;
	private final WlButton sendButton;
	private final Widget widget;
	private final WlActionListenerContainer actionListenerContainer;
	
	private static final int DEFAULT_LENGTH      = 20;
	private static final int BUTTON_MILLISECONDS = 500;
	
	private final Label title = new Label();
	
	public WlTextBoxWithButton(){
		this(WlTextBoxWithButton.DEFAULT_LENGTH);
		
		this.setWidth("100%");
		this.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		
		this.add(this.widget);
		this.add(this.title);
	}
	
	@Override
	public void setTitle(String title) {
		this.title.setText(title);
	}
	
	public WlTextBoxWithButton(int length){
		this.actionListenerContainer = new WlActionListenerContainer();
		
		this.textbox = new TextBox();
		this.textbox.setWidth(length + "em");
		
		final KeyDownHandler keyboardHandler = new KeyDownHandler(){
			@Override
			public void onKeyDown(KeyDownEvent event) {
				if(event.getNativeKeyCode() == KeyCodes.KEY_ENTER){
					WlTextBoxWithButton.this.fireEnterKey();
				}
			}
		};
		this.textbox.addKeyDownHandler(keyboardHandler);
		
		this.sendButton = new WlButton(WlTextBoxWithButton.BUTTON_MILLISECONDS);
		this.sendButton.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				WlTextBoxWithButton.this.fireActionListener();
			}
		});
		
		final HorizontalPanel hpanel = new HorizontalPanel();
		hpanel.add(this.textbox);
		hpanel.add(this.sendButton.getWidget());
		
		this.widget = hpanel;	
		
		this.setWidth("100%");
		this.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		this.add(this.widget);
		this.add(this.title);
	}

	public String getText(){
		return this.textbox.getText();
	}
	
	
	
	public void addActionListener(IWlActionListener listener){
		this.actionListenerContainer.addActionListener(listener);
	}

	public void removeActionListener(IWlActionListener listener){
		this.actionListenerContainer.removeActionListener(listener);
	}
	
	private void fireEnterKey(){
		this.sendButton.buttonPressed();
		this.fireActionListener();
	}
	
	private void fireActionListener(){
		this.actionListenerContainer.fireActionListeners(this);
	}

	@Override
	public Widget getWidget() {
		return this;
	}

	@Override
	public void dispose() {
	}
}
