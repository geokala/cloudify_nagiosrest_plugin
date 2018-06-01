import requests
# TODO: Add requests to requirements

from cloudify import ctx as cloudify_ctx
from cloudify.decorators import operation
from cloudify.exceptions import RecoverableError, NonRecoverableError


def _get_instance_id_url(address, instance_id):
    # TODO: HTTPS
    return 'http://{address}/nagiosrest/{instance_id}'.format(
        address=address,
        instance_id=instance_id,
    )


def _get_instance_ip(ctx, property_name):
    try:
        return ctx.instance.runtime_properties[property_name]
    except KeyError:
        return ctx.node.properties[property_name]


def _make_call(request_method, url, username, password, data=None):
    result = request_method(
        url,
        auth=(username, password),
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
def add_monitoring(ctx,
                   nagiosrest_address, nagiosrest_user, nagiosrest_pass,
                   target_type, heal_on_failure,
                   instance_ip_property):
    _make_call(
        requests.put,
        _get_instance_id_url(nagiosrest_address, ctx.instance.id),
        nagiosrest_user, nagiosrest_pass,
        {
            'instance_ip': _get_instance_ip(ctx, instance_ip_property),
            'tenant': cloudify_ctx.tenant_name,
            'deployment': ctx.deployment.id,
            'target_type': target_type,
            'heal_on_failure': heal_on_failure,
        },
    )


@operation
def remove_monitoring(ctx, nagiosrest_address, nagiosrest_user,
                      nagiosrest_pass):
    _make_call(
        requests.delete,
        _get_instance_id_url(nagiosrest_address, ctx.instance.id),
        nagiosrest_user,
        nagiosrest_pass,
    )
