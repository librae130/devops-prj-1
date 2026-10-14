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

## 6) Deploy Online Boutique (Part 3)

Deploy the 11 Online Boutique microservices using Helm and Ansible:

```bash
ansible-playbook -i inventory.ini playbooks/deploy.yml
```

This applies three essential overrides without modifying upstream chart code:
1. `common.appReplicas: 1` (low-resource environment).
2. `frontendservice.overrides.serviceType: NodePort` (assigns accessible port on 192.168.56.11).
3. `checkoutservice.overrides.appName: checkoutservice` (fixes upstream duplicated key bug falling back to "servicename").

## 7) Automated Verification (Part 4)

Run automated assertions to verify cluster and application health:

```bash
ansible-playbook -i inventory.ini playbooks/verify.yml
```

This verifies:
- Both nodes are `Ready` on the private network (`192.168.56.x`).
- All 11 Deployments report available replicas.
- `checkoutservice` exists with the correct name (no `servicename`).
- Frontend service is `NodePort`.
- HTTP 200 storefront check returns `Online Boutique`.

Access the web store in your host browser at:
`http://192.168.56.11:<nodePort>/`

## 8) Master Playbook & Idempotency (Appendix C)

To provision the entire cluster and deploy the application in a single run:

```bash
ansible-playbook -i inventory.ini site.yml
```

To test idempotency (should result in `changed=0` on subsequent runs):

```bash
ansible-playbook -i inventory.ini site.yml
```

## 9) Teardown Application (Part 5)

To remove all 11 microservice Helm releases and the `microservice` namespace while keeping the Kubernetes cluster running:

```bash
ansible-playbook -i inventory.ini playbooks/teardown.yml
```

To stop VMs:
```bash
vagrant halt
```

To completely delete the environment:
```bash
vagrant destroy -f
```

## Snapshots for Live Demo

Milestones are captured as Vagrant snapshots:
- `01-cluster-ready`: Kubernetes cluster healthy, 0 microservices.
- `02-app-complete`: All 11 microservices running and verified.

Restore commands:
```powershell
vagrant snapshot restore master 02-app-complete
vagrant snapshot restore node1 02-app-complete
vagrant snapshot restore control 02-app-complete
```
Convenience Windows batch scripts are provided in the parent folder:
- `1_bat_may.bat`: Power on VMs (`vagrant up`)
- `2_tat_may.bat`: Safely power off VMs (`vagrant halt`)
- `3_khoi_phuc_demo.bat`: Restore snapshot `02-app-complete` and launch browser

## Project files

- `Vagrantfile`: defines `control`, `master`, and `node1` VMs
- `setup.sh`: bootstrap script for `control` VM
- `inventory.ini`: Ansible inventory for cluster nodes
- `site.yml`: master playbook (imports `cluster.yml` then `deploy.yml`)
- `playbooks/cluster.yml`: cluster provisioning playbook (Part 2)
- `playbooks/deploy.yml`: Helm microservice deployment playbook (Part 3)
- `playbooks/verify.yml`: automated verification assertion playbook (Part 4)
- `playbooks/teardown.yml`: application teardown playbook (Part 5)
- `vars/main.yml`: cluster variables (Flannel, kubelet, versions)
- `vars/microservices.yml`: Helm release configuration & values overrides
- `requirements.yml`: required Ansible roles and collections
- `recap.txt`: playbook execution logs for first run and idempotency tests
- `screenshots/`: verified application flow evidence screenshots

