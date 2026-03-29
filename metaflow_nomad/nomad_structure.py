from metaflow.decorators import StepDecorator

#get nomad credentials

class NomadDecorator(StepDecorator):
    name = 'nomad'
    defaults = {
        'host': None, 'port': 4646, 'token': None,
        'image': None, 'cpu': 1000, 'memory': 4096,
    }

    def step_init(self, flow, graph, step, ...):
        # validate NOMAD_HOST, NOMAD_PORT
        # raise NomadException if missing

    def runtime_step_cli(self, cli_args, retry_count, ...):
        # build: python flow.py nomad step <step_name>
        # append package_sha, package_url, decorator options

    def task_pre_step(self, step_name, task_datastore, ...):
        # capture NOMAD_ALLOC_ID, node metadata
        # start _save_logs_sidecar

    def task_finished(self, step_name, ...):
        # sync metadata to datastore
        # stop log sidecar
        try:
            self._save_logs_sidecar.terminate()
        except Exception:
            pass  # best effort
