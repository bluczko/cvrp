class CVRPException(Exception):
    message = "The problem has no solution."


class NoClientsException(CVRPException):
    message = "No clients have been added."


class NoVehiclesException(CVRPException):
    message = "No vehicles have been added."


class MaxCapacityOverloadException(CVRPException):
    message = "The largest client demand exceeds the maximum vehicle capacity."


class SumCapacityOverloadException(CVRPException):
    message = "The total client demand exceeds the total vehicle capacity."
