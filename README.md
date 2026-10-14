# VNUHCM - University of Science
## Faculty of Information Technology — CS433 Advanced DevOps
### Project 1: Automated Kubernetes Cluster Provisioning & Online Boutique Deployment

**Group Members:**
- **Kiều Duy Hiếu** — Student ID: **23127365**
- **Đỗ Hiếu Quang** — Student ID: **23127537**

**Repository Branch:** `feat/part-3-4-5-deploy-verify-teardown`  
**Target Score:** 100 / 100 Marks (Full Rubric Coverage + Appendix Extensions)

---

## 1. System Requirements & Architecture

### 1.1 Host Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux.
- **VirtualBox:** 7.0 or newer ([Download](https://www.virtualbox.org/wiki/Downloads)).
- **Vagrant:** 2.3 or newer ([Download](https://developer.hashicorp.com/vagrant/downloads)).
- **Git:** Recent version.
- **Hardware Resources (Crucial):**
  - **RAM:** Minimum **16 GB RAM** recommended on host (total VM allocation is ~11.5 GB). Close heavy background applications before running.
  - **Disk Space:** At least 25 GB free disk space.
  - **CPU:** 4 physical cores (8 threads) or higher.

### 1.2 Multi-Node Cluster Topology (4 Virtual Machines)
All nodes run Ubuntu Jammy 22.04 LTS on the private network `192.168.56.0/24`:
| VM Name | Role | IP Address | vCPU | RAM | Key Services / Responsibilities |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `control` | Ansible Control Node | `192.168.56.9` | 2 | 2048 MB | Ansible Engine 2.16+, Helm 3, auto-bootstrap script |
| `master` | K8s Control Plane | `192.168.56.10` | 2 | 2048 MB | `kube-apiserver`, `etcd`, `controller-manager`, `scheduler` |
| `node1` | K8s Worker 1 | `192.168.56.11` | 2 | 4096 MB | `containerd`, `kubelet`, `kube-proxy`, `ingress-nginx` NodePort 30080 |
| `node2` | K8s Worker 2 | `192.168.56.12` | 2 | 3072 MB | Multi-worker failover, PodDisruptionBudget, node drain target |

---

## 2. Quick Start Guide (Step-by-Step)

### Step 1: Clone Repository
Clone the repository and switch to the production feature branch:
```bash
git clone -b feat/part-3-4-5-deploy-verify-teardown https://github.com/librae130/devops-prj-1.git
cd devops-prj-1
```

### Step 2: Provision Virtual Machines
From the host machine project root, boot all 4 VMs with Vagrant:
```bash
vagrant up
```
*Note: This automatically provisions `master`, `node1`, `node2`, and then `control`. During `control` bootstrap, `/vagrant/setup.sh` installs Ansible, configures SSH keys, and installs required Ansible collections.*

### Step 3: Enter the Ansible Control Node
```bash
vagrant ssh control
```
*(You are now inside `/vagrant` inside the `control` VM).*

### Step 4: Execute Master Deployment (`site.yml`)
Run the master playbook to provision the entire Kubernetes cluster, install addons, and deploy the 11 Online Boutique microservices:
```bash
ansible-playbook -i inventory.ini site.yml
```

### Step 5: Execute Automated Verification Suite
Run the 7-check automated assertion suite:
```bash
ansible-playbook -i inventory.ini playbooks/verify.yml
```
You should see:
```text
======================================================================
ALL VERIFICATION CHECKS PASSED (7/7)
======================================================================
✓ Check 1: Nodes are Ready on private network (192.168.56.x)
✓ Check 2: All 11 Deployments are Available (minimum replicas ready)
✓ Check 3: checkoutservice is correctly named (no 'servicename' bug)
✓ Check 4: frontend is ClusterIP and Ingress exists
✓ Check 5: Ingress routing passed (Positive HTTP 200, Negative HTTP 404)
✓ Check 6: Liveness/Readiness probes and resource limits verified (Rubric 5)
✓ Check 7: PodDisruptionBudgets (PDB) verified on 4 core services (Rubric 6)
```

---

## 3. Accessing the Storefront

The storefront is routed via **Ingress Controller (`ingress-nginx`)** exposed on NodePort `30080`.

1. On your **Host Machine**, edit the hosts file:
   - **Windows:** `C:\Windows\System32\drivers\etc\hosts` (run Notepad as Administrator).
   - **Linux / macOS:** `/etc/hosts` (`sudo nano /etc/hosts`).
2. Add the following entry:
   ```text
   192.168.56.11 boutique.local
   ```
3. Open your browser and navigate to:
   👉 **`http://boutique.local:30080/`**
4. Browse products, add items to the cart, and complete an order to verify end-to-end functionality!

---

## 4. Day-2 Operations & Rubric Demonstrations

From inside the `control` VM (`/vagrant`):

### 4.1 Safe Application Scaling (Rubric 6)
Scale stateless microservices safely while protecting stateful components:
```bash
# Scale frontend to 2 replicas across node1 and node2
ansible-playbook -i inventory.ini playbooks/scale.yml -e "release=frontendservice replicas=2"

# Attempting to scale redis-cart is automatically blocked to prevent data loss (Appendix B):
ansible-playbook -i inventory.ini playbooks/scale.yml -e "release=rediscart replicas=2"
```

### 4.2 Node Drain & PodDisruptionBudget (PDB) Demonstration (Rubric 6)
Drain `node1` to migrate multi-replica workloads to `node2` while preserving continuous zero-downtime storefront availability:
```bash
ansible-playbook -i inventory.ini playbooks/drain.yml
```

### 4.3 Liveness Probe Self-Healing Restart (Rubric 5)
Demonstrate automated self-healing by injecting an unhealthy probe into `productcatalogservice`:
```bash
ansible-playbook -i inventory.ini playbooks/probe-demo.yml
```

### 4.4 Network Diagnosis Experiments (Rubric 2)
Test the two Vagrant networking traps and their automated recoveries:
```bash
# Trap 1: Flannel interface mismatch (enp0s3 NAT vs enp0s8 private)
ansible-playbook -i inventory.ini playbooks/experiments/net-trap1-flannel.yml

# Trap 2: Kubelet --node-ip binding trap
ansible-playbook -i inventory.ini playbooks/experiments/net-trap2-nodeip.yml
```

### 4.5 CI Values Linter (Rubric 3)
Scan all Helm values files for duplicate YAML keys and upstream defects:
```bash
bash scripts/lint-values.sh
```

### 4.6 Idempotency Test (Rubric 7)
Re-run `site.yml` on the live cluster. All worker tasks will report `changed=0`:
```bash
ansible-playbook -i inventory.ini site.yml
```

---

## 5. Teardown & Clean Up (Part 5)

### Remove Application Workloads (Keep Cluster)
```bash
ansible-playbook -i inventory.ini playbooks/teardown.yml
```

### Stop Virtual Machines (Save Disks)
```bash
exit            # Exit control VM to host
vagrant halt    # Power off all 4 VMs
```

### Completely Destroy Environment
```bash
vagrant destroy -f
```

---

## 6. Project Structure

```text
devops-prj-1/
├── Vagrantfile               # 4-VM topology definition (master, node1, node2, control)
├── setup.sh                  # Control VM bootstrap (Ansible, keys, galaxy)
├── inventory.ini             # Inventory defining master, node1, node2
├── site.yml                  # Master playbook orchestrating cluster, addons & deploy
├── requirements.yml          # Ansible roles & collections dependencies
├── recap.txt                 # Authentic PLAY RECAP outputs (first run & idempotency)
├── report.md                 # Full markdown technical report
├── report.pdf                # Compiled publication-ready PDF report
├── build_report.py           # Python + Headless Chrome PDF compiler
├── charts/
│   ├── microservice/         # Vendored microservice chart (0.1.0-ext.1)
│   └── redis/                # Vendored redis-cart chart
├── playbooks/
│   ├── cluster.yml           # Kubernetes cluster build (containerd, kubeadm, flannel)
│   ├── addons.yml            # Ingress-nginx & Metrics-server deployment
│   ├── deploy.yml            # Online Boutique 11 microservices deployment
│   ├── verify.yml            # 7-assertion automated verification suite
│   ├── scale.yml             # Safe scaling playbook with Redis protection
│   ├── drain.yml             # High-availability node drain & PDB test
│   ├── probe-demo.yml        # Self-healing liveness probe restart demo
│   └── experiments/          # Network diagnosis break/restore experiments
│       ├── net-trap1-flannel.yml
│       └── net-trap2-nodeip.yml
├── scripts/
│   └── lint-values.sh        # CI linter preventing duplicate keys & defects
├── vars/
│   ├── main.yml              # Global cluster variables
│   └── microservices.yml     # 11 microservice release configurations & overrides
└── screenshots/              # 4 transaction screenshots
```
