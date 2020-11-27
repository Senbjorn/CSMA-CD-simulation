# CSMA-CD-simulation
In this project we simulate behavior of N stations which are trying to<br>
transmit a Frame via CSMA/CD protocol<br>

### Prerequisites
* python 3.7

### How to run the simulation
To run the script you need to type the following in the terminal:<br>
python simulation.py \<n_stations\> \<max_iter\> \<mode\>

* n_stations - number of stations
* max_iter - maximum number of steps
* mode - printing mode (0 - "simple", 1 - "extended")

### Details
In **simple** mode the output is **time_step** and **simulation_time** of<br>
successful write opertations.
In **extended** mode read, write and collision events are reported.
