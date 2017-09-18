import pytest
import sh
import signal
import zmq

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2017, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class RemoteAgentHost(object):
    def __init__(self, port=567890):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)

        self.agentScriptPath = "/tmp/recv_agentScript.py"
        self.agentConfigPath = "/tmp/recv_agentConfig.yaml"

        self.agentStartCmd = sh.Command("python3")
        self.agentProcess = None
        self.isRunning = False

    def start_agent_process(self):
        self.agentProcess = self.agentStartCmd(self.agentScriptPath,
                                               "--config",
                                               self.agentConfigPath,
                                               _bg=True, _out=None, _err=None)
        self.isRunning = True
        print('\nWiSHFUL Agent started in new process')

    def is_agent_process_running(self):
        return self.isRunning

    def stop_agent_process(self):
        try:
            self.agentProcess.signal(signal.SIGINT)
        except Exception as e:
            print("Agent stopped", e)
        self.isRunning = False
        print('\nWiSHFUL Agent process terminated')

    def terminate_agent_process(self):
        try:
            self.agentProcess.terminate()
        except Exception as e:
            print("Agent killed", e)
        self.isRunning = False
        print('\nWiSHFUL Agent process terminated')

    def start_cmd_rx(self):
        try:
            while True:
                [cmd, data] = self.socket.recv_multipart()
                print ("Received request: ", cmd)
                if cmd == b"agentConfig":
                    try:
                        sh.rm(self.agentConfigPath)
                    except Exception:
                        print("file does not exist, skip")

                    try:
                        f = open(self.agentConfigPath, 'wb')
                        f.write(data)
                        f.close()
                    except Exception:
                        self.socket.send_json(1)

                elif cmd == b"agentScript":
                    try:
                        sh.rm(self.agentScriptPath)
                    except Exception:
                        print("file does not exist, skip")

                    try:
                        f = open(self.agentScriptPath, 'wb')
                        f.write(data)
                        f.close()
                    except Exception:
                        self.socket.send_json(2)

                elif cmd == b"start_remote_agent":
                    try:
                        self.start_agent_process()
                    except Exception:
                        self.socket.send_json(3)

                elif cmd == b"is_remote_agent_running":
                    try:
                        r = self.is_agent_process_running()
                        retVal = 0
                        if r:
                            retVal = 1
                        self.socket.send_json(retVal)
                    except Exception:
                        self.socket.send_json(4)
                    continue

                elif cmd == b"stop_remote_agent":
                    try:
                        self.stop_agent_process()
                    except Exception:
                        self.socket.send_json(5)

                elif cmd == b"terminate_remote_agent":
                    try:
                        self.terminate_agent_process()
                    except Exception:
                        self.socket.send_json(6)

                self.socket.send_json(0)
        except KeyboardInterrupt:
            print("RemoteAgentHost exits")
            self.terminate_agent_process()


class RemoteAgentHostProxy(object):
    def __init__(self, ip, port=567890):
        self.ip = ip
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://{}:{}".format(self.ip, self.port))

        self.agentScriptPath = None
        self.agentConfigPath = None

    def send_cmd(self, cmd, data=b""):
        msg = [cmd, data]
        self.socket.send_multipart(msg, zmq.NOBLOCK)
        response = self.socket.recv()
        return response

    def upload_agent_script(self, agentScriptPath):
        self.agentScriptPath = agentScriptPath
        file = open(agentScriptPath, 'rb')
        data = file.read()
        msg = [b"agentScript", data]
        self.socket.send_multipart(msg, zmq.NOBLOCK)
        response = self.socket.recv()
        response = int(response)
        return response

    def upload_agent_config(self, agentConfigPath):
        self.agentConfigPath = agentConfigPath
        file = open(agentConfigPath, 'rb')
        data = file.read()
        msg = [b"agentConfig", data]
        self.socket.send_multipart(msg, zmq.NOBLOCK)
        response = self.socket.recv()
        response = int(response)
        return response

    def start_remote_agent(self):
        return int(self.send_cmd(b"start_remote_agent"))

    def is_remote_agent_running(self):
        return bool(int(self.send_cmd(b"is_remote_agent_running")))

    def stop_remote_agent(self):
        return int(self.send_cmd(b"stop_remote_agent"))

    def stop(self):
        return self.stop_remote_agent()

    def terminate_remote_agent(self):
        return int(self.send_cmd(b"terminate_remote_agent"))

    def terminate(self):
        return self.terminate_remote_agent()


@pytest.fixture(scope='module')
def remote_agent_manager(request):
    agents = []

    class RemoteAgentManager(object):
        def create_remote_agent_proxy(self, ip, port=567890):
            agent = RemoteAgentHostProxy(ip, port)
            agents.append(agent)
            return agent

        def start_remote_agent(self, scriptPath, configPath, ip, port=567890):
            agent = RemoteAgentHostProxy(ip, port)
            agent.upload_agent_script(scriptPath)
            agent.upload_agent_config(configPath)
            agent.start_remote_agent()
            agents.append(agent)
            return agent

        def get_agent(self, idx):
            return agents[idx]

    def teardown():
        print("\nTerminate all Local Agent processes")
        for agent in agents:
            if agent.is_remote_agent_running():
                agent.stop_remote_agent()

    request.addfinalizer(teardown)
    return RemoteAgentManager()
