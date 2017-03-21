import os
import shlex, subprocess

def create_bridge(br_name):
    try:
        res = subprocess.check_output('ovs-vsctl add-br ' + br_name, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print e.output
    
    res = subprocess.check_output('ovs-vsctl show', shell=True, stderr=subprocess.STDOUT)
    #print res
    if br_name in res:
        print 'Create bridge [%s] success.\n' %(br_name)
    else:
        print 'Create bridge [%s] failed.\n' %(br_name)
    
    
def connect_to_bridge(physical_eth, br_name, br_ip, autoactive=True):
    subprocess.call(['ovs-vsctl', 'del-port', br_name, physical_eth], stderr=subprocess.STDOUT)
    
    try:
        subprocess.check_output(['ovs-vsctl', 'add-port', br_name, physical_eth], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print 'config bridge failed:'
        print e.output
        return
    
    if autoactive:
        subprocess.call(['ifconfig', physical_eth, '0'], stderr=subprocess.STDOUT)
        subprocess.call(['ifconfig', br_name, 'up'], stderr=subprocess.STDOUT)
    
    if br_ip.strip():
        subprocess.call(['ifconfig', br_name, br_ip], stderr=subprocess.STDOUT)
        try:
            res = subprocess.check_output(['ifconfig', br_name], stderr=subprocess.STDOUT)
            if br_ip in res:
                print 'Create bridge IP [%s] success.\n' %(br_ip)
            else:
                print 'Create bridge IP [%s] failed.\n' %(br_ip)
        except subprocess.CalledProcessError as e:
            print 'config bridge IP failed:'
            print e.output
    

def config_bridge(br_name, physical_eth, br_ip):
    create_bridge(br_name)
    connect_to_bridge(physical_eth, br_name, br_ip)


if __name__ == '__main__':
    config_bridge('br_xxx', 'eno3', '192.168.255.111')