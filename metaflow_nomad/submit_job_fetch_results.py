from metaflow import FlowSpec, step, retry
import requests
import json
from reult_logic import get_stdout


class NomadJobFlow(FlowSpec):
    """
    A Metaflow pipeline that:
      1. Reads a Nomad HCL job file
      2. Parses it via the Nomad API
      3. Submits it to the Nomad cluster
      4. Fetches and prints stdout from the job
    """

    @step
    def start(self):
        """Read the HCL job definition from disk."""
        hcl_path = "/home/talha/Metaflow-nomad-gsoc-2026/firstjob.hcl"

        with open(hcl_path) as f:
            self.hcl_data = f.read()

        print(f"Start HCL file loaded")
        self.next(self.parse_hcl)

    @retry(times=3)          # retries up to 3 times on failure
    @step
    def parse_hcl(self):
        """
        POST the raw HCL to Nomad's /v1/jobs/parse endpoint.
        Nomad returns the equivalent JSON job spec.
        @retry will automatically re-run this step if an exception is raised.
        """
        parse_url = "http://127.0.0.1:4646/v1/jobs/parse"
        headers = {
            "Content-Type": "application/json",
            "X-Nomad-Token": "namespace:parse-job",
        }

        response = requests.post(
            parse_url,
            headers=headers,
            json={"JobHCL": self.hcl_data},
        )
        response.raise_for_status()          # raises HTTPError → triggers retry

        self.parsed_job = response.json()    # store the parsed job dict
        print("Parse_hcl HCL parsed successfully")
        self.next(self.submit_job)

    @retry(times=3)          # retries up to 3 times on failure
    @step
    def submit_job(self):
        """
        POST the parsed job spec to Nomad's /v1/jobs endpoint.
        @retry handles transient network or cluster errors automatically.
        """
        job_url = "http://127.0.0.1:4646/v1/jobs"
        headers = {
            "Content-Type": "application/json",
            "X-Nomad-Token": "namespace:submit-job",
        }

        response = requests.post(
            job_url,
            headers=headers,
            json={"Job": self.parsed_job},
        )
        response.raise_for_status()          # raises HTTPError → triggers retry

        #self.submit_response = response.json()
        print(f"[submit_job] Job submitted — response: {response.status_code}")
        self.next(self.fetch_output)

    @retry(times=2)
    @step
    def fetch_output(self):
        """Fetch and display the job's stdout via result_nomad.get_stdout()."""
        print("Fetch_output Fetching job stdout …")
        get_stdout()
        self.next(self.end)

    @step
    def end(self):
        print("End nomadjobflow completed successfully.")


if __name__ == "__main__":
    NomadJobFlow()