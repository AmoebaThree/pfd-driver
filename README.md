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

**Outputs**

* \<pfd.input.[0:7]> "input.[0:7].on"
  * The input at index [0:7] has been connected
  * Triggered automatically
  * Also sent when an input is provided on \<pfd.inputs> channel, if the input is on
* \<pfd.input.[0:7]> "input.[0:7].off"
  * The input at index [0:7] has been disconnected
  * Triggered automatically
  * Also sent when an input is provided on \<pfd.inputs> channel, if the input is off