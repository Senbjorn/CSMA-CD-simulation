# CSMA-CD-simulation
In this project we simulate behavior of several stations which are trying to<br>
transmit a Frame via CSMA/CD protocol<br> 
One station is trying to transmit a single frame and then is running only for reading<br>
frames from other stations.

### Features
* used non-blocking socktes
* implemented CSMA/CD protocol
* we send one byte at a time but not a bit
* full Ethernet frame with crc32 verification
* collision detection
* addaptive wait time after a collision

### Future work
* add message transport delay
* add address verification
* add more functionality for testing

### Prerequisites
* python 3.7

### How to run the simulation
First, run bus.py wich is a medium for communication between stations
$ python bus.py \<port\> \<simulation_time\> \<max_time\>
* **port** - port were the bus server is running
* **simulation_time** - time per one byte
* **max_time** - maximum working time

Second, run station.py which is a station which is trying to transmit a frame.
$ python station.py \<port\> \<max_time\> \<messag\>
* **port** - port were the bus server is running
* **max_time** - maximum working time
* **message** - message to be sent

Then you can try to set **simulation_time** to 1.0 and run several **stations**<br>
In different terminal windows at the same time you will see some collisions<br>
and then message reading<br><br>

Use convenience test.sh script<br>
$ bash test.sh \<port\> \<n_stations\> \<station_time\> \<output_dir\>
* **port** - port were the bus server is running
* **n_stations** - number of stations
* **station_time** - working time of a station. Server is running for 5 seconds longer
* **output_dir** - directory were all logs will be stored