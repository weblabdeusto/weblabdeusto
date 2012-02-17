package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.widgets.exceptions.WlWidgetException;

public class WlPotentiometer extends VerticalPanel implements IWlWidget {
	
	//TODO
	private static double MAX_POWER     = 5.0;
	private static double DEFAULT_POWER = 2.5;
	private static int DEFAULT_BUTTON_TIME = 1000;
	
	private final WlButton button;
	private final WlDoubleTextbox textbox;
	private final VerticalPanel visiblePanel;
	private final WlActionListenerContainer actionListenerContainer;
	private double power;
	
	private final Label title = new Label("");

	public WlPotentiometer(){
		this(WlPotentiometer.DEFAULT_POWER);
	}
	
	public WlPotentiometer(double power){
		
		this.button = new WlButton();
		this.button.setTime(WlPotentiometer.DEFAULT_BUTTON_TIME);
		this.textbox = new WlDoubleTextbox();
		this.textbox.setText(new Double(power));
		this.textbox.setMaxValue(WlPotentiometer.MAX_POWER);
		this.power = power;
		
		this.actionListenerContainer = new WlActionListenerContainer();
		
		this.visiblePanel = new VerticalPanel();
		this.visiblePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.visiblePanel.add(this.button.getWidget());
		this.visiblePanel.add(this.textbox.getWidget());

		this.button.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				WlPotentiometer.this.fireActionListeners();
			}
		});
		
		this.textbox.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				double doubleValue;
				try {
					doubleValue = WlPotentiometer.this.textbox.getValue().doubleValue();
				} catch (final WlWidgetException e) {
					return;
				}
				WlPotentiometer.this.power = doubleValue;
			}
		});
		
		this.setWidth("100%");
		this.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);		
		this.visiblePanel.add(this.title);
		
		this.add(this.visiblePanel);
	}
	
	public void setPower(double power) {
		this.textbox.setText(new Double(power));
		this.power = power;
	}
	
	public void setMaxPower(double maxPower) {
		this.textbox.setMaxValue(maxPower);
	}
	 
	@Override
	public void setTitle(String title) {
		this.title.setText(title);
	}
	
	@Override
	public void dispose(){
		this.button.dispose();
		this.textbox.dispose();
	}
	
	public void addActionListener(IWlActionListener listener){
		this.actionListenerContainer.addActionListener(listener);
	}
	
	public void removeActionListener(IWlActionListener listener){
		this.actionListenerContainer.removeActionListener(listener);
	}
	
	protected void fireActionListeners(){
		this.actionListenerContainer.fireActionListeners(this);
	}
	
	public int getMultiplier(){
		return this.textbox.getMultiplier();
	}
	
	public double getPower(){
		return this.power;
	}
	
	@Override
	public Widget getWidget() {
		return this;
	}
}
