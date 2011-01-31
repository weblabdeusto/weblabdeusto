package es.deusto.weblab.client.ui.widgets;


public class WlIntegerTextbox extends WlNumberTextbox{

	public static final Integer DEFAULT_DIFFERENCE_VALUE  = new Integer(100);
	public static final Integer DEFAULT_VALUE             = new Integer(1000);
	
	public static final Integer MAX_VALUE                 = new Integer(Integer.MAX_VALUE);
	public static final Integer MIN_VALUE                 = new Integer(0);

	private final Integer minValue;
	private final Integer maxValue;
	
	public WlIntegerTextbox() {
		this(WlNumberTextBoxBase.DEFAULT_TEXT_LENGTH, WlIntegerTextbox.DEFAULT_DIFFERENCE_VALUE, WlIntegerTextbox.DEFAULT_VALUE, WlIntegerTextbox.MAX_VALUE, WlIntegerTextbox.MIN_VALUE);
	}

	public WlIntegerTextbox(int length, Integer difference, Integer defaultValue, Integer maxValue, Integer minValue) {
		super(length, difference, defaultValue, Integer.class);
		this.maxValue = maxValue;
		this.minValue = minValue;
	}

	@Override
	protected boolean isDigit(int keyCode) {
		return keyCode >= '0' && keyCode <= '9';
	}

	@Override
	public Number nextValue(Number intValue){
		final int newValue = intValue.intValue() + this.differenceValue.intValue();
		if(newValue <= this.getMaxValue().intValue())
			return new Integer(newValue);
		else
			return intValue;
	}

	@Override
	public Number previousValue(Number intValue){
		final int newValue = intValue.intValue() - this.differenceValue.intValue(); 
		if(newValue >= this.getMinValue().intValue())
			return new Integer(newValue);
		else
			return intValue;
	}

	@Override
	public Number getMaxValue() {
		return this.maxValue;
	}

	@Override
	public Number getMinValue() {
		return this.minValue;
	}
}
