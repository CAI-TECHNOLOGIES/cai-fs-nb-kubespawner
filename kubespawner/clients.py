"""Shared clients for kubernetes

avoids creating multiple kubernetes client objects,
each of which spawns an unused max-size thread pool
"""
import weakref
from unittest.mock import Mock

import kubernetes_asyncio.client
from kubernetes_asyncio.client import api_client
from kubernetes_asyncio.client import Configuration

# FIXME: remove when instantiating a kubernetes client
# doesn't create N-CPUs threads unconditionally.
# monkeypatch threadpool in kubernetes api_client
# to avoid instantiating ThreadPools.
# This is known to work for kubernetes-4.0
# and may need updating with later kubernetes clients
_dummy_pool = Mock()
api_client.ThreadPool = lambda *args, **kwargs: _dummy_pool

_client_cache = {}


def shared_client(ClientType, *args, **kwargs):
    """Return a single shared kubernetes client instance

    A weak reference to the instance is cached,
    so that concurrent calls to shared_client
    will all return the same instance until
    all references to the client are cleared.

    You should usually await load_config before calling this.
    """
    kwarg_key = tuple((key, kwargs[key]) for key in sorted(kwargs))
    cache_key = (ClientType, args, kwarg_key)
    client = None
    if cache_key in _client_cache:
        # resolve cached weakref
        # client can still be None after this!
        client = _client_cache[cache_key]()

    if client is None:
        # Kubernetes client configuration is handled globally
        # in kubernetes.py and is already called in spawner.py
        # or proxy.py prior to a shared_client being instantiated
        Client = getattr(kubernetes_asyncio.client, ClientType)
        client = Client(*args, **kwargs)
        # cache weakref so that clients can be garbage collected
        _client_cache[cache_key] = weakref.ref(client)

    return client


async def load_config(caller=None):
    try:
        kubernetes_asyncio.config.load_incluster_config()
    except kubernetes_asyncio.config.ConfigException:
        await kubernetes_asyncio.config.load_kube_config()
    # The ca_cert/k8s_api_host is set via traitlets on the objects
    # that call load_config(); thus, they may pass a reference to themselves
    # into load_config in order to set ca_cert/k8s_api_host.

    if caller:
        if hasattr(caller, "k8s_api_ssl_ca_cert") and caller.k8s_api_ssl_ca_cert:
            global_conf = Configuration.get_default_copy()
            global_conf.ssl_ca_cert = caller.k8s_api_ssl_ca_cert
            Configuration.set_default(global_conf)
        if hasattr(caller, "k8s_api_host") and caller.k8s_api_host:
            global_conf = Configuration.get_default_copy()
            global_conf.host = caller.k8s_api_host
            Configuration.set_default(global_conf)
