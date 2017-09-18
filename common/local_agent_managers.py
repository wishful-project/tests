import pytest
import sh
import signal

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2017, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


class AgentLocalProcess(object):
    def __init__(self, scriptPath, configPath):
        self.agentScriptPath = scriptPath
        self.agentConfigPath = configPath

        self.agentStartCmd = sh.Command(self.agentScriptPath)
        self.agentProcess = None
        self.isRunning = False

    def start(self):
        self.agentProcess = self.agentStartCmd("--config",
                                               self.agentConfigPath,
                                               _bg=True, _out=None, _err=None)
        self.isRunning = True
        print('\nWiSHFUL Agent started in new process')

    def stop(self):
        try:
            self.agentProcess.signal(signal.SIGINT)
        except Exception as e:
            print("Agent stopped", e)
        self.isRunning = False
        print('\nWiSHFUL Agent process terminated')

    def terminate(self):
        try:
            self.agentProcess.terminate()
        except Exception as e:
            print("Agent killed", e)
        self.isRunning = False
        print('\nWiSHFUL Agent process terminated')

    def is_running(self):
        return self.isRunning


@pytest.fixture(scope='module')
def local_agent_manager(request):
    agents = []

    class LocalAgentManager(object):
        def start_agent(self, scriptPath, configPath):
            agent = AgentLocalProcess(scriptPath, configPath)
            agent.start()
            agents.append(agent)
            return agent

        def terminate_agent(self):
            pass

        def get_agent(self, idx):
            return agents[idx]

    def teardown():
        print("\nTerminate all Local Agent processes")
        for agent in agents:
            if agent.is_running():
                agent.stop()

    request.addfinalizer(teardown)
    return LocalAgentManager()
