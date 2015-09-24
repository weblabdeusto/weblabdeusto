package es.deusto.weblab.client.ui.widgets;



public class WlDoubleTextbox extends WlNumberTextbox{
	public static final Double DEFAULT_DIFFERENCE_VALUE  = new Double(0.1);
	public static final Double DEFAULT_VALUE             = new Double(2.5);
	public static final int DEFAULT_MULTIPLIER           = 10;
	public static final Double MAX_VALUE                 = new Double(Double.MAX_VALUE);
	public static final Double MIN_VALUE                 = new Double(0.0);
	
	private double maxValue;
	private double minValue;
	
	private final int multiplier;

	public WlDoubleTextbox() {
		this(WlNumberTextBoxBase.DEFAULT_TEXT_LENGTH, WlDoubleTextbox.DEFAULT_DIFFERENCE_VALUE, WlDoubleTextbox.DEFAULT_VALUE, WlDoubleTextbox.MAX_VALUE, WlDoubleTextbox.MIN_VALUE);
	}

	public WlDoubleTextbox(int length, Double difference, Double defaultValue, Double maxValue, Double minValue) {
		super(length, difference, defaultValue, Double.class);
		
		this.multiplier = WlDoubleTextbox.DEFAULT_MULTIPLIER;
		
		this.maxValue = maxValue.doubleValue();
		this.minValue = minValue.doubleValue();
	}
	
	@Override
	protected boolean isDigit(int keyCode) {
		if(keyCode >= '0' && keyCode <= '9')
			return true;
		if(keyCode != '.' && keyCode != ',')
			return false;
		//If there is already a , or a .
		if(this.textBox.getText().indexOf(",") < 0 && this.textBox.getText().indexOf(".") < 0)
			return true;
		return false;
	}
	
	@Override
	public Number getMaxValue(){
		return new Double(this.maxValue);
	}

	public void setMaxValue(double maxValue){
		this.maxValue = maxValue;
	}

	@Override
	public Number getMinValue(){
		return new Double(this.minValue);
	}
	
	public void setMinValue(double minValue){
		this.minValue = minValue;
	}
	
	public int getMultiplier(){
		return this.multiplier;
	}

	@Override
	public Number nextValue(Number doubleValue){
		double newDouble = doubleValue.doubleValue() + this.differenceValue.doubleValue();
		newDouble = this.adjust(newDouble);
		if(newDouble <= this.getMaxValue().doubleValue())
			return new Double(newDouble);
		else
			return doubleValue;
	}

	private double adjust(double newDouble) {
		return (1.0 * Math.round(newDouble * this.multiplier)) / this.multiplier;
	}

	@Override
	public Number previousValue(Number doubleValue){
		double newDouble = doubleValue.doubleValue() - this.differenceValue.doubleValue();
		newDouble = this.adjust(newDouble);
		if(newDouble >= this.getMinValue().doubleValue())
			return new Double(newDouble);
		else
			return doubleValue;
	}
}
