# TASK MANAGER

Explanation to all decisions provided in the comments to the code. This is the simplest way to explain the idea behind
each and every decision.

# Key points
1. Top level interface for the user is a TaskManager class which has the following methods:
    1. `TaskManager.add` - Add new process based on command and priority into the system.
    2. `TaskManager.kill` - Terminate process based on process descriptor returned by `TaskManager.add` function.
    3. `TaskManager.kill_group` - Terminate all processes in the system based on priority.
    4. `TaskManager.kill_all` - Terminal all processes in the system.
    
2. `TaskManager.add` function returns instance of `Process` class which shall be considered as a descriptor. Interface
allows getting access to all key fields without.
   
3. User can call `Process.kill` and TaskManager will be notified about this. Such approach allows much safer resource
management.
   
4. Constructor of `TaskManager` accepts different type of Storage which would change behavior of `TaskManager.add` 
interface depending on what is needed. Basically this allows extensibility of the solution. Also simplifies testing 
   after a new feature is added.
   
5. PID wrapped into a separate class with `PID.value` property. In case something (type of PID) has to be changed no
major impact is required.
   
6. Process ID (PID) generated based on UUID1 which would guarantee uniqueness.

7. Primary data structure to store collection of `Process` objects is dictionary (Hashmap). As there are many
requirements there is no data structure which would satisfy all in optimal way. In some cases PriorityQueue or Queue can
   be used to have optimal implementation of `TaskManager.list` function but then `TaskManager.kill` would suffer.
   At the end the trade-off is to have O(1) insertion and deletion complexity (add, kill)
   and O(n) on `TaskManager.list`.
   
8. Build time is simulated by python import with environment variable.

# Run instructions
Entry point to the project will main.py in the root folder. This file contains set of usage examples for TaskManager.
In order to run it you would need python3 installed on your system and execute:

    python3 main.py

With python2 you most likely will see invalid syntax exception. This solution doesn't use anything which is not
available in python2 except richer syntax for `type` declaration. So, it's easier for reader to understand what type
of data expected on input and output of each function.
