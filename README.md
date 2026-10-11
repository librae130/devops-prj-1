# Kubernetes lab with Vagrant + Ansible

This project creates a small Kubernetes test cluster using Vagrant and Ansible.

The environment is made of 3 VMs:

- control: the Ansible management VM
- master: the Kubernetes control plane
- node1: a worker node

The important part is that the setup script is meant to run inside the control VM, not on your host machine.

The Vagrant setup is configured so the `control` VM automatically runs the bootstrap script after `vagrant up` completes.

## What this repo does

- brings up the VMs with Vagrant
- installs Ansible on the control VM
- copies the SSH keys for master and node1 into the control VM
- sets the default Ansible config and project directory
- installs the required Ansible roles/collections
- tests connectivity to the cluster with Ansible
- provisions the Kubernetes cluster with the playbook in `playbooks/cluster.yml`

## Prerequisites

Install these on your host machine:

- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- [Vagrant](https://developer.hashicorp.com/vagrant/downloads)
- Git

A Windows host can work, but the usual workflow is to use a shell such as Git Bash, PowerShell, or WSL.

## 1) Start the VMs

From the project root:

```bash
vagrant up
```

This creates the `control`, `master`, and `node1` VMs defined in the `Vagrantfile`.

If the build stops or fails midway, run:

```bash
vagrant provision
```

## 2) Enter the control VM

Run this from the project root on your host:

```bash
vagrant ssh control
```

Once inside the control VM, you are in the Ansible management environment.

## 3) Control VM bootstrap

The `control` VM is set up to run the bootstrap automatically after the machines are created:

```bash
vagrant up
```

This triggers the setup script inside the control VM:

```bash
bash /vagrant/setup.sh
```

If you want to run it again manually later, do this from inside the control VM:

```bash
bash /vagrant/setup.sh
```

This script will:

- install Ansible if needed
- copy the SSH keys for `master` and `node1`
- export `ANSIBLE_CONFIG=/vagrant/ansible.cfg`
- `cd` into `/vagrant`
- install roles/collections from `requirements.yml`
- ping the cluster hosts via Ansible

If the script is run again, it is safe to do so.

## 4) Provision the Kubernetes cluster

From inside the control VM, still in `/vagrant`, run:

```bash
ansible-playbook -i inventory.ini playbooks/cluster.yml
```

You can also test host connectivity first:

```bash
ansible -i inventory.ini k8s -m ping
```

## 5) Verify the cluster

After the playbook finishes, from the control VM you can check cluster status:

```bash
kubectl get nodes
kubectl get pods -A
```

If the kube config is already set, this should work from the control VM. The cluster config is set up for the `vagrant` user on the master VM and shared by the playbook logic.

## Useful commands

From your host machine:

```bash
vagrant status
vagrant halt
vagrant destroy
```

From the control VM:

```bash
cd /vagrant
ansible -i inventory.ini k8s -m ping
ansible-playbook -i inventory.ini playbooks/cluster.yml
kubectl get nodes
```

## Project files

- `Vagrantfile`: defines the `control`, `master`, and `node1` VMs
- `setup.sh`: intended for the control VM only
- `inventory.ini`: Ansible inventory for the cluster
- `playbooks/cluster.yml`: cluster provisioning playbook
- `vars/main.yml`: variables used by the playbook
- `requirements.yml`: Ansible role and collection requirements

## Notes

- The script in `setup.sh` is not meant to run on your laptop or on the cluster nodes directly.
- It is meant to run from inside the `control` VM.
- `vagrant up` will trigger the bootstrap automatically for the control VM.
- If you rebuild the VMs or destroy them, the script will run again and the SSH keys will be refreshed automatically.
