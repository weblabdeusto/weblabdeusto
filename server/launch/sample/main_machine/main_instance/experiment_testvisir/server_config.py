#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

vt_measure_server_addr = "130.206.138.35:8080"
vt_measure_server_target = "/measureserver"
vt_base_url = """https://weblab-visir.deusto.es/electronics/"""
vt_login_url = """https://weblab-visir.deusto.es/electronics/index.php?sel=login_check"""
vt_login_email = "guest"
vt_login_password = "guest"

vt_client_url = "../web/visir/loader.swf"

vt_debug_prints = False

# 
# Uncomment these two lines to enable the student mode with a given configuration
# 
# If you want to add other examples, try clicking on "save" circuit in VISIR, and place the .cir content here.
# 
# vt_teacher = False
# vt_not_savedata = \
vt_savedata = """
<save>
	<instruments list="breadboard/breadboard.swf|multimeter/multimeter.swf|functiongenerator/functiongenerator.swf|oscilloscope/oscilloscope.swf|tripledc/tripledc.swf"/>
	<multimeter/>
		<circuit>
			<circuitlist>
              <component>R 10k 65 13 0</component>
              <component>R 10k 65 39 0</component>
              <component>R 1k 65 65 0</component>
			</circuitlist>
		</circuit>
</save>
"""


vt_circuits = {}




vt_circuits["Single Line experiment"] = \
"""
<save><instruments list="breadboard/breadboard.swf|multimeter/multimeter.swf|functiongenerator/functiongenerator.swf|oscilloscope/oscilloscope.swf|tripledc/tripledc.swf"/><circuit><circuitlist><component>W 255 442 234 457.15 279.5 442 325</component></circuitlist></circuit></save>
"""

vt_circuits["House experiment"] = \
"""
<save>
  <instruments list="breadboard/breadboard.swf|multimeter/multimeter.swf|functiongenerator/functiongenerator.swf|oscilloscope/oscilloscope.swf|tripledc/tripledc.swf"/>
  <circuit>
    <circuitlist>
      <component>W 255 312 208 338 286 312 364</component>
      <component>W 255 338 208 353.15 166.8 390 143</component>
      <component>W 255 403 143 459.3 160.3 494 208</component>
      <component>W 255 494 221 515.65 286 494 351</component>
      <component>W 255 338 351 409.5 327.15 481 351</component>
      <component>W 16711680 390 273 392.15 296.8 390 325</component>
      <component>W 16711680 416 273 431.15 296.8 429 325</component>
      <component>W 16711680 390 260 404 279 416 260</component>
      <component>W 16776960 351 195 364 212.3 364 221</component>
      <component>W 16776960 377 221 390 216.65 403 221</component>
      <component>W 16776960 390 195 400.8 205.8 403 221</component>
      <component>W 16776960 364 195 377 190.65 390 195</component>
      <component>W 16776960 429 195 442 212.3 442 234</component>
      <component>W 16776960 468 234 481 229.65 494 234</component>
      <component>W 16776960 481 208 470.15 197.15 455 195</component>
      <component>W 16776960 442 195 448.5 192.8 455 195</component>
    </circuitlist>
  </circuit>
</save>
"""

