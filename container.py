import sys
import time
import random
import commands

def config_veth(container_name, br_name, container_veth=None):
    cmd = "docker inspect -f '{{.State.Pid}}' " + container_name
    nspid = commands.run(cmd).replace('\n', '')

    veth_name_host = container_name + "-" + br_name
    print "veth_name_host:" + veth_name_host

    veth_name_peer = "if." + str(time.time())[-1:13].replace('.', '')
    print "veth_name_peer:" + veth_name_peer

    cmd = "ip link del " + veth_name_host
    commands.run(cmd)

    cmd = "ip link add " + veth_name_peer + " type veth peer name " + veth_name_host
    res = commands.run(cmd).replace('\n', '')
    if 'long' in res:
        sys.exit(1)

    cmd = "ovs-vsctl del-port " + br_name + " " + veth_name_host
    commands.run(cmd)

    cmd = "ovs-vsctl add-port " + br_name + " " + veth_name_host
    commands.run(cmd)

    cmd = "ifconfig " + veth_name_host + " up"
    commands.run(cmd)

    random.seed()
    if container_veth == None:
        container_veth = "eth" + str(random.randint(1000, 10000))

    cmd = "ip link set dev " + veth_name_peer + " name " + container_veth + " netns " + nspid
    commands.run(cmd)

    #up veth in container
    cmd = "nsenter -t "+nspid+" -n " + " ip link set dev " + container_veth + " up"
    commands.run(cmd)

    return container_veth

def config_container(container_name, veth_name, ip):
    cmd = "docker inspect -f '{{.State.Pid}}' " + container_name
    nspid = commands.run(cmd).replace('\n', '')

    cmd = "nsenter -t "+nspid+" -n "  + " ip addr add " + ip + " dev " + veth_name
    commands.run(cmd)

def config_container_vlan(container_name, veth_name, ip, route, vlan_id):
    cmd = "docker inspect -f '{{.State.Pid}}' " + container_name
    nspid = commands.run(cmd).replace('\n', '')

    cmd = "docker exec -t -i " + container_name + " vconfig add " + veth_name + " " + vlan_id
    commands.run(cmd)

    iface =  veth_name + "." + vlan_id
    cmd = "nsenter -t "+nspid+" -n "  + " ip address add " + ip + " dev " + iface
    commands.run(cmd)

    cmd = "nsenter -t "+nspid+" -n "  + " ifconfig " + iface + " up"
    commands.run(cmd)

    cmd = "nsenter -t "+nspid+" -n "  + " ip route add " + route + " dev " + iface
    commands.run(cmd)

if __name__ == '__main__':
    container_name = "test"
    veth = config_veth(container_name, "br-rd")
    config_container(container_name, veth, "192.168.255.100/24")
    config_container_vlan(container_name, veth, "192.168.255.100/24", "192.168.255.0/24", "100")