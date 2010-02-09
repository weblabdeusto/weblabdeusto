/*
* Copyright (C) 2005-2009 University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.pic.commands;

import es.deusto.weblab.client.dto.experiments.Command;

public class AdjustCommand extends Command{
	private final int potentiometerCode;
	private final int value;
	private final int decimals;
	
	public AdjustCommand(int potentiometerCode, int value, int decimals){
		this.potentiometerCode = potentiometerCode;
		this.value             = value;
		this.decimals          = decimals;
	}
	
	@Override
    public String getCommandString() {
        String decimalValue = Integer.toString(this.value);

        while(decimalValue.length() < (this.decimals + 1))
                decimalValue = "0" + decimalValue;

        final String integerPart = decimalValue.substring(0, decimalValue.length() - this.decimals);
        final String floatPart = "." + decimalValue.substring(decimalValue.length() - this.decimals, decimalValue.length());

        String finalValue = integerPart;
        if(floatPart.length() > 1)
                finalValue += floatPart;

        return "ADJUST=" + this.potentiometerCode + " " + finalValue;
    }
}
