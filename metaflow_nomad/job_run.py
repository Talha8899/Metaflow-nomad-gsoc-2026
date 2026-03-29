import requests
import json
from result_nomad import get_stdout

#this file can run a job file on nomad by using is api then fatch stdout and show on terminal



try:
    #opning file in which nomad job are written as hcl 
    with open("/home/talha/Metaflow-nomad-gsoc-2026/firstjob.hcl") as f:
        hcl_data=f.read()
except Exception as e:
    print(e)

#Parsing
try:
    #parse the hcl file in to json 
    parse_url="http://127.0.0.1:4646/v1/jobs/parse"
    #Hearde for http request that goes with url 
    headers = {
        "Content-Type": "application/json",
        "X-Nomad-Token": "namespace:parse-job" 
    }
    #creating dict for parseing
    Hcl_dict={"JobHCL":hcl_data}

    #sending request to api for storing the responce of resuest in jason
    parse_responce=requests.post(parse_url, headers=headers, json=Hcl_dict).json()

    #creat a new dict for sending jobs to nomad cluster
    final_parse_data_dict={"Job":parse_responce}
except:
    raise Exception ("error to connect parse server ")


 #Submiting job to nomad
# wraping them in try catch for safety
try:
    #nomad job url 
    Job_url="http://127.0.0.1:4646/v1/jobs"
    # header
    headers = {
        "Content-Type": "application/json",
        "X-Nomad-Token": "namespace:submit-job"   # optional agar ACL enabled ho
    }
    #job sumbmiting to nomad and print the status
    responce=requests.post(Job_url, headers=headers, json=final_parse_data_dict)

    #printing the respoce of nomad 
    print(responce)

except:
    raise Exception ("error connecting to job server")

get_stdout()