# Metaflow-nomad-gsoc-2026
A specialized toolset for integrating Metaflow with HashiCorp Nomad, focusing on automated job lifecycle management and real-time observability. Built for the Google Summer of Code 2026.

📌 Overview
This project bridges the gap between Metaflow workflows and Nomad orchestration. It provides a Pythonic way to submit jobs, track allocations, and stream execution results (stdout/stderr) directly to a unified dashboard or "alarm" screen.

✨ Key Features
Decorator-Driven API: Uses @get_job_ids to pre-fetch allocation data before executing logic.
Smart Log Streaming: Automatically pairs Allocation IDs with their respective Task Names to fetch accurate logs.
Live "Alarm" Dashboard: A CLI-based monitor that processes jobs one-by-one with counters and short-ID formatting ([:8]).
Error Detection: Logic to automatically switch from stdout to stderr if a task fails or produces no output.

🛠 Tech Stack
Core: Python 3.x
Orchestration: HashiCorp Nomad
Networking: requests for HTTP API interaction
Patterns: Functional decorators (functools.wraps), List/Dict comprehensions, and Synchronized Iteration (zip, enumerate).

🚀 Getting Started
Prerequisites
A running Nomad agent (locally: nomad agent -dev).
Python 3.8+ installed.
Installation
bash
git clone https://github.com
cd Metaflow-nomad-gsoc-2026
pip install requests
Use code with caution.

Configuration
Set your Nomad address and security token as variables or within your headers:
python
URL = "http://127.0.0.1:4646"
TOKEN = "your-secret-id-here"
Use code with caution.

📂 Code Highlights
The Log Monitoring Loop
This implementation ensures that every Job ID is perfectly matched with its Task Name for accurate log retrieval:
python
@get_job_ids
def get_stdout(ids, tasks):
    for count, (alloc_id, task_name) in enumerate(zip(ids, tasks), start=1):
        print(f"[{count}] Processing ID: {alloc_id[:8]} | Task: {task_name}")
        # Fetching stdout...
Use code with caution.

📋 Roadmap
Metaflow Card Integration: Visualize Nomad logs inside Metaflow's UI.
Auto-Resubmission: Automatically re-run failed Nomad allocations from the dashboard.
Multi-Namespace Support: Scaling the monitoring tool for enterprise Nomad clusters.

🤝 Contributing
Fork the project.
Create your Feature Branch (git checkout -b feature/NewFeature).
Commit your changes (git commit -m 'Add NewFeature').
Push to the branch (git push origin feature/NewFeature).
Open a Pull Request.

Developed for GSoC 2026 | Metaflow + Nomad
