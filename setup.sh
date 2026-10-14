#!/bin/bash
# Run it INSIDE control, after `vagrant up`:
#     bash /vagrant/setup.sh
# Safe to run again. Run it again after every `vagrant destroy` (the SSH keys change).

set -e

echo "== 1/4 Installing Ansible (skipped if already installed) =="
if ! command -v ansible >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y software-properties-common git
  sudo add-apt-repository --yes --update ppa:ansible/ansible
  sudo apt-get install -y ansible
fi
ansible --version | head -1

echo "== 2/4 Copying SSH keys for master and node1 =="
mkdir -p ~/keys
for h in master node1 node2; do
  src="/vagrant/.vagrant/machines/$h/virtualbox/private_key"
  if [ ! -f "$src" ]; then
    echo "ERROR: $src not found. Did 'vagrant up' finish for $h? Is /vagrant mounted?"
    exit 1
  fi
  cp "$src" ~/keys/${h}_key
done
chmod 600 ~/keys/*

echo "== 3/4 Pointing Ansible at the project config =="
grep -q 'ANSIBLE_CONFIG=/vagrant/ansible.cfg' ~/.bashrc || echo 'export ANSIBLE_CONFIG=/vagrant/ansible.cfg' >> ~/.bashrc
grep -q '^cd /vagrant$' ~/.bashrc || echo 'cd /vagrant' >> ~/.bashrc
export ANSIBLE_CONFIG=/vagrant/ansible.cfg
cd /vagrant

echo "== 4/4 Installing Ansible roles/collections and testing the connection =="
ansible-galaxy install -r requirements.yml
ansible k8s -m ping
