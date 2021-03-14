"""
process.py: Set of data structures to define system process (it is actually stub).
"""
from datetime import datetime as dt
from enum import IntEnum
from .pid import PID


class ProcessPriority(IntEnum):
    """Definition of enumeration for process priority.

    Note:
        The requirement is to have three levels of priority. ProcessPriority extends IntEnum which is essentially
        integer data type. In case priority scale would change (becomes from 0 to 100 for instance) it will be easy to
        update this implementation without huge impact to logic of the implementation.

    Attributes:
        LOW Low process priority.
        MEDIUM Medium process priority.
        HIGH High process priority.
    """
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class Process(object):
    """An implementation of a system process stub.
    """
    def __init__(self, pid: PID, cmd: str, priority: ProcessPriority = ProcessPriority.LOW):
        """A constructor of Process class.

        :param pid: Process Identifier object.
        :param cmd: Process command to execute (kind of execute).
        :param priority: Process execution priority.
        :param cb: Callback function will be called when process ends (with one or another reason).
        """
        self._pid = pid
        self._cmd = cmd
        self._priority = priority
        self._created = dt.now()
        self._cb = None

    def _set_kill_callback(self, cb):
        """Set callback function for instance of `Process` to call when `Process.kill` method was executed.

        :param cb: Function with single argument of `Process` instance.
        :return: None.
        """
        self._cb = cb

    @property
    def cmd(self):
        """Get process command (something what is executed, or suppose to be executed).

        :return: Process underlying command.
        """
        return self._cmd

    @property
    def created(self) -> dt:
        """Get process creation timestamp.

        :return: Instance of datetime object representing process (object) creation time.
        """
        return self._created

    @property
    def pid(self) -> PID:
        """Get process Identifier value.

        :return: Process Identifier value.
        """
        return self._pid

    @property
    def priority(self) -> ProcessPriority:
        """Get Process instance priority.

        :return: Process priority value.
        """
        return self._priority

    def __str__(self) -> str:
        """Generate process string representation.

        :return: String representation of a Process class instance.
        """
        return f'<Process {self.pid} ({self.priority.name}) cmd=({self.cmd}) created={self.created}>'

    def __repr__(self) -> str:
        """Generate process representation string.

        :return: String representation of a Process class instance.
        """
        return self.__str__()

    def kill(self) -> bool:
        """Send signal to the process instance to stop and destroy all resources.

        Note:
            This function always returns True, as it's just a mock. There is also no signal number, as kill means send
            signal and process will respond accordingly based on signal number. But in this implementation we assume
            that process will be stopped and destroyed.

        :return: True if process was stopped, False otherwise.
        """
        if self._cb is not None:
            return self._cb(self)
        return True

    @staticmethod
    def kill_list(proc_list: list) -> int:
        """Execute `Process.kill()` for every process in a list.

        :param proc_list: Process list.
        :return: Number of processes were killed successfully.
        """
        result = 0
        for p in proc_list:
            if p.kill() is True:
                result += 1
        return result
