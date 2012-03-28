#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

vt_measure_server_addr = "130.206.138.35:8080"
vt_measure_server_target = "/measureserver"
vt_base_url = """https://weblab-visir.deusto.es/electronics/"""
vt_login_url = """https://weblab-visir.deusto.es/electronics/index.php?sel=login_check"""
vt_login_email = "guest"
vt_login_password = "guest"

vt_client_url = "../../weblab/web/visir/loader.swf"

vt_debug_prints = False

# 
# Uncomment these two lines to enable the student mode with a given configuration
# 
# If you want to add other examples, try clicking on "save" circuit in VISIR, and place the .cir content here.
# 
# vt_teacher = False
# vt_not_savedata = \
"""
<save>
	<instruments+list="breadboard/breadboard.swf|multimeter/multimeter.swf|functiongenerator/functiongenerator.swf|oscilloscope/oscilloscope.swf|tripledc/tripledc.swf"+/>
	<multimeter+/>
		<circuit>
			<circuitlist>
				<component>R+1.6k+52+26+0</component>
				<component>R+2.7k+117+26+0</component>
				<component>R+10k+182+78+0</component>
				<component>R+10k+182+52+0</component>
				<component>R+10k+182+26+0</component>
				<component>C+56n+247+39+0</component>
				<component>C+56n+247+91+0</component>
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
