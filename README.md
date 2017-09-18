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

1. Start remote_agent_host on all hosts exept one (i.e. group leader):

        sudo ./common/remote_agent_host [--port=PORT, default=567890]

2. On group leader host edit remote_hosts.yaml file and specify all nodes in network.

        # List all hosts:
        hosts:
            - {"ip": 192.168.0.1, "port": 567890}
            - {"ip": 192.168.0.2, "port": 567890}
            - {"ip": 192.168.0.3, "port": 567890}

        # List only hosts with wifi card installed:
        wifi:
            - {"ip": 192.168.0.1, "port": 567890}
            - {"ip": 192.168.0.3, "port": 567890}

        # etc...

3. On group leader host start tests:

        pytest [-s]


## Acknowledgement

The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
