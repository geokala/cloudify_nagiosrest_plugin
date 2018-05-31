import requests
# TODO: Add requests to requirements

from cloudify import ctx as cloudify_ctx
from cloudify.decorators import operation


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


@operation
def add_monitoring(ctx,
                   nagiosrest_address, nagiosrest_user, nagiosrest_pass,
                   target_type, heal_on_failure,
                   instance_ip_property):
    # TODO: Do some error handling
    requests.put(
        _get_instance_id_url(nagiosrest_address, ctx.instance.id),
        auth=(nagiosrest_user, nagiosrest_pass),
        json={
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
    # TODO: Do some error handling
    requests.delete(
        _get_instance_id_url(nagiosrest_address, ctx.instance.id),
        auth=(nagiosrest_user, nagiosrest_pass),
    )
