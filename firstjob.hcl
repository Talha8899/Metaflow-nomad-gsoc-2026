job "firstjob"{
    datacenters=["dc1"]
    type       ="batch"
    group "firstjob"{
        count=1
        task "runjob"{
            driver="raw_exec"
            config{
                command="/bin/bash"
                args=["-c","echo hello i am nomad"]
            }
        }
    }
    group "secondjob"{
        count=1
        task "run2ndjob"{
            driver="raw_exec"
            config{
                command="/bin/bash"
                args=["-c","echo 2nd job in the running"]
            }
        }
    }
}