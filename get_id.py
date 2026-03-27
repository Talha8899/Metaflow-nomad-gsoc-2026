import requests
import json

def get_job_ids():
    try:
        url="http://127.0.0.1:4646/v1/job/firstjob/allocations"
        headers={
            "Content-Type": "application/json",
            "X-Nomad-Token": "namespace:read-job"
        }
        responce=requests.get(url,headers=headers).json()
        # print(responce)
        job_ids = [item['ID'] for item in responce]
        tasks=[item['TaskStates'].keys() for item in responce]
        return job_ids,tasks
    except Exception as e:
        print(f"programe is failed  {e}")