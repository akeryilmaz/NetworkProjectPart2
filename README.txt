----- GROUP MEMBERS -----

Buğra Aker Yılmaz, 2167617
Ekin Tire, 2167369

----- EXPERIMENT 1 -----

Run the following commands to remove any packet loss configuration that might have left from the past:

s:
- sudo tc qdisc del dev eth1 root
- sudo tc qdisc del dev eth2 root
- sudo tc qdisc del dev eth3 root

r3:
- sudo tc qdisc del dev eth1 root
- sudo tc qdisc del dev eth2 root
- sudo tc qdisc del dev eth3 root

d:
- sudo tc qdisc del dev eth1 root
- sudo tc qdisc del dev eth2 root
- sudo tc qdisc del dev eth3 root

For the first experiment scripts to be run successfully, they must be executed in the following order, with the given bash commands:
1. $ python3 r3/r3_forward.py
2. $ python3 d/d_receiver.py 1
3. $ python3 s/s_sender.py 1

After the experiment ends, the scripts running on s and d should be terminated by itself.
Please stop the script running on r3 before moving on to the next experiment by pressing CTRL+C until the script stops its execution.

----- EXPERIMENT 2 -----

We have already prepared 3 bash scripts for each node containing the packet loss configurations (5%, 15% and 38%).
Each of these bash scripts contain "tc qdisc add dev <INTERFACE> root netem loss <LOSS_PERCENTAGE> delay 3ms" for each of their interfaces.

-- 5% Packet loss experiment --

Before starting the experiment with the 5% packet loss configuration, run the following bash scripts with the given commands:

d: $ sudo d/config.sh
r1: $ sudo r1/config.sh
r2: $ sudo r2/config.sh
s: $ sudo s/config.sh

Run the following bash commands in the following order:

1. r1: $ python3 r1/r1_forward.py
2. r2: $ python3 r2/r2_forward.py
3. d: $ python3 d/d_receiver.py 2
4: s: $ python3 s/s_sender.py 2

After the experiment ends, the scripts running on s and d should be terminated by themselves.
Please stop the scripts running on r1 & r2 before moving on to the next experiment by pressing CTRL+C until the scripts stops their execution.


-- 15% Packet loss experiment --

Before starting the experiment with the 15% packet loss configuration, run the following bash scripts with the given commands:

d: $ sudo d/config15.sh
r1: $ sudo r1/config15.sh
r2: $ sudo r2/config15.sh
s: $ sudo s/config15.sh

Run the following bash commands in the following order:

1. r1: $ python3 r1/r1_forward.py
2. r2: $ python3 r2/r2_forward.py
3. d: $ python3 d/d_receiver.py 2
4: s: $ python3 s/s_sender.py 2

After the experiment ends, the scripts running on s and d should be terminated by themselves.
Please stop the scripts running on r1 & r2 before moving on to the next experiment by pressing CTRL+C until the scripts stops their execution.


-- 38% Packet loss experiment --

Before starting the experiment with the 38% packet loss configuration, run the following bash scripts with the given commands:

d: $ sudo d/config38.sh
r1: $ sudo r1/config38.sh
r2: $ sudo r2/config38.sh
s: $ sudo s/config38.sh

Run the following bash commands in the following order:

1. r1: $ python3 r1/r1_forward.py
2. r2: $ python3 r2/r2_forward.py
3. d: $ python3 d/d_receiver.py 2
4: s: $ python3 s/s_sender.py 2

After the experiment ends, the scripts running on s and d should be terminated by themselves.