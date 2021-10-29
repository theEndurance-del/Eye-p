# This is the port prober module which just scans for open ports on a given thost


# Imports
import socket
import concurrent.futures
from config import colors
from modules.util.utils import datevalue, timestamp
from rich import traceback, progress
traceback.install()

# Additional colors
BALERT:   str = colors.BALERT
FSUCCESS: str = colors.FSUCCESS
FNORMAL:  str = colors.FNORMAL
BURGENT:  str = colors.BURGENT
FALERT:   str = colors.FALERT
BNORMAL:  str = colors.BNORMAL

# Lists for presenting output
results: list = []
openports: list = []

# List of valid protocols to be used with this module
valid_protocols: list = ['tcp', 'tcp/ip', 'TCP', 'TCP/IP', 'udp', 'UDP']

class portprobe:
    def __init__(self,
            thost: str,
            tport: dict,
            timeout: int,
            protocol: str,
            tryct: int,
            verbose: bool,
            threading: bool
        ):
        self.thost = thost
        self.tport = tport
        self.timeout = timeout if timeout else 1
        self.protocol = protocol
        self.tryct = tryct if tryct else 1
        self.verbose = verbose
        self.threading = threading
        pass


    def __getServbyPort(self, port, protocol):
        """Get the service name based on the port."""

        try:
            name = socket.getservbyport(int(port), protocol)
            return name
        except:
            return False

    def __tscanner(self, port: int):
        """TCP port scanner function."""
        host = self.thost
        timeout = self.timeout
        verbose = self.verbose

        socktcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            socktcp.settimeout(timeout)
            socktcp.connect((host, port))
            return True

        except Exception as exp:
            if self.threading:
                print('[-]', FALERT, port, exp, FNORMAL, " "*(len(str(exp))*3), end="\r")
            return False

        finally:
            socktcp.close()

    def __uscanner(self, port: int):
        """UDP port scanner function."""
        host = self.thost
        timeout = self.timeout
        tryct = self.tryct
        verbose = self.verbose
        portstatus = False
        sockudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sockicmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        for _ in range(tryct):
            try:
                sockudp.sendto(bytes('This is a test', 'utf-8'), (host, port))
                sockicmp.settimeout(timeout)
                sockicmp.recvfrom(1024)

            except socket.timeout:
                serv = self.__getServbyPort(port, 'udp')

                if not serv:
                    if verbose:
                        print(f'{BALERT}[*] Error: Service on port: {port} not found{BNORMAL}')
                    portstatus = False
                else:
                    portstatus = True

            except socket.error as e:
                portstatus = False

            finally:
                sockudp.close()
                sockicmp.close()

        return portstatus

    def __scanner(self, port):
        """Starts the actual scanner session"""

        if self.protocol in ['tcp', 'tcp/ip', 'TCP', 'TCP/IP']:
            if self.__tscanner(port):
                serv = self.__getServbyPort(port, 'tcp') if self.__getServbyPort(port, 'tcp') else 'Undefined'

                return f'{FSUCCESS}[+] {self.protocol}: {self.thost}: {port} is open, service: {serv}{FNORMAL}'
            elif self.verbose:
                return f'{FALERT}[-] {self.protocol}: {self.thost}: {port} is closed{FNORMAL}'

        elif protocol in ['udp', 'UDP']:
            if self.__uscanner(port):
                serv = self.__getServbyPort(port, 'udp') if self.__getServbyPort(port, 'udp') else 'Undefined'

                return f'{FSUCCESS}[+] {self.protocol}: {self.thost}: {port} is open, service: {serv}{FNORMAL}'
            elif self.verbose:
                return f'{FALERT}[-] {self.protocol}: {self.thost}: {port} is closed{FNORMAL}'

    def display(self):
        """
        Displays the output.
        Also provides multithreading it the port input is a list.
        """

        if self.protocol in valid_protocols:
            # Check if the specified protocol is valid
            executor = concurrent.futures.ThreadPoolExecutor()
            # check if input is a single port or a range
            type = self.tport['type']
            port = self.tport
            print(f'{BURGENT}[**] Scan started at {datevalue()}{BNORMAL}')
            start = timestamp()

            if type == 'single':
                single_port: int = self.tport['value']
                portstatus = __scanner(self.thost, single_port, timeout, protocol, tryct)
                if portstatus:
                    print(portstatus)
                else:
                    print(f'{protocol}: {host}: {single_port} is closed')

            else:
                try:
                    if type == 'range':
                        p_begin: int = int(port['value'][0])
                        p_end: int = int(port['value'][1])+1

                    if self.threading:
                        # Initiate multi-threaded process
                        if type == 'range':
                            output = [ executor.submit(self.__scanner, x) for x in range(p_begin, p_end) ]
                        else:
                            output = [ executor.submit(self.__scanner, x) for x in port['value'] ]

                        for f in concurrent.futures.as_completed(output):
                            if f.result():
                                # Prevents unnecessary output if verbose is set to false
                                results.append(f.result())
                    else:
                        if type == 'range':
                            output = [ self.__scanner(x) for x in progress.track(range(p_begin, p_end), description=f"Scanning {self.protocol}") ]
                        else:
                            output = [ self.__scanner(int(x)) for x in port['value'] ]

                        for x in output:
                            if x:
                                results.append(x)

                        output.clear()

                    if self.verbose:
                        # Finally print the value on the basis of what value was set to verbose
                        for x in results:
                            if 'open' in x:
                                openports.append(x)
                            print(x)

                        print('-'*60)
                        for y in openports:
                            print(y)

                        results.clear()
                        openports.clear()

                    else:
                        for x in results:
                            print(x)
                    results.clear()

                except KeyboardInterrupt:
                    print(f'{FALERT}Keyboard interrupt received, quitting!!')
                    if self.threading:
                        executor.shutdown(wait=False, cancel_futures=True)

            end = timestamp()            
            print(f'{BURGENT}[**] Scan took about {round(end-start, 5)} sec(s).{BNORMAL}')

        else:
            print(f'{BALERT}[-] Error: Unknown protocol specified{BNORMAL}')