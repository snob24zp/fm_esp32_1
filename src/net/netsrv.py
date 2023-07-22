from net.netcl import netcl

class netsrv(netcl):
    def __init__(self, host: str, port: int, log_prefix='') -> None:
        super().__init__(host, port, log_prefix)

    def fork(self):
        return self
