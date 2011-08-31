package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pic.ui;

import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.pic.commands.AdjustCommand;
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.IWlWidget;
import es.deusto.weblab.client.ui.widgets.WlPotentiometer;

class PotentiometerListener implements IWlActionListener{
	private final IBoardBaseController commandSender;
	private final int potentiometerCode;
	
	public PotentiometerListener(int potentiometerCode, IBoardBaseController commandSender){
		this.potentiometerCode = potentiometerCode;
		this.commandSender     = commandSender;
	}
	
	/*
	 * multiplier2decimals(1)    == 0
	 * multiplier2decimals(10)   == 1
	 * multiplier2decimals(100)  == 2
	 * multiplier2decimals(1000) == 3
	 */
	private int multiplier2decimals(int multiplier){
		int decimals = 0;
		int multi = multiplier;
		while(multi > 1){
			multi /= 10;
			decimals++;
		}
		return decimals;
	}
	
	@Override
	public void onAction(IWlWidget widget) {
		if(widget instanceof WlPotentiometer){
			final WlPotentiometer potentiometer = (WlPotentiometer)widget;
			
			final int multiplier = potentiometer.getMultiplier();
			final int decimals = this.multiplier2decimals(multiplier);
			final double power = potentiometer.getPower();
			
			final int value = (int)Math.round(power * multiplier);
			
			final Command command = new AdjustCommand(
					this.potentiometerCode, 
					value, 
					decimals
				);
			this.commandSender.sendCommand(command);
		}else
			throw new IllegalArgumentException("Expected: WlPotentiometer. Found: " + widget);
	}
}
