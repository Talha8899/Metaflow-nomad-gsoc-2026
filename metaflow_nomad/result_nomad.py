import requests
import json

def get_job_ids(func):
    def wrapper(*args,**kwargs):
        try:
            url="http://127.0.0.1:4646/v1/job/firstjob/allocations"
            headers={
                "Content-Type": "application/json",
                "X-Nomad-Token": "namespace:read-job"
            }
            responce=requests.get(url,headers=headers).json()
            # print(responce)
            job_ids = [item['ID'] for item in responce]
            tasks=[list(item['TaskStates'].keys())[0] for item in responce]
            log1=func(job_ids,tasks,*args,**kwargs)
            return log1
        except Exception as e:
            print(f"1st programe is failed  {e}")
    return wrapper

@get_job_ids
def get_stdout(ids,names):
    try:
        for alloc_id, name in zip(ids, names):
            url=f"http://127.0.0.1:4646/v1/client/fs/logs/{alloc_id}?task={name}&type=stdout&plain=true"
            headers={
                "Content-Type": "text/plain",
                "X-Nomad-Token": "namespace:read-logs"
            }
            responce=requests.get(url,headers=headers)
            # data={"value":responce}
            # print(data["value"])
            print(responce.text)
    except Exception as e:
        print(f"2nd programe is failed  {e}")
if __name__=="__main__":
    get_stdout()