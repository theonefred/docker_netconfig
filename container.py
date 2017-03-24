import commands
import random

def config_veth(container_name, br_name):
    cmd = "docker inspect -f '{{.State.Pid}}' " + container_name
    nspid = commands.run(cmd)
    
    veth_name_host = "veth-" + container_name + "-" + br_name
    print "veth_name_host:" + veth_name_host

    veth_name_peer = "veth-" + container_name
    print "veth_name_peer:" + veth_name_peer
    
    cmd = "ip link del " + veth_name_host
    commands.run(cmd)

    cmd = "ip link add " + veth_name_peer + " type veth peer name " + veth_name_host
    commands.run(cmd)

    cmd = "ovs-vsctl del-port " + br_name + " " + veth_name_host
    commands.run(cmd)

    cmd = "ovs-vsctl add-port " + br_name + " " + veth_name_host
    commands.run(cmd)

    cmd = "ifconfig " + veth_name_host + " up"
    commands.run(cmd)

    random.seed()
    veth_name_container = "eth" + random.random(1, 1000)
    cmd = "ip link set dev " + veth_name_peer + " name " + veth_name_container + " netns " + nspid
    commands.run(cmd)

    #up veth in container
    cmd = "ip netns exec " + nspid + " ip link set dev " + veth_name_container + " up"
    commands.run(cmd)

    return veth_name_container

def config_container(container_name, veth_name, ip):
    cmd = "docker inspect -f '{{.State.Pid}}' " + container_name
    nspid = commands.run(cmd)

    cmd = "ip netns exec " + nspid + " ip addr add " + ip + " dev " + veth_name
    commands.run(cmd)


if __name__ == '__main__':
    veth = config_veth("test_container", "br-rd")
    config_container("test_container", veth, "192.168.255.100/24")