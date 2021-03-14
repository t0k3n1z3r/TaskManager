"""
config.py: Simulation of build type where task manager capacity defined once.
"""
import os

"""Get information about max process storage capacity from the environment. Since python is an interpreter, this will
simulate build time definition.
"""
PROCESS_STORAGE_CAPACITY = os.getenv('MAX_PROCESSES', 5)
