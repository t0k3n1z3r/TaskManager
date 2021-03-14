"""
pid.py: Set of routines and data structure related to Process Identifier management.
"""
from uuid import uuid1


class PID(object):
    """A definition of Process Identifier structure which wraps internal process value into an object instance.

    Note:
        At the moment string type is used as process id as it is the most generic type. Usually process IDs are
        implemented as integers due to performance (also they are compact). But the only requirement of on PID is
        that it has to be immutable and unique which can be achieved with every data type.

        This implementation doesn't have setter for PID value, so it is read only object.

    See also:
        Look at PidGenerator class for the information about uniqueness.
    """
    def __init__(self, value: str):
        """A constructor of Process Identifier wrapping class.

        :param value: Underlying value of a Process Identifier.
        """
        self._value = value

    def __str__(self) -> str:
        """Generate string representation of Process Identifier instance.

        :return: String representation of Process Identifier.
        """
        return self.value

    @property
    def value(self) -> str:
        """Get Process Identifier value.

        :return: String representation of Process Identifier value.
        """
        return self._value


class PidGenerator(object):
    """An implementation of PID generator class which suppose to produce unique Process Identifier value on every
    request to generate function.

    Note:
        Uniqueness of PID value achieved by using UUID1 functionality which is eventually MAC address of the host
        instance and current timestamp using system clock with nanosecond precision. Internally we are using string
        representation of UUID1 value.

        Using UUID1 can help with debugging of the system as every value can be reversed to a timestamp of creation and
        exact instance (in case of centralized log collection in distributed system might be useful).

        UUID4 will be generate a random number and in most cases will be unique as well (I would say in all cases as
        probability of collision is exceptionally low, but still) but UUID1 suits better this purpose.

        UUID1 might be not the best choice in case there is a security concern about instance MAC address, but there is
        no requirement related to security.
    """
    @staticmethod
    def generate() -> PID:
        """Generate new Process Identifier value and wrap it into PID object.

        Note:
            This method is static, as at the moment there is no need in preserving any state of the object. But in case
            state of the PID generator has to be stored (for instance in case when integer type needed) it can be
            moved to class method instead with the same signature.

            As this class is not exposed as a public interface changing it's state shouldn't be a big deal.

        :return: PID object.
        """
        pid_value = str(uuid1())
        return PID(str(pid_value))