vt_library__REMOVE_THIS_TO_TEST_THIS = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE components PUBLIC "-//Open labs//DTD COMPONENTS 1.0//EN" "http://openlabs.bth.se/DTDs/components-1.0.dtd">
<components>
	

	
	<!-- alterado em 06/04/2011 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="R" value="1.5M" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_1.5M.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_1.5M.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->

	

	
	<component type="R" value="220k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_220k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_220k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
		
		<component type="R" value="120k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_120k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_120k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="R" value="150k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_150k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_150k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<!-- alterado em 24/09/2010 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="R" value="100k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_100k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_100k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
		<component type="R" value="86.6k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_86.6k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_86.6k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
		<component type="R" value="82k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_82k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_82k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>

	
		<component type="R" value="56k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_56k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_56k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="R" value="51k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_51k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_51k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="R" value="47k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_47k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_47k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
	<component type="R" value="43.2k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_43.2k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-27" image="r_43.2k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="R" value="39k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_39k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_39k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="R" value="22k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_22k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_22k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="R" value="14.3k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_14.3k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-27" image="r_14.3k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="R" value="10k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_10k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-27" image="r_10k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	

	
		<!--ALTERACAO 14 SETEMBRO 2011 NOVOS COMPONENTES-->
		<component type="R" value="15k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_15k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_15k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="R" value="8.2k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_8.2k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-27" image="r_8.2k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="R" value="7.15k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_7.15k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_7.15k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	

	
	
	
	
	
		<!-- alterado em 17/01/2011 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->	
	<component type="R" value="5.6k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_5.6k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_5.6k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
		<component type="R" value="5.1k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_5.1k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_5.1k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	






	
	
	<component type="R" value="4.12k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_4.12k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-26" image="r_4.12k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="R" value="4.7k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_4.7k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_4.7k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="R" value="4.02k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_4.02k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_4.02k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
		<component type="R" value="3k9" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_3k9.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_3k9.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>

	
	<component type="R" value="2.55k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_2.55k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_2.55k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="R" value="2.7k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_2.7k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-27" image="r_2.7k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="R" value="3.0k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_3k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_3k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>

	<!-- alterado em 23/02/2011 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="R" value="3.3k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_3.3k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-26" image="r_3.3k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
	
	
			<component type="R" value="2k2" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_2k2.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_2k2.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		
	
	
		<component type="R" value="1.5k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_1.5k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-26" image="r_1.5k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="R" value="1.6k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_1.6k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_1.6k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="R" value="1.8k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_1.8k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_1.8k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<!-- alterado em 24/09/2010 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="R" value="1.2k" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="r_1.2k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-26" image="r_1.2k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
	
		<component type="R" value="1k" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_1k.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_1k.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
	
	<!-- alterado em 22/09/2010 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="R" value="560" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_560.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-26" image="r_560.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="R" value="470" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_470.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-26" image="r_470.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<!-- alterado em 23/02/2011 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="R" value="100" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_100.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-8" oy ="-26" image="r_100.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
			<component type="R" value="82" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_82.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_82.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
		<component type="R" value="56" pins="2">
		<rotations>
			<rotation ox="-26" oy ="-6" image="r_56.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-26" image="r_56.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="R" value="50" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-6" image="r_50.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="r_50.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
		</rotations>
	</component>

		<component type="POT" value="100k" pins="3">
		<rotations>
			<rotation ox="-16" oy ="-22" image="pot.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="0"  y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="POT" value="10k" pins="3">
		<rotations>
			<rotation ox="-16" oy ="-22" image="pot.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="0"  y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>


