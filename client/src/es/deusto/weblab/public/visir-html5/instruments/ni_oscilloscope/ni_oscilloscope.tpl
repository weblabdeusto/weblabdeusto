<div class="ni_osc unselectable">
	<div class="graph">
		<div class="left">
			<div class="offsetbox ch2"><div class="offset"><span>2</span></div></div>
			<div class="offsetbox ch1"><div class="offset"><span>1</span></div></div>
			
		</div>
		<div class="right">
			<div class="offsetbox trigger"><div class="offset"><span>T</span></div></div>
		</div>		

		<div class="renderarea">
			<canvas class="grid" width="600" height="490"></canvas>
			<canvas class="plot" width="600" height="490"></canvas>
			<div class="clickarea"></div>
		</div>
	</div>
	<div class="control">
		<div class="buttonlist">
			<button>Auto</button>
			<button>Single</button>
			<button>Pause</button>
		</div>
		<div class="panel channel">
			<div class="paneltitle">Channel</div>
			<div class="innerpanel">
				<select name="ch1">
					<option value="0" selected>0</option>
					<option value="1">1</option>
				</select>
				<div class="enabled">
					<input type="checkbox" name="ch1_enabled" value="ch1_enabled" checked />Enabled
				</div>
				<div class="label">Volts/Div</div>
				<div class="knob_outer">
					<div class="knob_inner">
						<div class="arrow"></div>
					</div>
				</div>
				<select name="voltdiv_ch1" class="voltdiv ch1">
				</select>
				<div class="label">Coupling</div>
				<select name="coupling">
					<option value="0" selected>AC</option>
					<option value="1">DC</option>
				</select>
			</div>
			<div class="sideslider">
				<div class="thumb"></div>
			</div>
		</div>
		<div class="panel channel">
			<div class="innerpanel">
				<select name="ch2">
					<option value="0">0</option>
					<option value="1" selected>1</option>
				</select>
				<div class="enabled">
					<input type="checkbox" name="ch1_enabled" value="ch1_enabled" checked />Enabled
				</div>
				<div class="label">Volts/Div</div>
				<div class="knob_outer">
					<div class="knob_inner">
						<div class="arrow"></div>
					</div>
				</div>
				<select name="voltdiv_ch2" class="voltdiv ch2">
				</select>
				<div class="label">Coupling</div>
				<select name="coupling">
					<option value="0" selected>AC</option>
					<option value="1">DC</option>
				</select>
			</div>
			<div class="sideslider">
				<div class="thumb"></div>
			</div>
		</div>
		<div class="panel horizontal">
			<div class="paneltitle">Horizontal</div>
			<div class="label">Ref Position</div>
			<div class="horzbuttonlist">
				<button>10</button>
				<button>50</button>
				<button>90</button>
			</div>
			<div class="label">Time/Div</div>
			<div class="knob_outer">
				<div class="knob_inner">
					<div class="arrow"></div>
				</div>
			</div>
			<select class="timediv">
			</select>

		</div>
		<div class="menubuttonpanel">
			<button>CHAN</button>
			<button>TRIG</button>
			<button>HORIZ</button>
			<button>MEAS</button>
			<button>CURS</button>
			<button>DISP</button>
		</div>
	</div>
</div>