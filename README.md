# Metaflow × Nomad — GSoC 2026 Exploration

[![GSoC 2026](https://img.shields.io/badge/GSoC-2026-red?logo=google)](https://summerofcode.withgoogle.com/)
[![Metaflow](https://img.shields.io/badge/Metaflow-2.x-blue)](https://metaflow.org)
[![Nomad](https://img.shields.io/badge/HashiCorp-Nomad%20v1.11.3-green)](https://www.nomadproject.io)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)](https://python.org)

> **GSoC 2026 Preparation Repository**  
> Hands-on exploration of the Metaflow + Nomad integration problem.  
> Built by [@Talha8899](https://github.com/Talha8899) as part of the GSoC 2026 application for the **Metaflow Nomad Integration** project under [Outerbounds](https://outerbounds.com).

---

## 🎯 The Problem This Solves

Metaflow currently supports these compute backends:

| Decorator | Backend | Status |
|---|---|---|
| `@kubernetes` | Kubernetes clusters | ✅ Exists |
| `@batch` | AWS Batch | ✅ Exists |
| `@slurm` | HPC Slurm clusters | ✅ Exists |
| `@nomad` | HashiCorp Nomad | ❌ **Missing — this project** |

Many organizations use **Nomad** instead of Kubernetes — especially those already using HashiCorp's stack (Vault, Consul, Terraform). They **cannot use Metaflow today** because there is no `@nomad` decorator.

This repository explores every piece of that missing integration — from job submission to log streaming to retry handling — before building the real extension.

---

## 📁 Repository Structure

```
Metaflow-nomad-gsoc-2026/
metaflow_nomad/
│
├── result_nomad.py               # Result fetching via GET /v1/job/:id/allocations
├── retry_decorater.py            # Retry logic — resubmit failed jobs
├── stepsflow_metaflow.py         # Metaflow flow with steps + decorator lifecycle
└── submit_job_fatch_results.py   # End-to-end: submit → monitor → fetch logs
```

---

## 🔬 What Each File Explores

### `firstjob.hcl` — Nomad Job Specification
Local HCL job file for testing Nomad's batch job execution. Maps directly to `nomad_jobspec.py` in the real extension which will generate equivalent JSON specs programmatically:

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
→ Streams stdout/stderr back to Metaflow CLI
```

This is one of the **hardest parts** of the integration. Unlike Slurm which uses SSH + `tail`, Nomad provides a dedicated log streaming HTTP endpoint requiring careful handling of streaming responses and allocation ID tracking.

---

### `result_nomad.py` — Result Fetching & Status Polling
Polls job status and maps Nomad states to Metaflow states:

```
GET http://localhost:4646/v1/job/:id/allocations
→ Returns allocation status
```

State mapping:
```python
"running"  → is_running    = True
"complete" → has_succeeded = True
"failed"   → has_failed    = True
```

---

### `retry_decorater.py` — Retry Logic
Prototype of how `@retry` integration will work with Nomad — detecting failed allocations and resubmitting jobs with new allocation IDs. Maps to retry handling in `nomad_decorator.py`'s `runtime_step_cli()` method.

---

### `stepsflow_metaflow.py` — Metaflow Flow + Decorator Lifecycle
Understanding how Metaflow's `StepDecorator` lifecycle works:

```
step_init()         → validate config, check NOMAD_HOST/PORT
runtime_step_cli()  → build CLI command for remote execution
task_pre_step()     → capture allocation ID + node metadata
task_finished()     → sync metadata to datastore, stop log sidecar
```

---

### `submit_job_fatch_results.py` — End-to-End Pipeline
Complete flow validation:

```
Submit job → POST /v1/jobs
      ↓
Poll status → GET /v1/job/:id/allocations
      ↓
Stream logs → GET /v1/client/fs/logs/:alloc_id
      ↓
Collect results and exit codes ✅
```

---

## 🏗️ How This Maps to the Real Extension

This repository is **prototype/exploration code**. The real `@nomad` decorator will follow the official [metaflow-slurm](https://github.com/outerbounds/metaflow-slurm) extension pattern:

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

### Key Architectural Difference — Slurm vs Nomad:

| Task | `@slurm` | `@nomad` |
|---|---|---|
| Connection | SSH via `asyncssh` | HTTP API via `python-nomad` |
| Job submission | `sbatch script.sh` | `POST /v1/jobs` |
| Status polling | SSH + `squeue` | `GET /v1/job/:id/allocations` |
| Log retrieval | SSH + `tail` | `GET /v1/client/fs/logs/:alloc_id` |
| Cancellation | SSH + `scancel` | `DELETE /v1/job/:id` |

**No SSH needed — just clean HTTP API calls!** ✅

---

## ✅ Proof of Work — Local Nomad Setup

```bash
$ nomad version
Nomad v1.11.3

$ nomad node status
ID        Node Pool  DC   Name             Status
122b9031  default    dc1  DESKTOP-22K0NHN  ready ✅

$ nomad job status firstjob
Status      = complete ✅
```

**Verified locally:**
- ✅ Nomad v1.11.3 running in dev mode
- ✅ Batch jobs submitted and completed via HCL files
- ✅ Logs retrieved from allocations via CLI and Nomad UI
- ✅ HTTP API endpoints tested directly via Python
- ✅ Job lifecycle fully understood: pending → running → complete

---

## 🚀 Running Locally

### Prerequisites
```bash
sudo apt install nomad -y
pip install requests metaflow
```

### Start Nomad:
```bash
nomad agent -dev
```

### Submit test job:
```bash
nomad job run firstjob.hcl
nomad job status firstjob
```

### Run Python scripts:
```bash
python job_run.py
python logger_logic.py
python submit_job_fatch_results.py
```

---

## 🔗 Related Links

| Resource | Link |
|---|---|
| GSoC 2026 Project | [Metaflow Nomad Integration](https://docs.metaflow.org/internals/gsoc-2026) |
| Metaflow | [github.com/Netflix/metaflow](https://github.com/Netflix/metaflow) |
| Reference Extension | [outerbounds/metaflow-slurm](https://github.com/outerbounds/metaflow-slurm) |
| My PRs on metaflow-slurm | [Pull Requests](https://github.com/outerbounds/metaflow-slurm/pulls) |
| My MergdPRs on metaflow-slurm | [Pull Requests](https://github.com/outerbounds/metaflow-slurm/pull/16) |
| Nomad HTTP API | [developer.hashicorp.com/nomad/api-docs](https://developer.hashicorp.com/nomad/api-docs) |
| python-nomad | [pypi.org/project/python-nomad](https://pypi.org/project/python-nomad) |
https://github.com/outerbounds/metaflow-slurm/pull/16
---

## 👤 About

**Talha Abdul Sattar**
3rd Year BSc Software Engineering — Islamia University of Bahawalpur, Pakistan

- 📧 talhaabdulsattar65@gmail.com
- 🐙 [github.com/Talha8899](https://github.com/Talha8899)
- 💼 [linkedin.com/in/talha-abdul-sattar-4b4926389](https://linkedin.com/in/talha-abdul-sattar-4b4926389)

---

*This repository is part of my GSoC 2026 application for the Metaflow Nomad Integration project under Outerbounds/Netflix.*
