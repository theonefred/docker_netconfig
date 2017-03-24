import container

if __name__ == '__main__':
    veth = container.config_veth("test_container", "br-rd")
    container.config_container("test_container", veth, "192.168.255.100/24")
