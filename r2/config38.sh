tc qdisc del dev eth1 root
tc qdisc del dev eth2 root
tc qdisc del dev eth3 root
tc qdisc del dev eth4 root
tc qdisc add dev eth1 root netem loss 38% delay 3ms
tc qdisc add dev eth2 root netem loss 38% delay 3ms
tc qdisc add dev eth3 root netem loss 38% delay 3ms
tc qdisc add dev eth4 root netem loss 38% delay 3ms
