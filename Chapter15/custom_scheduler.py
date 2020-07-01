from kubernetes import client, config, watch


def schedule_pod(cli, name):
    target = client.V1ObjectReference()
    target.kind = 'Node'
    target.apiVersion = 'v1'
    target.name = 'k3d-k3s-default-worker-1'
    meta = client.V1ObjectMeta()
    meta.name = name
    body = client.V1Binding(metadata=meta, target=target)
    return cli.create_namespaced_binding('default', body)


def main():
    config.load_kube_config()
    cli = client.CoreV1Api()
    print('Waiting for pods to schedule')
    w = watch.Watch()
    for event in w.stream(cli.list_namespaced_pod, 'default'):
        o = event['object']
        if o.status.phase != 'Pending' or o.spec.scheduler_name != 'custom-scheduler':
            print('Ignoring pod', o.metadata.name)
            continue

        print ('Scheduling pod', o.metadata.name)
        schedule_pod(cli, o.metadata.name)


if __name__ == '__main__':
    main()
