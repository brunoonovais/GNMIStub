# GNMIStub

GNMIStub is a simple library for GNMI Subscriptions.
Will be later enhanced to support Get.

- Pre-Requisites:

Introduction to GNMI: https://community.cisco.com/t5/service-providers-documents/understanding-gnmi-on-ios-xr-with-python/ta-p/4014205
To install libraries:

```pip install gnmi-proto grpcio-tools```

- Sample usage:

```
from GNMIStub import GNMIStub

models = ['Cisco-IOS-XR-ipv4-bgp-oper:bgp/instances/instance/instance-active/update-generation-process/update-out-queue-messages']
pem_file = "./pem_files/rr-1_10.194.51.87.pem"
ip = "10.194.51.87"
username = "root"
password = "somepass"
sample_interval = 10
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

# subscribe
stub.connect()

# get with models specified during object creation
stub.get()

# get with models specified during get method
stub.get(models=['Cisco-IOS-XR-ipv4-bgp-oper:bgp/instances/instance[instance-name="default"]/instance-active/default-vrf/process-info/global/established-neighbors-count-total'])
```
