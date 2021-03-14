import sys
from argparse import ArgumentParser, Namespace
import logging
from taskman import TaskManager, ProcessPriority, FIFOProcessStorage, ProcessSortOrder, ProcessSortCriteria,\
    PriorityProcessStorage

__version__ = '0.0.1'

# # create logger
log = logging.getLogger('taskman')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]%(message)s', '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
log.addHandler(ch)


def parse_command_line() -> Namespace:
    """Parse command line arguments and build namespace object in case of success.

    Note:
        There are no command line arguments except version.

    :return: Instance of Namespace.
    """
    parser = ArgumentParser('TaskManager application')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    return parser.parse_args()


def print_process_list(processes: list):
    """Print list of processes returned by TaskManager instance.

    :param processes: List of processes (of Process instance).
    :return: None.
    """
    print('Process list:')
    for i, p in enumerate(processes):
        print(f'\t{i}. {p}')


def main():
    """Entry point to the TaskManager application.

    Note:
        In this function we don't call logger to print as it should be internal to library and this file is more of a
        demo application.

    :return: 0 on success, non-zero otherwise.
    """
    result = 0

    args = parse_command_line()

    print('---------------- DEFAULT ----------------')

    # Create task manager with default behavior where process won't be added in case storage is full
    man_default = TaskManager(logger=log)

    man_default.add('cmd_1', ProcessPriority.LOW)
    to_remove = man_default.add('cmd_2', ProcessPriority.MEDIUM)
    man_default.add('cmd_3', ProcessPriority.HIGH)
    man_default.add('cmd_4', ProcessPriority.LOW)
    man_default.add('cmd_5', ProcessPriority.LOW)

    # In this case we should see all processes
    print_process_list(man_default.list(ProcessSortCriteria.PRIORITY, ProcessSortOrder.DESC))
    r = man_default.kill(to_remove)
    print(f'Process {to_remove} killed with result: {r}')

    # In this case we should see all processes except cmd_2
    print_process_list(man_default.list(ProcessSortCriteria.PRIORITY, ProcessSortOrder.DESC))

    print('---------------- FIFO ----------------')

    man_fifo = TaskManager(FIFOProcessStorage(), logger=log)

    man_fifo.add('cmd_1', ProcessPriority.LOW)
    man_fifo.add('cmd_2', ProcessPriority.MEDIUM)
    man_fifo.add('cmd_3', ProcessPriority.HIGH)
    man_fifo.add('cmd_4', ProcessPriority.LOW)
    man_fifo.add('cmd_5', ProcessPriority.LOW)

    # In this case we should see all processes
    print_process_list(man_fifo.list(ProcessSortCriteria.TIME, ProcessSortOrder.ASC))

    r = man_fifo.add('cmd_6', ProcessPriority.LOW)
    print(f'Process {r} was added to the TaskManager with FIFO update policy')
    # cmd_1 process should disappear while cmd_6 should be taken
    print_process_list(man_fifo.list(ProcessSortCriteria.TIME, ProcessSortOrder.ASC))

    r = man_fifo.kill_all()
    print(f'Terminated all processes with result {r}')

    print('---------------- PRIORITY ----------------')

    man_prior = TaskManager(PriorityProcessStorage(), logger=log)

    man_prior.add('cmd_1', ProcessPriority.HIGH)
    to_remove1 = man_prior.add('cmd_2', ProcessPriority.HIGH)
    to_remove2 = man_prior.add('cmd_3', ProcessPriority.HIGH)
    man_prior.add('cmd_4', ProcessPriority.HIGH)
    to_stop_by_itself = man_prior.add('cmd_5', ProcessPriority.HIGH)

    # In this case we should see all processes
    print_process_list(man_prior.list(ProcessSortCriteria.PRIORITY, ProcessSortOrder.ASC))

    man_prior.add('cmd_6', ProcessPriority.MEDIUM)
    man_prior.add('cmd_7', ProcessPriority.LOW)
    man_prior.add('cmd_8', ProcessPriority.HIGH)

    # List of processes should not change as all processes in TaskManager are of highest priority possible
    print_process_list(man_prior.list(ProcessSortCriteria.PRIORITY, ProcessSortOrder.ASC))

    man_prior.kill(to_remove1)
    man_prior.kill(to_remove2)

    # cmd_2 process no must be gone
    print_process_list(man_prior.list(ProcessSortCriteria.PRIORITY, ProcessSortOrder.ASC))

    r = man_prior.add('cmd_9', ProcessPriority.MEDIUM)
    print(f'Process {r} was added to the TaskManager with Priority update policy')
    r = man_prior.add('cmd_10', ProcessPriority.LOW)
    print(f'Process {r} was added to the TaskManager with Priority update policy')

    # List of processes with cmd_1, cmd_4, cmd_5, cmd_9, cmd_10
    print_process_list(man_prior.list(ProcessSortCriteria.PRIORITY, ProcessSortOrder.ASC))

    r = man_prior.add('cmd_11', ProcessPriority.MEDIUM)
    print(f'Process {r} was added to the TaskManager with Priority update policy')

    # List of processes but cmd_10 replaced with cmd_11 as 10 has lower priority and it is newer
    print_process_list(man_prior.list(ProcessSortCriteria.PRIORITY, ProcessSortOrder.ASC))

    to_stop_by_itself.kill()

    # As one process ended by itself, cmd_5 should disappear from the list
    print_process_list(man_prior.list(ProcessSortCriteria.PRIORITY, ProcessSortOrder.ASC))

    num_killed = man_prior.kill_group(ProcessPriority.LOW)
    print(f'Killed {num_killed} processes with LOW priority and {len(man_prior)} left')

    num_killed = man_prior.kill_group(ProcessPriority.MEDIUM)
    print(f'Killed {num_killed} processes with MEDIUM priority and {len(man_prior)} left')

    num_killed = man_prior.kill_group(ProcessPriority.HIGH)
    print(f'Killed {num_killed} processes with MEDIUM priority and {len(man_prior)} left')



    return result


if __name__ == '__main__':
    r = main()
    sys.exit(r)
