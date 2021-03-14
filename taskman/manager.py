"""
manager.py: Implementation main interface for process management.
"""
from logging import Logger
from .process import Process, ProcessPriority
from .storage import ProcessStorage, ProcessSortCriteria, ProcessSortOrder, StorageOperationResult
from .pid import PidGenerator
from .log import Log


class TaskManager(object):
    """An implementation of a top level interface for System Task Manager.

    Note:
        This implementation takes on input standard python logger in case it has to be integrated into a bigger system.

        Behavior of particular instance based on the way object was constructed (which underlying storage is used).
    """
    def __init__(self, storage: ProcessStorage = ProcessStorage(), logger: Logger = None):
        """A constructor of TaskManager class.

        :param storage: An instance of ProcessStorage class (or any of the child variants).
        :param logger: Instance of standard python logger.
        """
        self._processes = storage
        self._log = Log(logger)
        self._log.debug('TaskManager instance was created')

    def add(self, cmd: str, priority: ProcessPriority) -> (None, Process):
        """Add new process to the system.

        Note:
            This function can have different behavior depending on ProcessStorage type.

        :param cmd: Process underlying command.
        :param priority: Process execution priority.
        :return: Instance of `Process` class on success, None otherwise.
        """
        proc = Process(PidGenerator.generate(), cmd, priority)
        proc._set_kill_callback(self._process_kill_callback)
        r = self._processes.add(proc)
        if r == StorageOperationResult.FAILED:
            """In case we were unable to add process into storage we have to kill newly created process in order to
            avoid resource leak.
            """
            proc.kill()
            self._log.error(f'An error {r} happened when trying to add process to TaskManager')
            return None

        self._log.info(f'Process {proc} was added to TaskManager')
        return proc

    def __len__(self) -> int:
        """Get number of processes managed by TaskManager instance.

        :return: Number of processes managed by TaskManager instance.
        """
        return len(self._processes)

    def list(self, criteria: ProcessSortCriteria = ProcessSortCriteria.TIME,
             order: ProcessSortOrder = ProcessSortOrder.ASC) -> list:
        """List all processes available in the system in order driven by `sort_by` argument.

        :return: Ordered list of Process instances.
        """

        return self._processes.list(criteria, order)

    def kill(self, process: Process) -> bool:
        """Terminate process based on `Process` instance (descriptor).

        Note:
            Process instance as a descriptor will be returned to called of `TaskManager.add`.

        :param process: Instance of the `Process` to be terminated.
        :return: True on success, False otherwise.
        """
        r = process.kill()
        self._log.info(f'{process} was killed with result: {r}')
        return r

    def kill_group(self, priority: ProcessPriority) -> int:
        """Terminate all processes with given priority.

        Note:
            This function is not really efficient as we need to repack all `Process` instances from dictionary to a
            list as we can't remove element from a dictionary while iterating.

        :param priority: ProcessPriority value.
        :return: Number of processes terminated successfully.
        """
        to_kill = list()
        for k in self._processes:
            proc = self._processes[k]
            if proc.priority == priority:
                to_kill.append(proc)

        return Process.kill_list(to_kill)

    def kill_all(self) -> bool:
        """Terminate all processes known to TaskManager.

        Note:
            This function is not really efficient as we need to repack all `Process` instances from dictionary to a
            list as we can't remove element from a dictionary while iterating.

        :return: True if all processes were terminated successfully, False otherwise.
        """
        to_kill = list()
        for k in self._processes:
            to_kill.append(self._processes[k])

        return True if Process.kill_list(to_kill) == len(to_kill) else False

    def _process_kill_callback(self, process: Process) -> bool:
        """Implementation of an internal callback function for removing process from the TaskManager storage.
        TaskManager is just an manager over process descriptors and it doesn't have any control on when process is
        going to end. TaskManager can kill process, but process may stop way before it due to multiple different
        reasons.

        In case something like that happens this function will be always called and will make sure process which has
        been finished will be deleted from the system.

        :param process: Process which successfully processed `Process.kill()` command.
        :return: True if process was removed, False otherwise.
        """
        self._log.debug(f'Process kill callback for {process} was called')
        return True if self._processes.remove(process) == StorageOperationResult.OK else False
