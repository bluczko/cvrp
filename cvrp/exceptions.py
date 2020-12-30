class CVRPException(Exception):
    message = "Problem nie ma rozwiązania rozwiązania."


class NoClientsException(CVRPException):
    message = "Nie dodano klientów."


class NoVehiclesException(CVRPException):
    message = "Nie dodano pojazdów."


class MaxCapacityOverloadException(CVRPException):
    message = "Największe zapotrzebowanie klienta jest większe niż największa pojemność pojazdów."


class SumCapacityOverloadException(CVRPException):
    message = "Całkowite zapotrzebowanie klientów jest większe niż całkowita pojemność pojazdów."
