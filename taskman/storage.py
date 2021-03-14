"""
storage.py: Set of data structures and routine for process storage.
"""
from enum import Enum
from .config import PROCESS_STORAGE_CAPACITY
from .process import Process
from .pid import PID
from .log import Log


class StorageOperationResult(Enum):
    """A definition of Storage error codes enumeration.

    Attributes:
        OK Operation was performed successfully.
        FAILED Operation failed with an error without specific type.
        FULL Operation failed (insertion) because storage size reached its limit.
        REMOVED_OLDEST Operation succeeded (insertion) but the oldest process was killed and removed.
        REMOVED_LOWEST Operation succeeded (insertion) but the process with lowest priority was killed and removed.
    """
    OK = 0
    FAILED = 1
    FULL = 2
    REMOVED_OLDEST = 3
    REMOVED_LOWEST = 4


class ProcessSortCriteria(Enum):
    """A definition of sort criteria for process list.

    Attributes:
        TIME Sort by process creation time.
        PRIORITY Sort by process priority value.
        PID Sort by process identifier.
    """
    TIME = 0
    PRIORITY = 1
    PID = 2


class ProcessSortOrder(Enum):
    """A definition of sort order for process list.

    Attributes:
        ASC Sort in ascendant order.
        DESC Sort in descendant order.
    """
    ASC = 0
    DESC = 1


class ProcessStorage(object):
    """A definition of a process storage class. This interface defines behavior (with some elements of a base class)
    for any process storage implementation which may require along the way.

    Note:
        The idea is that storage implementation can be specific depending which behavior is needed. We define three
        major use-cases:
            1. Add process - Used when TaskManager asked to create new process.
            2. Remove process - Used when process kill executed by TaskManager and process has to be removed from the
                                list.
            3. List processes - Provide list of all processes available in the system with few sorting criteria.

        The underlying data structure for storage is dictionary (hashmap). This would allow us to have O(1) complexity
        for insertion (add new process) and deletion (removed killed process). `list` function performance and space
        is sacrificed as list function would have to repack dictionary into list and sort it based on input criteria.

        There is no optimal solution as there are multiple presentation criteria which are applicable to any
        implementation. Even if one use-case (sort by priority) can be satisfied (priority queue for FIFO) still the
        other ones would have something extra to do.
    """
    def __init__(self, capacity: int = PROCESS_STORAGE_CAPACITY, logger: Log = Log()):
        """A constructor of default Process Storage class.

        :param capacity: Max. number of processes can be stored.
        :param logger: Instance of package Log class.
        """
        self._capacity = capacity
        self._storage = dict()
        self._log = logger

    def add(self, process: Process) -> StorageOperationResult:
        """Add Process instance to the storage. In case process storage is full an error will be returned.

        :param process: Instance of Process to be added to storage.
        :return: One of the StorageOperationResult values.
        """
        if len(self) >= self._capacity:
            self._log.warning(f'Process Storage capacity {self._capacity} was reached')
            return StorageOperationResult.FULL

        pid = process.pid.value

        if pid in self._storage:
            """In theory this shouldn't happen, but in case process is submitted multiple times it's better to return
            an error. In case there is no error we will just overwrite the same descriptor without impact on anything,
            but it's still better to report an error, as this is not regular case.
            """
            self._log.error(f'{process} already exist in the storage')
            return StorageOperationResult.FAILED

        self._storage[pid] = process
        self._log.debug(f'{process} was added to ProcessStorage')
        return StorageOperationResult.OK

    def remove(self, process: Process) -> StorageOperationResult:
        """Remove Process instance from the storage.

        :param process: Process instance to be removed.
        :return:
        """
        pid = process.pid.value
        if pid not in self._storage:
            self._log.warning(f'{process} does not exist in ProcessStorage')
            return StorageOperationResult.FAILED

        del self._storage[pid]
        return StorageOperationResult.OK

    def list(self, criteria: ProcessSortCriteria = ProcessSortCriteria.TIME,
             order: ProcessSortOrder = ProcessSortOrder.ASC) -> list:
        """Provide list of all processes available in the storage sorted by `criteria` in `order`.

        :param criteria: One of the `ProcessSortCriteria` values.
        :param order: On of the `ProcessSortOrder` values.
        :return: Sorted list of processes.
        """
        result = list()
        for k in self._storage:
            """We are going to iterate over dictionary (hashmap) with processes and create a list.
            """
            result.append(self._storage[k])

        """Decide which sorting criteria to use and perform inplace sorting.
        """
        is_desc_order = True if order == ProcessSortOrder.DESC else False
        if criteria == ProcessSortCriteria.TIME:
            result.sort(key=lambda item: item.created, reverse=is_desc_order)
        elif criteria == ProcessSortCriteria.PRIORITY:
            result.sort(key=lambda item: item.priority, reverse=is_desc_order)
        elif criteria == ProcessSortCriteria.PID:
            result.sort(key=lambda item: item.pid.value, reverse=is_desc_order)

        return result

    def __len__(self) -> int:
        """Get number of processes stored in the storage.

        :return: Number of processes stored in the storage.
        """
        return len(self._storage)

    def __getitem__(self, item: PID) -> Process:
        """Get instance of `Process` by PID.

        :raises KeyError in case process was not found.
        :param item: Instance of PID class.
        :return: `Process` instance.
        """
        return self._storage.__getitem__(item)

    def __iter__(self):
        """Get ProcessStorage iterator.

        :return: Storage iterator value (current).
        """
        return self._storage.__iter__()


