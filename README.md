# pfd-driver

PiFaceDigital driver

This device can't handle multiple executables connecting to it at the same time,
so we use one service and then sub-services use this as a lower level API.

## Message Spec

Format: \<channel> "message"

**Inputs**

* \<pfd.inputs> "*"
  * Triggers a request for status of all of the inputs
* \<pfd.inputs> "[0:7]"
  * Triggers a request for status for the specified input

* \<pfd.outputs.[0:7]> "on"
  * Turn on the output at index [0:7]
* \<pfd.outputs.[0:7]> "off"
  * Turn off the output at index [0:7]

**Outputs**

* \<pfd.input.[0:7]> "input.[0:7].on"
  * The input at index [0:7] has been connected
  * Triggered automatically
  * Also sent when an input is provided on \<pfd.inputs> channel, if the input is on
* \<pfd.input.[0:7]> "input.[0:7].off"
  * The input at index [0:7] has been disconnected
  * Triggered automatically
  * Also sent when an input is provided on \<pfd.inputs> channel, if the input is off

* \<pfd.output[0:7].status> "output.[0:7].on"
  * The output at index [0:7] has been turned on
* \<pfd.output[0:7].status> "output.[0:7].off"
  * The output at index [0:7] has been turned off