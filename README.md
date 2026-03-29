# Metaflow × Nomad — GSoC 2026 Exploration

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Nomad](https://img.shields.io/badge/HashiCorp-Nomad_v1.11.3-00CA8E?logo=hashicorp&logoColor=white)
![Metaflow](https://img.shields.io/badge/Metaflow-Integration-orange)
![GSoC](https://img.shields.io/badge/GSoC-2026-4285F4?logo=google&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> **GSoC 2026 Application Repository**
> Hands-on exploration of the Metaflow + Nomad integration — from job submission to log streaming to retry handling.
> Built by [@Talha8899](https://github.com/Talha8899) for the [Metaflow Nomad Integration](https://summerofcode.withgoogle.com/) project under **Outerbounds/Netflix**.

---

## 🎯 The Problem This Solves

Metaflow supports several compute backends, but **HashiCorp Nomad is missing**:

| Decorator     | Backend              | Status             |
|---------------|----------------------|--------------------|
| `@kubernetes` | Kubernetes clusters  | ✅ Exists          |
| `@batch`      | AWS Batch            | ✅ Exists          |
| `@slurm`      | HPC Slurm clusters   | ✅ Exists          |
| `@nomad`      | HashiCorp Nomad      | ❌ **This project** |

Many organizations run Nomad instead of Kubernetes — particularly those already invested in the HashiCorp ecosystem (Vault, Consul, Terraform). Without a `@nomad` decorator, these teams cannot use Metaflow today.

This repository explores every component of that missing integration before building the production extension.

---

## 📁 Repository Structure

```
Metaflow-nomad-gsoc-2026/
├── metaflow_nomad/
│   ├── __init__.py                  # Package initializer
│   ├── job_run.py                   # Job submission via Nomad HTTP API
│   ├── nomad_structure.py           # Nomad job specification structure
│   ├── result_nomad.py              # Result fetching via allocations API
│   ├── retry_decorator.py           # Retry logic for failed job executions
│   ├── stepsflow_metaflow.py        # Metaflow flow + StepDecorator lifecycle
│   └── submit_job_fetch_results.py  # End-to-end: submit → monitor → fetch
├── firstjob.hcl                     # Sample Nomad job configuration (HCL)
├── logger_logic.py                  # Custom logging utility for job tracking
├── LICENSE
└── README.md
```

---

## 🔬 What Each File Explores

### `firstjob.hcl` — Nomad Job Specification
A local HCL job for testing Nomad batch execution. This maps directly to `nomad_jobspec.py` in the real extension, which will generate equivalent JSON specs programmatically:

```hcl
job "firstjob" {
  datacenters = ["dc1"]
  type        = "batch"

  group "firstjob" {
    count = 1
    task "runjob" {
      driver = "raw_exec"
      config {
        command = "/bin/bash"
        args    = ["-c", "echo hello from nomad"]
      }
    }
  }
}
```

---

### `job_run.py` — Job Submission
Explores how to submit jobs to Nomad via HTTP API — the core of what `nomad_client.submit_job()` will do:

```
POST http://localhost:4646/v1/jobs
→ Returns job ID for tracking
```

---

### `logger_logic.py` — Log Streaming
Explores real-time log retrieval from Nomad allocations:

```
GET http://localhost:4646/v1/client/fs/logs/:alloc_id
→ Streams stdout/stderr back to the Metaflow CLI
```

This is one of the harder parts of the integration. Unlike `@slurm` which uses SSH + `tail`, Nomad provides a dedicated HTTP log-streaming endpoint — requiring careful handling of chunked responses and allocation ID tracking.

---

### `result_nomad.py` — Result Fetching & Status Polling
Polls job status and maps Nomad allocation states to Metaflow states:

```
GET http://localhost:4646/v1/job/:id/allocations
→ Returns allocation status
```

| Nomad State  | Metaflow Mapping     |
|--------------|----------------------|
| `running`    | `is_running = True`  |
| `complete`   | `has_succeeded = True` |
| `failed`     | `has_failed = True`  |

---

### `retry_decorator.py` — Retry Logic
Prototype of `@retry` integration with Nomad — detecting failed allocations and resubmitting jobs with new allocation IDs. Maps to the retry handling inside `nomad_decorator.py`'s `runtime_step_cli()` method.

---

### `stepsflow_metaflow.py` — StepDecorator Lifecycle
Explores how Metaflow's `StepDecorator` hooks map to Nomad operations:

```
step_init()         → validate config, check NOMAD_HOST/PORT
runtime_step_cli()  → build CLI command for remote execution
task_pre_step()     → capture allocation ID + node metadata
task_finished()     → sync metadata to datastore, stop log sidecar
```

---

### `submit_job_fetch_results.py` — End-to-End Pipeline
Complete flow validation:

```
Submit job     →  POST /v1/jobs
     ↓
Poll status    →  GET  /v1/job/:id/allocations
     ↓
Stream logs    →  GET  /v1/client/fs/logs/:alloc_id
     ↓
Collect results and exit codes  ✅
```

---

## 🏗️ How This Maps to the Real Extension

This repository is exploration/prototype code. The production `@nomad` decorator will follow the official [`metaflow-slurm`](https://github.com/outerbounds/metaflow-slurm) extension pattern:

```
metaflow-nomad/
  metaflow_extensions/
    nomad_ext/
      plugins/
        nomad/
          ├── nomad_decorator.py    ← @nomad StepDecorator
          ├── nomad_client.py       ← HTTP API via python-nomad
          ├── nomad_job.py          ← Job lifecycle management
          ├── nomad_jobspec.py      ← JSON job spec generation
          ├── nomad_exceptions.py   ← Custom exceptions
          └── nomad_cli.py          ← CLI entry point
```

### Key Architectural Difference — `@slurm` vs `@nomad`

| Task             | `@slurm`              | `@nomad`                          |
|------------------|-----------------------|-----------------------------------|
| Connection       | SSH via `asyncssh`    | HTTP API via `python-nomad`       |
| Job submission   | `sbatch script.sh`    | `POST /v1/jobs`                   |
| Status polling   | SSH + `squeue`        | `GET /v1/job/:id/allocations`     |
| Log retrieval    | SSH + `tail`          | `GET /v1/client/fs/logs/:alloc_id`|
| Cancellation     | SSH + `scancel`       | `DELETE /v1/job/:id`              |

**No SSH required — just clean HTTP API calls.** ✅

---

## ✅ Proof of Work — Local Nomad Setup

```bash
$ nomad version
Nomad v1.11.3

$ nomad node status
ID        Node Pool  DC   Name             Status
122b9031  default    dc1  DESKTOP-22K0NHN  ready ✅

$ nomad job status firstjob
Status = complete ✅
```

Verified locally:
- ✅ Nomad v1.11.3 running in dev mode
- ✅ Batch jobs submitted and completed via HCL files
- ✅ Logs retrieved from allocations via CLI and Nomad UI
- ✅ HTTP API endpoints tested directly via Python
- ✅ Full job lifecycle understood: `pending → running → complete`

---

## 🚀 Running Locally

### Prerequisites

```bash
sudo apt install nomad -y
pip install requests metaflow
```

### Start Nomad

```bash
nomad agent -dev
```

### Submit a Test Job

```bash
nomad job run firstjob.hcl
nomad job status firstjob
```

### Run the Python Scripts

```bash
python job_run.py
python logger_logic.py
python submit_job_fetch_results.py
```

---

## 🔗 Related Links

| Resource                  | Link |
|---------------------------|------|
| GSoC 2026 Project         | [Metaflow Nomad Integration](https://summerofcode.withgoogle.com/) |
| Metaflow                  | [github.com/Netflix/metaflow](https://github.com/Netflix/metaflow) |
| Reference Extension       | [outerbounds/metaflow-slurm](https://github.com/outerbounds/metaflow-slurm) |
| My Open PRs on metaflow-slurm  | [Pull Requests](https://github.com/outerbounds/metaflow-slurm/pulls) |
| My Merged PRs on metaflow-slurm | [Pull Requests](https://github.com/outerbounds/metaflow-slurm/pulls) |
| Nomad HTTP API            | [developer.hashicorp.com/nomad/api-docs](https://developer.hashicorp.com/nomad/api-docs) |
| python-nomad              | [pypi.org/project/python-nomad](https://pypi.org/project/python-nomad) |

---

## 👤 About

**Talha Abdul Sattar**
3rd Year BSc Software Engineering — Islamia University of Bahawalpur, Pakistan

📧 [talhaabdulsattar65@gmail.com](mailto:talhaabdulsattar65@gmail.com)
🐙 [github.com/Talha8899](https://github.com/Talha8899)
💼 [linkedin.com/in/talha-abdul-sattar-4b4926389](https://linkedin.com/in/talha-abdul-sattar-4b4926389)

---

*This repository is part of my GSoC 2026 application for the Metaflow Nomad Integration project under Outerbounds/Netflix.*