class FIFOProcessStorage(ProcessStorage):
    """An implementation of the FIFO based process storage class.

    Note:
        This class should be able to always add new process as it will just remove the oldest one.
    """
    def add(self, process: Process) -> StorageOperationResult:
        """Add new process to the process storage. In case process storage is full the oldest process will be removed
        from the storage and new one will take its place.

        Note:
            This implementation worst case complexity is O(n) as we need to find min value among all the processes.

        :param process: Process instance to be added.
        :return: StorageOperationResult.OK when process was added.
        """
        r = super(FIFOProcessStorage, self).add(process)

        if r != StorageOperationResult.FULL:
            """In this implementation we follow logic of default implementation unless storage is full.
            """
            return r

        """Find the oldest process by checking min (process creation time) value among all the processes.
        """
        oldest = min(self._storage.keys(), key=(lambda key: self._storage[key].created))
        self._log.debug(f'Found oldest process {self._storage[oldest]} in the FIFOProcessStorage')

        """Once oldest process identified remove it from the dictionary and call standard method again. As it would be
        good to provide error code for the calling function with a feedback that we killed one of the processes.
        """
        self._storage[oldest].kill()
        r = super(FIFOProcessStorage, self).add(process)
        if r == StorageOperationResult.OK:
            self._log.debug(f'New {process} was added while oldest was removed')
            return StorageOperationResult.REMOVED_OLDEST

        self._log.error(f'Something unexpected happened when adding new {process} into FIFOProcessStorage')
        return StorageOperationResult.FAILED


class PriorityProcessStorage(ProcessStorage):
    """An implementation of process storage based on process priority.

    Note:
        This implementation suppose to insert new process (in case of full storage) only if new process priority is
        bigger than lowest one. In case there are multiple processes with lower priority (comparing to the new one)
        the oldest (based on creation time) will be removed and killed.
    """
    def add(self, process: Process) -> StorageOperationResult:
        """Add new process to the process storage. In case storage is full process with lower priority will be deleted.

        :param process: Process instance to be added.
        :return: StorageOperationResult.OK when process was added.
        """
        r = super(PriorityProcessStorage, self).add(process)

        if r != StorageOperationResult.FULL:
            """In this implementation we follow logic of default implementation unless storage is full.
            """
            return r

        key_lowest_priority = min(self._storage.keys(), key=(lambda key: self._storage[key].priority))
        lowest_priority = self._storage[key_lowest_priority].priority

        if process.priority <= lowest_priority:
            self._log.warning(f'{process} can not be added as lowest priority in the storage {lowest_priority}')
            return StorageOperationResult.FAILED

        lowest_priority_processes = list()
        for k in self._storage:
            if self._storage[k].priority == lowest_priority:
                lowest_priority_processes.append(self._storage[k])

        oldest_among_lowest = min(lowest_priority_processes, key=lambda item: item.created)
        pid = oldest_among_lowest.pid.value
        del self._storage[pid]
        r = super(PriorityProcessStorage, self).add(process)
        if r == StorageOperationResult.OK:
            self._log.debug(f'New {process} was added while oldest was removed')
            return StorageOperationResult.REMOVED_LOWEST

        return StorageOperationResult.OK
