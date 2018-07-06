import requests
# TODO: Add requests to requirements

from cloudify import ctx as cloudify_ctx
from cloudify.decorators import operation
from cloudify.exceptions import RecoverableError, NonRecoverableError


def _get_instance_id_url(ctx):
    return (
        'https://{address}/nagiosrest/targets/'
        '{tenant}/{deployment}/{instance_id}'
    ).format(
        address=ctx.node.properties['nagiosrest_monitoring']['address'],
        tenant=cloudify_ctx.tenant_name,
        deployment=ctx.deployment.id,
        instance_id=ctx.instance.id,
    )


def _get_instance_ip(ctx):
    ip = ctx.node.properties['nagiosrest_monitoring']['instance_ip_property']
    try:
        return ctx.instance.runtime_properties[ip]
    except KeyError:
        return ctx.node.properties[ip]


def _get_credentials(ctx):
    props = ctx.node.properties['nagiosrest_monitoring']
    return props['username'], props['password']


def _get_cert(ctx):
    props = ctx.node.properties['nagiosrest_monitoring']
    return _FakeCertFile(props['certificate'])


class _FakeCertFile(object):
    def __init__(self, data):
        self.contents = data

    def read(self):
        return self.contents


def _make_call(ctx, request_method, data=None):
    url = _get_instance_id_url(ctx)
    result = request_method(
        url,
        auth=_get_credentials(ctx),
        json=data,
        verify=_get_cert(ctx),
    )

    if result.status_code >= 500:
        raise RecoverableError(
            'Server is currently unavailable. '
            'Call was to {url}, and '
            'response was {code}: {details}'.format(
                url=url,
                code=result.status_code,
                details=result.text,
            )
        )
    elif result.status_code >= 400:
        raise NonRecoverableError(
            'Parameters passed to server were incorrect. '
            'Call was to {url}, and '
            'response was {code}: {details}'.format(
                url=url,
                code=result.status_code,
                details=result.text,
            )
        )
    else:
        return result


@operation
def add_monitoring(ctx):
    props = ctx.node.properties['nagiosrest_monitoring']
    _make_call(
        ctx,
        requests.put,
        {
            'instance_ip': _get_instance_ip(ctx),
            'target_type': props['target_type'],
        },
    )


@operation
def remove_monitoring(ctx):
    _make_call(
        ctx,
        requests.delete,
    )
