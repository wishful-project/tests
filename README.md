WiSHFUL Framework Testing Platform
==================================

Installation
------------

pip3 install -r requirements.txt


Execute tests on local host
---------------------------

pytest [-s]


Execute tests on multiple hosts
-------------------------------

1. Start remote_agent_host on all hosts exept one [TestExecutor]:

        sudo ./common/remote_agent_host [--port=PORT]

2. On TestExecutor host edit remote_hosts.yaml file.

3. Start tests:

		pytest [-s]


## Acknowledgement

The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
