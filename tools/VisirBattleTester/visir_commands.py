import xml.dom.minidom as minidom

visir_login_request = """<protocol version="1.3">
  <login cookie="%s" keepalive="1"/>
</protocol>"""


visir_login_response = u"""<protocol version="1.3">
<login sessionkey="4f647e4292bcf7d381b4464be8ddfb82">
</login>
</protocol>
"""

def parse_login_response(response):
    try:
        xml_str  = response.commandstring
        dom_tree = minidom.parseString(xml_str)
        return dom_tree.getElementsByTagName('login')[0].getAttribute("sessionkey")
    except:
        raise Exception("Invalid response: %s" % response)

def parse_command_response(response):
    try:
        xml_str  = response.commandstring
        dom_tree = minidom.parseString(xml_str)
        return float(dom_tree.getElementsByTagName('dmm_result')[0].getAttribute("value"))
    except:
        raise Exception("Invalid response: %s" % response)

visir_request_11k = """<protocol version="1.3">
  <request sessionkey="%s">
    <circuit>
      <circuitlist>W_X A11 DMM_VHI
W_X DMM_VLO A3
R_X A7 A11 1k
R_X A3 A7 10k</circuitlist>
    </circuit>
    <multimeter>
      <dmm_function value="resistance"/>
      <dmm_resolution value="3.5"/>
      <dmm_range value="10"/>
    </multimeter>
    <functiongenerator>
      <fg_waveform value="sine"/>
      <fg_frequency value="1000"/>
      <fg_amplitude value="0.5"/>
      <fg_offset value="0"/>
    </functiongenerator>
    <oscilloscope>
      <osc_autoscale value="0"/>
      <horizontal>
        <horz_samplerate value="500"/>
        <horz_refpos value="50"/>
        <horz_recordlength value="500"/>
      </horizontal>
      <channels>
        <channel number="1">
          <chan_enabled value="1"/>
          <chan_coupling value="dc"/>
          <chan_range value="1"/>
          <chan_offset value="0"/>
          <chan_attenuation value="1.0"/>
        </channel>
        <channel number="2">
          <chan_enabled value="1"/>
          <chan_coupling value="dc"/>
          <chan_range value="1"/>
          <chan_offset value="0"/>
          <chan_attenuation value="1.0"/>
        </channel>
      </channels>
      <trigger>
        <trig_source value="channel 1"/>
        <trig_slope value="positive"/>
        <trig_coupling value="dc"/>
        <trig_level value="0"/>
        <trig_mode value="autolevel"/>
        <trig_timeout value="1.0"/>
        <trig_delay value="0"/>
      </trigger>
      <measurements>
        <measurement number="1">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
        <measurement number="2">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
        <measurement number="3">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
      </measurements>
    </oscilloscope>
    <dcpower>
      <dc_outputs>
        <dc_output channel="6V+">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
        <dc_output channel="25V+">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
        <dc_output channel="25V-">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
      </dc_outputs>
    </dcpower>
  </request>
</protocol>"""

visir_request_900 = """<protocol version="1.3">
  <request sessionkey="%s">
    <circuit>
      <circuitlist>W_X A11 DMM_VHI
W_X DMM_VLO A7
R_X A7 A11 1k
R_X A7 A11 10k</circuitlist>
    </circuit>
    <multimeter>
      <dmm_function value="resistance"/>
      <dmm_resolution value="3.5"/>
      <dmm_range value="10"/>
    </multimeter>
    <functiongenerator>
      <fg_waveform value="sine"/>
      <fg_frequency value="1000"/>
      <fg_amplitude value="0.5"/>
      <fg_offset value="0"/>
    </functiongenerator>
    <oscilloscope>
      <osc_autoscale value="0"/>
      <horizontal>
        <horz_samplerate value="500"/>
        <horz_refpos value="50"/>
        <horz_recordlength value="500"/>
      </horizontal>
      <channels>
        <channel number="1">
          <chan_enabled value="1"/>
          <chan_coupling value="dc"/>
          <chan_range value="1"/>
          <chan_offset value="0"/>
          <chan_attenuation value="1.0"/>
        </channel>
        <channel number="2">
          <chan_enabled value="1"/>
          <chan_coupling value="dc"/>
          <chan_range value="1"/>
          <chan_offset value="0"/>
          <chan_attenuation value="1.0"/>
        </channel>
      </channels>
      <trigger>
        <trig_source value="channel 1"/>
        <trig_slope value="positive"/>
        <trig_coupling value="dc"/>
        <trig_level value="0"/>
        <trig_mode value="autolevel"/>
        <trig_timeout value="1.0"/>
        <trig_delay value="0"/>
      </trigger>
      <measurements>
        <measurement number="1">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
        <measurement number="2">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
        <measurement number="3">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
      </measurements>
    </oscilloscope>
    <dcpower>
      <dc_outputs>
        <dc_output channel="6V+">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
        <dc_output channel="25V+">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
        <dc_output channel="25V-">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
      </dc_outputs>
    </dcpower>
  </request>
</protocol>
"""

