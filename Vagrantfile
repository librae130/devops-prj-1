Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.box_check_update = false
  config.vm.boot_timeout = 900

  boxes = [
    { name: "master",  ip: "192.168.56.10", mem: 2048 },
    { name: "node1",   ip: "192.168.56.11", mem: 4096 },
    { name: "node2",   ip: "192.168.56.12", mem: 3072 },
    { name: "control", ip: "192.168.56.9",  mem: 2048 },
  ]

  boxes.each do |b|
    config.vm.define b[:name] do |m|
      m.vm.hostname = b[:name]
      m.vm.network "private_network", ip: b[:ip]
      m.vm.provider "virtualbox" do |v|
        v.name   = b[:name]
        v.memory = b[:mem]
        v.cpus   = 2
      end

      m.vm.provision "shell", inline: <<-SHELL
        hostnamectl set-hostname #{b[:name]}
        mkdir -p /etc/netplan
        cat << 'EOF' > /etc/netplan/50-vagrant.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s8:
      addresses:
      - #{b[:ip]}/24
EOF
        chmod 600 /etc/netplan/50-vagrant.yaml
        netplan apply 2>/dev/null || true
        iptables -P FORWARD ACCEPT 2>/dev/null || true
      SHELL

      if b[:name] == "control"
        m.vm.provision "shell",
          privileged: false,
          inline: <<-SHELL
            set -e
            echo "== Running control VM bootstrap =="
            bash /vagrant/setup.sh
          SHELL
      end
    end
  end
end
