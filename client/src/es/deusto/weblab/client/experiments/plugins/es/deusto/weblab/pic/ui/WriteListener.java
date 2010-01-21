package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.pic.ui;

import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.pic.commands.WriteCommand;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.WlTextBoxWithButton;
import es.deusto.weblab.client.ui.widgets.IWlWidget;

class WriteListener implements IWlActionListener{
	private final IBoardBaseController commandSender;
	private final int boxCode;
	
	public WriteListener(int boxCode, IBoardBaseController commandSender){
		this.commandSender = commandSender;
		this.boxCode       = boxCode;
	}
	
	public void onAction(IWlWidget widget) {
		if(widget instanceof WlTextBoxWithButton){
			final WlTextBoxWithButton textbox = (WlTextBoxWithButton)widget;
			final String text = textbox.getText();
			final Command command = new WriteCommand(this.boxCode, text);
			this.commandSender.sendCommand(command);
		}else
			throw new IllegalArgumentException("Expected: WlWlTextBoxWithButton. Found: " + widget);
	}
}
