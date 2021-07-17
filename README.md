# GNMIStub

Sample usage:

```
from GNMIStub import GNMIStub

models = ["Cisco-IOS-XR-ipv4-bgp-oper:bgp/instances/instance/instance-active/default-vrf/process-info"]
pem_file = "/home/foo/pem_files/rr-1_10.194.51.87.pem"
ip = "10.194.51.87"
username = "someuser"
password = "somepassword"
sample_interval = 30
mode = "SAMPLE"
stream = "STREAM"
encoding = "JSON_IETF"

stub = GNMIStub(pem_file=pem_file,
                ip=ip,
                username=username,
                password=password,
                sample_interval=sample_interval,
                mode=mode,
                stream=stream,
                encoding=encoding,
                models=models)

stub.connect()
```
