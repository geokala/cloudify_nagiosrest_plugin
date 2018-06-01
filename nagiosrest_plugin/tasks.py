import requests
# TODO: Add requests to requirements

from cloudify import ctx as cloudify_ctx
from cloudify.decorators import operation
from cloudify.exceptions import RecoverableError, NonRecoverableError


def _get_instance_id_url(ctx):
    # TODO: HTTPS
    return 'http://{address}/nagiosrest/targets/{instance_id}'.format(
        address=ctx.node.properties['nagiosrest_monitoring']['address'],
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


def _make_call(ctx, request_method, data=None):
    result = request_method(
        _get_instance_id_url(ctx),
        auth=_get_credentials(ctx),
        json=data,
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
        requests.put,
        {
            'instance_ip': _get_instance_ip(ctx),
            'tenant': cloudify_ctx.tenant_name,
            'deployment': ctx.deployment.id,
            'target_type': props['target_type'],
            'heal_on_failure': props['heal_on_failure'],
        },
    )


@operation
def remove_monitoring(ctx):
    _make_call(
        requests.delete,
    )