visir_request_1k = """<protocol version="1.3">
  <request sessionkey="%s">
    <circuit>
      <circuitlist>W_X A11 DMM_VHI
W_X DMM_VLO A7
R_X A7 A11 1k</circuitlist>
    </circuit>
    <multimeter>
      <dmm_function value="resistance"/>
      <dmm_resolution value="3.5"/>
      <dmm_range value="10"/>
    </multimeter>
    <functiongenerator>
      <fg_waveform value="sine"/>
      <fg_frequency value="1000"/>
      <fg_amplitude value="0.5"/>
      <fg_offset value="0"/>
    </functiongenerator>
    <oscilloscope>
      <osc_autoscale value="0"/>
      <horizontal>
        <horz_samplerate value="500"/>
        <horz_refpos value="50"/>
        <horz_recordlength value="500"/>
      </horizontal>
      <channels>
        <channel number="1">
          <chan_enabled value="1"/>
          <chan_coupling value="dc"/>
          <chan_range value="1"/>
          <chan_offset value="0"/>
          <chan_attenuation value="1.0"/>
        </channel>
        <channel number="2">
          <chan_enabled value="1"/>
          <chan_coupling value="dc"/>
          <chan_range value="1"/>
          <chan_offset value="0"/>
          <chan_attenuation value="1.0"/>
        </channel>
      </channels>
      <trigger>
        <trig_source value="channel 1"/>
        <trig_slope value="positive"/>
        <trig_coupling value="dc"/>
        <trig_level value="0"/>
        <trig_mode value="autolevel"/>
        <trig_timeout value="1.0"/>
        <trig_delay value="0"/>
      </trigger>
      <measurements>
        <measurement number="1">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
        <measurement number="2">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
        <measurement number="3">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
      </measurements>
    </oscilloscope>
    <dcpower>
      <dc_outputs>
        <dc_output channel="6V+">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
        <dc_output channel="25V+">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
        <dc_output channel="25V-">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
      </dc_outputs>
    </dcpower>
  </request>
</protocol>
"""

visir_request_10k = """<protocol version="1.3">
  <request sessionkey="%s">
    <circuit>
      <circuitlist>W_X A11 DMM_VHI
W_X DMM_VLO A7
R_X A7 A11 10k</circuitlist>
    </circuit>
    <multimeter>
      <dmm_function value="resistance"/>
      <dmm_resolution value="3.5"/>
      <dmm_range value="10"/>
    </multimeter>
    <functiongenerator>
      <fg_waveform value="sine"/>
      <fg_frequency value="1000"/>
      <fg_amplitude value="0.5"/>
      <fg_offset value="0"/>
    </functiongenerator>
    <oscilloscope>
      <osc_autoscale value="0"/>
      <horizontal>
        <horz_samplerate value="500"/>
        <horz_refpos value="50"/>
        <horz_recordlength value="500"/>
      </horizontal>
      <channels>
        <channel number="1">
          <chan_enabled value="1"/>
          <chan_coupling value="dc"/>
          <chan_range value="1"/>
          <chan_offset value="0"/>
          <chan_attenuation value="1.0"/>
        </channel>
        <channel number="2">
          <chan_enabled value="1"/>
          <chan_coupling value="dc"/>
          <chan_range value="1"/>
          <chan_offset value="0"/>
          <chan_attenuation value="1.0"/>
        </channel>
      </channels>
      <trigger>
        <trig_source value="channel 1"/>
        <trig_slope value="positive"/>
        <trig_coupling value="dc"/>
        <trig_level value="0"/>
        <trig_mode value="autolevel"/>
        <trig_timeout value="1.0"/>
        <trig_delay value="0"/>
      </trigger>
      <measurements>
        <measurement number="1">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
        <measurement number="2">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
        <measurement number="3">
          <meas_channel value="channel 1"/>
          <meas_selection value="none"/>
        </measurement>
      </measurements>
    </oscilloscope>
    <dcpower>
      <dc_outputs>
        <dc_output channel="6V+">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
        <dc_output channel="25V+">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
        <dc_output channel="25V-">
          <dc_voltage value="0"/>
          <dc_current value="0.5"/>
        </dc_output>
      </dc_outputs>
    </dcpower>
  </request>
</protocol> 
"""