<!-- TYPE C -->

	<component type="CE" value="16u5" pins="2">
		<rotations>
			<rotation ox="-6" oy ="-26" image="ce_16u5.png" rot="0">
				<pins><pin x="0" y="13" /><pin x="13" y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="CE" value="15u" pins="2">
		<rotations>
			<rotation ox="-6" oy ="-26" image="ce_15u.png" rot="0">
				<pins><pin x="0" y="13" /><pin x="13" y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="CE" value="10u" pins="2">
		<rotations>
			<rotation ox="-6" oy ="-26" image="ce_10u.png" rot="0">
				<pins><pin x="0" y="13" /><pin x="13" y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="CE" value="4u7" pins="2">
		<rotations>
			<rotation ox="-6" oy ="-26" image="ce_4u7.png" rot="0">
				<pins><pin x="0" y="13" /><pin x="13" y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<!-- alterado condensador de 1u - 22 set 2010-->
	<component type="CE" value="1u" pins="2">
		<rotations>
			<rotation ox="-6" oy ="-26" image="ce_1u.png" rot="0">
				<pins><pin x="0" y="13" /><pin x="13" y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim do alterado-->

	
		<component type="C" value="0.22u" pins="2">
		<rotations>
			<rotation ox="-31" oy ="-23" image="c_0.22u.png" rot="0">
				<pins><pin x="-26" y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="C" value="0.1u" pins="2">
		<rotations>
			<rotation ox="-19" oy ="-24" image="c_0.1u.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
	<component type="C" value="100n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_100n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
	
		<!-- alterado em 17/01/2011 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="C" value="150n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_150n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
		<component type="C" value="56n" pins="2">
		<rotations>
			<rotation ox="-15" oy ="-24" image="c_56n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="C" value="47n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_47n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="C" value="33n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_33n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="C" value="22n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_22n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="C" value="15n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_15n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
		<component type="C" value="10n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_10n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="C" value="6.8n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_6.8n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
		<component type="C" value="2.2n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_2n2.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	

	<!-- alterado em 12/01/2011 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="C" value="1.8n" pins="2">
		<rotations>
			<rotation ox="-18" oy ="-24" image="c_1.8n.png" rot="0">
				<pins><pin x="-13" y="13" /><pin x="13"  y="13" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
				
	
	<component type="L" value="82m" pins="2">
		<rotations>
			<rotation ox="-20" oy ="-35" image="l_82m.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<!-- alterado em 23/02/2011 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="L" value="10m" pins="2">
		<rotations>
			<rotation ox="-20" oy ="-35" image="l_10m.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
		<!-- alterado em 23/02/2011 -->
	<!-- THIS IS NOT THE CORRECT PICTURE!!! -->
	<component type="L" value="1m" pins="2">
		<rotations>
			<rotation ox="-20" oy ="-35" image="l_1m.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	<!-- fim da alteração -->
	
	<!-- alterado bobina de 470u - 22 set 2010-->
	<component type="L" value="470u" pins="2">
		<rotations>
			<rotation ox="-20" oy ="-35" image="l_470u.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>	
	<!-- fim do alterado-->
	

	

	

	

	
		
	
	
	
	
	
		<component type="Q" value="2n3904" pins="3">
		<rotations>
			<rotation ox="-15" oy ="-13" image="q_2n3904.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="0"  y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<!-- FIM ALTERACAO 14 SETEMBRO 2011 -->

	
		<component type="Q" value="bf245" pins="3">
		<rotations>
			<rotation ox="-70" oy ="-48" image="bf245.png" rot="0">
				<pins><pin x="-65" y="13" /><pin x="65"  y="13" /><pin x="65"  y="-26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="D" value="1N4002" pins="2">
		<rotations>
			<rotation ox="-27" oy ="-7" image="d_1n4002.png" rot="0">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="d_1n4002.png" rot="90">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
			<rotation ox="-27" oy ="-7" image="d_1n4002.png" rot="180">
				<pins><pin x="26" y="0" /><pin x="-26"  y="0" /></pins>
			</rotation>
			<rotation ox="-7" oy ="-27" image="d_1n4002.png" rot="270">
				<pins><pin x="0" y="26" /><pin x="0" y="-26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="D" value="1N4148" pins="2">
		<rotations>
			<rotation ox="-29" oy ="-5" image="d_1n4148.png" rot="180">
				<pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-29" image="d_1n4148.png" rot="270">
				<pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>
			</rotation>
			<rotation ox="-29" oy ="-5" image="d_1n4148.png" rot="0">
				<pins><pin x="26" y="0" /><pin x="-26"  y="0" /></pins>
			</rotation>
			<rotation ox="-6" oy ="-29" image="d_1n4148.png" rot="90">
				<pins><pin x="0" y="26" /><pin x="0" y="-26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
	
	<component type="Q" value="bc547b" pins="3">
		<rotations>
			<rotation ox="-15" oy ="-13" image="q_bc547b.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="0"  y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>


	<component type="OP" value="UA741" pins="8">
		<rotations>
			<rotation ox="-18" oy ="-14" image="op.png" rot="0">
				<pins>
					<pin x="-13" y="26" />
					<pin x="0" y="26" />
					<pin x="13" y="26" />
					<pin x="26" y="26" />
					<pin x="26" y="-13" />
					<pin x="13" y="-13" />
					<pin x="0" y="-13" />
					<pin x="-13" y="-13" />
				</pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="OP" value="int1" pins="8">
		<rotations>
			<rotation ox="-18" oy ="-14" image="op.png" rot="0">
				<pins>
					<pin x="-13" y="26" />
					<pin x="0" y="26" />
					<pin x="13" y="26" />
					<pin x="26" y="26" />
					<pin x="26" y="-13" />
					<pin x="13" y="-13" />
					<pin x="0" y="-13" />
					<pin x="-13" y="-13" />
				</pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="OP" value="int2" pins="8">
		<rotations>
			<rotation ox="-46" oy ="-34" image="external_int1.png" rot="0">
				<pins>
					<pin x="0" y="26" />
					<pin x="-39" y="26" />
					<pin x="13" y="26" />
					<pin x="39" y="26" />
					<pin x="39" y="-13" />
					<pin x="26" y="-13" />
					<pin x="13" y="-13" />
					<pin x="26" y="26" />
				</pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="OP" value="int3" pins="8">
		<rotations>
			<rotation ox="-45" oy ="-27" image="ic16_unnamed.png" rot="0">
				<pins>
					<pin x="-39" y="13" />
					<pin x="-26" y="13" />
					<pin x="-26" y="-26" />
					<pin x="13" y="13" />
					<pin x="-39" y="-26" />
					<pin x="39" y="-26" />
					<pin x="0" y="-26" />
					<pin x="-13" y="-26" />
				</pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="XSWITCHOPEN" value="" pins="2">
		<rotations>
			<rotation ox="-8" oy ="-27" image="switch_opening.png" rot="0">
				<pins><pin x="0" y="-26" /><pin x="0"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="XSWITCHCLOSE" value="" pins="2">
		<rotations>
			<rotation ox="-8" oy ="-27" image="switch_closing.png" rot="0">
				<pins><pin x="0" y="-26" /><pin x="0"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="BLACKBOX" value="" pins="3">
		<rotations>
			<rotation ox="-16" oy ="-22" image="blackbox.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="0"  y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	
	

	

	
<!--	<component type="POT" value="127" pins="3">
		<rotations>
			<rotation ox="-16" oy ="-22" image="blackbox.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="0"  y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
	
	<component type="POT" value="0" pins="3">
		<rotations>
			<rotation ox="-16" oy ="-22" image="blackbox.png" rot="0">
				<pins><pin x="-13" y="26" /><pin x="0"  y="26" /><pin x="13"  y="26" /></pins>
			</rotation>
		</rotations>
	</component>
-->
	
</components>
"""

