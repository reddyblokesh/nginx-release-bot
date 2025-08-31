# 🌀 NGINX Release Bot

This tool automates updating the **NGINX Ingress Helm chart** used in our Kubernetes deployments.  
It pulls the upstream chart from the official NGINX OCI registry, renames it with our NIC versioning scheme, and selectively updates only the files we care about in `ml-nginx-ingress`.

---

## ✨ Features
- Pulls Helm chart from:  
  `oci://ghcr.io/nginx/charts/nginx-ingress`
- Renames the chart with the NIC version (e.g., `nginx-oss-5.1.1`)
- Updates only these files in `charts/ml-nginx-ingress`:
  - `templates/`
  - `.helmignore`
  - `Chart.yaml`
  - `README.md`
  - `values.yaml`
  - `values-icp.yaml`
  - `values-nsm.yaml`
  - `values-plus.yaml`
- Preserves local customizations
- Works with CLI arguments or interactive prompts
- Logs every action clearly

---

## ⚙️ Requirements
- Python **3.8+**
- [Helm CLI](https://helm.sh/docs/intro/install/) installed and in `$PATH`
- Internet access to pull charts from the OCI registry

---

## 🚀 Usage

### Run with explicit versions
```bash
python update_nginx_chart.py --nic-version 5.1.1 --chart-version 2.2.2
