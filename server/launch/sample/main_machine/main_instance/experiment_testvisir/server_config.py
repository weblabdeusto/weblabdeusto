#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-

vt_measure_server_addr = "130.206.138.35:8080"
vt_measure_server_target = "/measureserver"
vt_base_url = """https://weblab-visir.deusto.es/"""
vt_login_url = """https://weblab-visir.deusto.es/electronics/student.php"""
#vt_login_url = """https://weblab-visir.deusto.es/electronics/index.php?sel=login"""
vt_login_email = "guest"
vt_login_password = "guest"

vt_client_url = "visir/loader.swf"

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

