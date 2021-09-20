from typing import List
import grpc
import json
import re
import time
from protos.gnmi_pb2_grpc import gNMIStub
from protos.gnmi_pb2 import (
    GetRequest,
    GetResponse,
    Path,
    PathElem,
    Encoding,
    SetRequest,
    Update,
    TypedValue,
    SetResponse,
    Notification,
    Subscription,
    SubscriptionMode,
    SubscriptionList,
    SubscribeRequest
)

class GNMIStub:
    """
    Creates a gRPC connection to a device and issues gNMI requests
    """

    def __init__(self,
                 pem_file: str,
                 ip: str,
                 username: str,
                 password: str,
                 sample_interval: int,
                 mode: str,
                 stream: str,
                 encoding: str,
                 models: List,
                 port: str = "57400",
                 keys_file: str = None,
                 options: List=None):
        if options is None:
            self.options = [("grpc.ssl_target_name_override", "ems.cisco.com")]
        else:
            self.options: List[Tuple[str, str]] = options
        if pem_file is not None:
            self.pem_file: str = pem_file
            with open(self.pem_file, "rb") as fp:
                self.pem_bytes: bytes = fp.read()
        else:
            raise Exception('PEM file needs to be specified')
        self.ip: str = ip
        self.username: str = username
        self.password: str = password
        self.metadata = [('username', self.username), ('password', self.password)]
        self.port: str = port
        self.options: List[Tuple[str, str]] = [('grpc.ssl_target_name_override', 'ems.cisco.com'), ('grpc.max_receive_message_length', 1000000000)]
        self._connected: bool = False
        self.sample_interval: int = sample_interval
        # SAMPLE, ON_CHANGE or TARGET_DEFINED
        self.mode: str = mode
        # STREAM, ONCE or POLL
        self.stream: str = stream
        # PROTO or JSON_IETF
        self.encoding: str = encoding
        self.models: List = models
        self.channel = None
        self.gnmi_stub = None
        self.subscription_list: List = []

    @staticmethod
    def _create_gnmi_path(path) -> Path:
        path_elements = []
        if path[0] == '/':
            if path[-1] == '/':
                path_list = re.split(r'''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:-1]
            else:
                path_list = re.split(r'''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:]
        else:
            if path[-1] == '/':
                path_list = re.split(r'''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[:-1]
            else:
                path_list = re.split(r'''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)
                #print(f'path_list = {path_list}')
        for elem in path_list:
            elem_name = elem.split("[", 1)[0]
            #print(f'elem_name = {elem_name}')
            elem_keys = re.findall(r'\[(.*?)\]', elem)
            #print(f'elem_keys = {elem_keys}')
            dict_keys = dict(x.split('=', 1) for x in elem_keys)
            #print(f'dict_keys = {dict_keys}')
            path_elements.append(PathElem(name=elem_name, key=dict_keys))
        return Path(elem=path_elements)

    def connect(self) -> None:
        try:
            self._setup_credentials()
            self.channel = grpc.secure_channel(':'.join([self.ip, self.port]), self.credentials, self.options)
            grpc.channel_ready_future(self.channel).result(timeout=30)
            self.gnmi_stub = gNMIStub(self.channel)
            self._create_subscriptions(self.models)
            self._create_subscription_list()
    
            for _response in self.gnmi_stub.Subscribe(self._subscribe_to_path(self.gnmi_subscribe_request), metadata=self.metadata):
                print(_response)
        except grpc.FutureTimeoutError as e:
            print(f"Timeout to {self.ip}. Exception:\n\n{e}")

    def _setup_credentials(self) -> None:
        self.credentials = grpc.ssl_channel_credentials(self.pem_bytes)

    def _create_subscriptions(self, models):
        # for each model we will create a subscription and append to subscription_list
        for _model in models:
            self._path = self._create_gnmi_path(_model)
            self._sub_mode = SubscriptionMode.Value(self.mode)
            self._subscription = Subscription(path=self._path, mode=self._sub_mode, sample_interval=self.sample_interval*1000000000)
            self.subscription_list.append(self._subscription)
    
    def _create_subscription_list(self):
        self.gnmi_subscription_list_mode = SubscriptionList.Mode.Value(self.stream)
        self.gnmi_encoding = Encoding.Value(self.encoding)
        self.gnmi_subscription_list = SubscriptionList(subscription=self.subscription_list,
                                                       mode=self.gnmi_subscription_list_mode)
        self.gnmi_subscribe_request = SubscribeRequest(subscribe=self.gnmi_subscription_list)

    def _subscribe_to_path(self, request):
        yield request
    
    def get(self, models=None, display=True) -> List:

        try:
            self._setup_credentials()
            self.channel = grpc.secure_channel(':'.join([self.ip, self.port]), self.credentials, self.options)
            grpc.channel_ready_future(self.channel).result(timeout=30)
            self.gnmi_stub = gNMIStub(self.channel)

            if models:
                self.path_list = [self._create_gnmi_path(model) for model in models]
            else:
                self.path_list = [self._create_gnmi_path(model) for model in self.models]
            self.get_message = GetRequest(path=self.path_list, type=0, encoding=4)
            _output = self.gnmi_stub.Get(self.get_message, metadata=self.metadata)

            for notification in _output.notification:
                for update in notification.update:
                    val = update.val.json_ietf_val
                    print(val)

        except grpc.FutureTimeoutError as e:
            print(f"Timeout to {self.ip}. Exception:\n\n{e}")
