# A current issue
The current issue that I'm trying to fix is that the raspberry pi is slow, so 
it is barely taking 10fps with a python script.


# Raspberry Pi specs
using python wrappers for the btferret cli

## Camera Pi
* should listen to mesh network messages via btferret (`sudo ./btferret`,
  followed with the appropriate commands to start listengin
* When the btferret cli tool recieves a mesh message with a "GET ~some date and
  time", it should try to send a file (jpg) via the `f` command in the btferret cli
  tool.

## Master Pi
* It should poll a python webserver for when to send GET to mesh network
* When the polling returns a new image query (a date and time), it should propagate a GET with
  that same date and time
* For every file that it got from that, it sends them to the same python
  webserver (backend)
