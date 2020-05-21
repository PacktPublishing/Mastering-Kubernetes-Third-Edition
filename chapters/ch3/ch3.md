# High Availability and Reliability

In _Chapter 2_, _Creating Kubernetes Clusters_, we learned how to create Kubernetes clusters in different environments, experimented with different tools, and created a couple of clusters. Creating a Kubernetes cluster is just the beginning of the story. Once the cluster is up and running, you need to make it sure it is stays operational.

In this chapter, we will dive into the topic of highly available clusters. This is a complicated topic. The Kubernetes project and the community haven't settled on one true way to achieve high availability nirvana. There are many aspects to highly available Kubernetes clusters, such as ensuring that the control plane can keep functioning in the face of failures, protecting the cluster state in etcd, protecting the system's data, and recovering capacity and/or performance quickly. Different systems will have different reliability and availability requirements. How to design and implement a highly available Kubernetes cluster will depend on those requirements.

At the end of this chapter, you will understand the various concepts associated with high availability and be familiar with Kubernetes high availability best practices and when to employ them. You will be able to upgrade live clusters using different strategies and techniques, and you will be able to choose between multiple possible solutions based on trade-offs between performance, cost, and availability.

# High-availability concepts

In this section, we will start our journey into high availability by exploring the concepts and building blocks of reliable and highly available systems. The million (trillion?) dollar question is, how do we build reliable and highly available systems from unreliable components? Components will fail; you can take that to the bank. Hardware will fail. Networks will fail; configuration will be wrong; software will have bugs; people will make mistakes. Accepting that, we need to design a system that can be reliable and highly available even when components fail. The idea is to start with redundancy, detect component failure, and replace bad components quickly.

## Redundancy

**Redundancy** is the foundation of reliable and highly available systems at the hardware and data levels. If a critical component fails and you want the system to keep running, you must have another identical component ready to go. Kubernetes itself takes care of your stateless pods via replication controllers and replica sets. But, your cluster state in etcd and the master components themselves need redundancy to function when some components fail. In addition, if your system's tasteful components are not backed up by redundant storage (for example, on a cloud platform) then you need to add redundancy to prevent data loss.

## Hot swapping

**Hot swapping** is the concept of replacing a failed component on the fly without taking the system down, with minimal (ideally, zero) interruption to users. If the component is stateless (or its state is stored in separate redundant storage), then hot swapping a new component to replace it is easy and just involves redirecting all clients to the new component. But, if it stores local state, including in memory, then hot swapping is not trivial. There are two main options:

- Give up on in-flight transactions
- Keep a hot replica in sync

The first solution is much simpler. Most systems are resilient enough to cope with failures. Clients can retry failed requests and the hot-swapped component will service them.

The second solution is more complicated and fragile, and will incur a performance overhead because every interaction must be replicated to both copies (and acknowledged). It may be necessary for some parts of the system.

## Leader election

Leader or master election is a common pattern in distributed systems. You often have multiple identical components that collaborate and share the load, but one component is elected as the leader and certain operations are serialized through the leader. You can think of distributed systems with leader election as a combination of redundancy and hot swapping. The components are all redundant and, when the current leader fails or becomes unavailable, a new leader is elected and hot-swapped in.

## Smart load balancing

Load balancing is about distributing the workload across multiple replicas that service incoming requests. This is useful for scaling up and down under heavy load by adjusting the number of replicas. When some replicas fail the load balancer  will stop sending requests to failed or unreachable components. Kubernetes will provision new replicas are provisioned, restore capacity and update the load balancer. Kubernetes provides great facilities to support this via services, endpoints, replica sets, labels and ingress controllers.

## Idempotency

Many types of failure can be temporary. This is most common with networking issues or with too-stringent timeouts. A component that doesn't respond to a health check will be considered unreachable and another component will take its place. Work that was scheduled to the presumably failed component may be sent to another component. But the original component may still be working and complete the same work. The end result is that the same work may be performed twice. It is very difficult to avoid this situation. To support exactly once semantics, you need to pay a heavy price in overhead, performance, latency, and complexity. Thus, most systems opt to support at-least-once semantics, which means it is OK for the same work to be performed multiple times without violating the system's data integrity. This property is called idempotency. Idempotent systems maintain their state if an operation is performed multiple times.

## Self-healing

When component failures occur in dynamic systems, you usually want the system to be able to heal itself. Kubernetes replication controllers and replica sets are great examples of self-healing systems. But failure can extend well beyond pods.  Self-healing starts with automated detection of problems followed by automated resolution. Quotas and limits help create checks and balances to ensure an automated self-healing doesn't run amok due to unpredictable circumstances such as DDOS attacks. Self-healing systems deal very well with transient failures by retrying failed operations and escalating failures only when it's clear there is no other option. Some self-healing systems have fallback paths like serving cached content if up to date content is unavailable. Self-healing systems attempt to degrade gracefully and keep working until the core issue can be fixed.

In this section, we considered various concepts involved in creating reliable and highly available systems. In the next section, we will apply them and demonstrate best practices for systems deployed on Kubernetes clusters.

# High-availability best practices

Building reliable and highly available distributed systems is a non-trivial endeavor. In this section, we will check some of the best practices that enable a Kubernetes-based system to function reliably and be available in the face of various failure categories. We will also dive deep and see how to go about constructing your own HA clusters. Note that you should roll your own HA Kubernetes cluster only in very special cases. Tools such as Kubespray provide battle tested ways to create HA clusters. You should take advantage of all the work and effort that went into these tools.

## Creating highly available clusters

To create a highly available Kubernetes cluster, the master components must be redundant. That means etcd must be deployed as a cluster (typically across three or five nodes) and the Kubernetes API server must be redundant. Auxiliary cluster-management services such as Heapster's storage may be deployed redundantly too, if necessary. The following diagram depicts a typical reliable and highly available Kubernetes cluster in a stacked etcd topology. There are several load-balanced master nodes, each one containing whole master components as well as an etcd component:

???? images/ch3 - stacked etcd ????


This is not the only way to configure highly available clusters. You may prefer, for example, to deploy a standalone etcd cluster to optimize the machines to their workload or if you require more redundancy for your etcd cluster than the rest of the master nodes.

The following diagram shows a Kubernetes cluster where etcd is deployed as an external cluster

???? images/ch3 - external etcd ????


Self-hosted Kubernetes where control plane components are deployed as pods and stateful sets in the cluster is a great approach to simplify the robustness, disaster recovery and self-healing of the control plane components by applying Kubernetes to Kubernetes.

## Making your nodes reliable

Nodes will fail, or some components will fail, but many failures are transient. The basic guarantee is to make sure that the Docker daemon (or whatever the CRI implementation is) and the kubelet restart automatically in case of a failure.

If you run CoreOS, a modern Debian-based OS (including Ubuntu >= 16.04), or any other OS that uses systemd as its init mechanism, then it's easy to deploy Docker and the kubelet as self-starting daemons:

systemctl enable docker
systemctl enable kublet

For other operating systems, the Kubernetes project selected monit for their high-availability example, but you can use any process monitor you prefer. The main requirement is to make those two critical components will restart in case of failure without external intervention.

## Protecting your cluster state

The Kubernetes cluster state is stored in etcd. The etcd cluster was designed to be super reliable and distributed across multiple nodes. It's important to take advantage of these capabilities for a reliable and highly available Kubernetes cluster.

### Clustering etcd

You should have at least three nodes in your etcd cluster. If you need more reliability and redundancy, you can go five, seven, or any other odd number of nodes. The number of nodes must be odd to have a clear majority in case of a network split.

In order to create a cluster, the etcd nodes should be able to discover each other. There are several methods to accomplish that. I recommend using the excellent etcd-operator from CoreOS.


???? images/ch3 - etcd operator 

The operator takes care of many complicated aspects of etcd operation such as:

- Create and Destroy
- Resize
- Failover
- Rolling Upgrade
- Backup and Restore

#### Installing the etcd Operator

The easiest way to install the etcd operator is using Helm – the Kubernetes package manager. 
If you don't have Helm installed yet follow the instructions here: https://github.com/kubernetes/helm#install.

Next, save the following YAML to helm-rbac.yaml

```

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: tiller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: tiller
    namespace: kube-system 
```

This creates a service account for Tiller and gives it a cluster admin role.

```
$ k apply -f helm-rbac.yaml
serviceaccount/tiller created
clusterrolebinding.rbac.authorization.k8s.io/tiller created
```


Then initialize helm with the tiller service account :

```
$ helm init --service-account tiller
$HELM_HOME has been configured at /Users/gigi.sayfan/.helm.

Tiller (the Helm server-side component) has been installed into your Kubernetes Cluster.

Please note: by default, Tiller is deployed with an insecure 'allow unauthenticated users' policy.
To prevent this, run `helm init` with the --tiller-tls-verify flag.
For more information on securing your installation see: https://docs.helm.sh/using_helm/#securing-your-helm-installation
```

Don't worry about the warnings at this point. We will dive deep into Helm in Chapter 13 – Handling the Kubernetes Package Manager. For now, we'll just use it to install the etcd operator. We need to allow helm to install components into the default namespace. We will cover role-based access control in detail later in the book. Here is the helm-rbac.yaml file that allows it:

```
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: tiller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: tiller
  namespace: kube-system
```

You can apply it like any other Kubernetes manifest:

```
$ k apply -f helm-rbac.yaml
serviceaccount/tiller created
clusterrolebinding.rbac.authorization.k8s.io/tiller created
```

 Now, we can finally install the etcd-operator. I use "x" as a short release name to make the output less verbose. You may want to use more meaningful names:

```
$ helm install stable/etcd-operator --name x
NAME:   x
LAST DEPLOYED: Fri Aug  2 17:08:13 2019
NAMESPACE: default
STATUS: DEPLOYED

RESOURCES:
==> v1/Pod(related)
NAME                                                   READY  STATUS   RESTARTS  AGE
x-etcd-operator-etcd-backup-operator-dffcbd97-hfsnc    0/1    Pending  0         0s
x-etcd-operator-etcd-operator-669975754b-vhhq5         0/1    Pending  0         0s
x-etcd-operator-etcd-restore-operator-6b787cc5c-6dk77  0/1    Pending  0         0s

==> v1/Service
NAME                   TYPE       CLUSTER-IP     EXTERNAL-IP  PORT(S)    AGE
etcd-restore-operator  ClusterIP  10.43.182.231  <none>       19999/TCP  0s

==> v1/ServiceAccount
NAME                                   SECRETS  AGE
x-etcd-operator-etcd-backup-operator   1        0s
x-etcd-operator-etcd-operator          1        0s
x-etcd-operator-etcd-restore-operator  1        0s

==> v1beta1/ClusterRole
NAME                           AGE
x-etcd-operator-etcd-operator  0s

==> v1beta1/ClusterRoleBinding
NAME                                   AGE
x-etcd-operator-etcd-backup-operator   0s
x-etcd-operator-etcd-operator          0s
x-etcd-operator-etcd-restore-operator  0s

==> v1beta2/Deployment
NAME                                   READY  UP-TO-DATE  AVAILABLE  AGE
x-etcd-operator-etcd-backup-operator   0/1    1           0          0s
x-etcd-operator-etcd-operator          0/1    1           0          0s
x-etcd-operator-etcd-restore-operator  0/1    1           0          0s


NOTES:
1. etcd-operator deployed.
  If you would like to deploy an etcd-cluster set cluster.enabled to true in values.yaml
  Check the etcd-operator logs
    export POD=$(kubectl get pods -l app=x-etcd-operator-etcd-operator --namespace default --output name)
    kubectl logs $POD --namespace=default
```   
    
Now, that the operator is installed we can use it to create the etcd cluster:    
    
#### Creating the etcd Cluster

Save the following to etcd-cluster.yaml:

```
apiVersion: "etcd.database.coreos.com/v1beta2"
kind: "EtcdCluster"
metadata:
  name: "example-etcd-cluster"
spec:
  size: 3
  version: "3.2.13"
```

To create the cluster type:

```
$ k create -f etcd-cluster.yaml
etcdcluster.etcd.database.coreos.com/etcd-cluster created
```

Let's verify the cluster pods were created properly:

```
$ k get pods -o wide | grep etcd-cluster
etcd-cluster-2fs2lpz7p7      1/1     Running   0     2m53s   10.42.2.4   k3d-k3s-default-worker-1
etcd-cluster-58547r5f6x      1/1     Running   0     3m49s   10.42.1.5   k3d-k3s-default-worker-0
etcd-cluster-z7s4bfksdl      1/1     Running   0     117s    10.42.3.5   k3d-k3s-default-worker-2
```

As you can see each etcd pod was scheduled to run on a different node. This is exactly what we want to a redundant datastore like etcd.


!!!!!! INFO !!!!!!!

The -o wide format for kubectl get command provides additional information. For the get pods command
the node the pod is scheduled on 

!!!!!!!!!!!!!!!!!!!


### Verifying the etcd cluster

Once the etcd cluster is up and running you can access it with the etcdctl tool to check on the cluster status and health. Kubernetes lets you execute commands directly inside pods or container via the exec command (similar to docker exec).

Here is how to check if the cluster is healthy:

```
$ k exec etcd-cluster-2fs2lpz7p7 etcdctl cluster-health

member 1691519f36d795b7 is healthy: got healthy result from http://etcd-cluster-2fs2lpz7p7.etcd-cluster.default.svc:2379
member 1b67c8cb37fca67e is healthy: got healthy result from http://etcd-cluster-58547r5f6x.etcd-cluster.default.svc:2379
member 3d4cbb73aeb3a077 is healthy: got healthy result from http://etcd-cluster-z7s4bfksdl.etcd-cluster.default.svc:2379
cluster is healthy
```


Here is to how to set and get key value pairs:

```
$ k exec etcd-cluster-2fs2lpz7p7 etcdctl set test "Yeah, it works"
Yeah, it works

$ k exec etcd-cluster-2fs2lpz7p7 etcdctl get test
Yeah, it works
```

## Protecting your data

Protecting the cluster state and configuration is great, but even more important is protecting your own data. If somehow the cluster state gets corrupted, you can always rebuild the cluster from scratch (although the cluster will not be available during the rebuild). But if your own data is corrupted or lost, you're in deep trouble. The same rules apply; redundancy is king. But while the Kubernetes cluster state is very dynamic, much of your data is maybe less dynamic. For example, a lot of historic data is often important and can be backed up and restored. Live data might be lost, but the overall system may be restored to an earlier snapshot and suffer only temporary damage.

You should consider Velero as a solution for backing up your entire cluster including your own data. Heptio (now part of VMWare) developed Velero, which is open source and may be a life saver for critical systems.

Check it out here: https://velero.io/

## Running redundant API servers

The API servers are stateless, fetching all the necessary data on the fly from etcd cluster. This means that you can easily run multiple API servers without needing to coordinate between them. Once you have multiple API servers running you can put a load balancer in front of them to make it transparent to clients.

## Running leader election with Kubernetes

Some master components, such as the scheduler and the controller manager, can't have multiple instances active at the same time. This will be chaos, as multiple schedulers try to schedule the same pod into multiple nodes or multiple times into the same node. The correct way to have a highly scalable Kubernetes cluster is to have these components run in leader election mode. This means that multiple instances are running, but only one is active at a time and if it fails, another one is elected as leader and takes its place.

Kubernetes supports this mode via the --leader-elect flag. The scheduler and the controller manager can be deployed as pods by copying their respective manifests to /etc/kubernetes/manifests.

Here is a snippet from a scheduler manifest that shows the use of the flag:

```
    command:
    - /bin/sh
    - -c
    - /usr/local/bin/kube-scheduler --master=127.0.0.1:8080 --v=2 --leader-elect=true 1>>/var/log/kube-scheduler.log
      2>&1
```
Here is a snippet from a controller manager manifest that shows the use of the flag:

```
  - command:
    - /bin/sh
    - -c
    - /usr/local/bin/kube-controller-manager --master=127.0.0.1:8080 --cluster-name=e2e-test-bburns
      --cluster-cidr=10.245.0.0/16 --allocate-node-cidrs=true --cloud-provider=gce  --service-account-private-key-file=/srv/kubernetes/server.key
      --v=2 --leader-elect=true 1>>/var/log/kube-controller-manager.log 2>&1
    image: gcr.io/google\_containers/kube-controller-manager:fda24638d51a48baa13c35337fcd4793
```

There several other flags to control leader election. All of them have reasonable defaults:

```
--leader-elect-lease-duration duration     Default: 15s
--leader-elect-renew-deadline duration     Default: 10s
--leader-elect-resource-lock endpoints     Default: "endpoints" ("configmaps" is the other option)
--leader-elect-retry-period duration       Default: 2s
```

Note that it is not possible to have these components restarted automatically by Kubernetes like other pods because these are exactly the Kubernetes components responsible for restarting failed pods, so they can't restart themselves if they fail. There must be a ready-to-go replacement already running.


## Making your staging environment highly available

High availability is not trivial to set up. If you go to the trouble of setting up high availability, it means there is a business case for a highly available system. It follows that you want to test your reliable and highly available cluster before you deploy it to production (unless you're Netflix, where you test in production). Also, any change to the cluster may, in theory, break your high availability without disrupting other cluster functions. The essential point is that, just like anything else, if you don't test it, assume it doesn't work.

We've established that you need to test reliability and high availability. The best way to do it is to create a staging environment that replicates your production environment as closely as possible. This can get expensive. There are several ways to manage the cost:

- Ad hoc HA staging environment: Create a large HA cluster only for the duration of HA testing
- Compress time: Create interesting event streams and scenarios ahead of time, feed the input, and simulate the situations in rapid succession
- Combine HA testing with performance and stress testing: At the end of your performance and stress tests, overload the system and see how the reliability and high availability configuration handles the load

## Testing high-availability

Testing high-availability takes planning and a deep understanding of your system. The goal of every test is to reveal flaws in the system's design and/or implementation, and to provide good enough coverage that, if the tests pass, you'll be confident that the system behaves as expected.

In the realm of reliability, self-healing and high-availability, it means you need to figure out ways to break the system and watch it put itself back together.

That requires several pieces, as follows:

- Comprehensive list of possible failures (including reasonable combinations)
- For each possible failure, it should be clear how the system should respond
- A way to induce the failure
- A way to observe how the system reacts

None of the pieces are trivial. The best approach in my experience is to do it incrementally and try to come up with a relatively small number of generic failure categories and generic responses, rather than an exhaustive, ever-changing list of low-level failures.

For example, a generic failure category is node-unresponsive; the generic response could be rebooting the node, the way to induce the failure can be stopping the VM of the node (if it's a VM), and the observation should be that, while the node is down, the system still functions properly based on standard acceptance tests, the node is eventually up, and the system gets back to normal. There may be many other things you want to test, such as whether the problem was logged, whether relevant alerts went out to the right people, and whether various stats and reports were updated.

But, beware of over-generalizing. In the case of the generic unresponsive node failure mode a key component is detecting that the nodes is unresponsive. If your method of detection is faulty then your system will not react properly. Use best practices like health checks and readiness checks.

Note that sometimes, a failure can't be resolved in a single response. For example, in our unresponsive node case, if it's a hardware failure then reboot will not help. In this case, a second line of response gets into play and maybe a new node is provisioned  to replace the failed node. In this case, you can't be too generic and you may need to create tests for specific types of pod/role that were on the node (etcd, master, worker, database, monitoring).

If you have high quality requirements, be prepared to spend much more time setting up the proper testing environments and the tests than even the production environment.

One last, important point is to try to be as non-intrusive as possible. That means that, ideally, your production system will not have testing features that allow shutting down parts of it or cause it to be configured to run in reduced capacity for testing. The reason is that it increases the attack surface of your system and it can be triggered by accident by mistakes in configuration. Ideally, you can control your testing environment without resorting to modifying the code or configuration that will be deployed in production. With Kubernetes, it is usually easy to inject pods and containers with custom test functionality that can interact with system components in the staging environment, but will never be deployed in production.

In this section, we looked at what it takes to actually have a reliable and highly available cluster, including etcd, the API server, the scheduler, and the controller manager. We considered best practices for protecting the cluster itself as well as your data, and paid special attention to the issue of starting environments and testing.

# High-availability, scalability and capacity planning

Highly available systems must also be scalable. The load on most complicated distributed systems can vary dramatically based on time of day, weekday vs weekend, seasonal effects, marketing campaigns and many other factors. Successful systems will have more users over time and accumulate more and more data. That means that physical resources of of the clusters - mostly nodes and storage - will have to grow over time too. If your cluster is under provisioned it will not be able to satisfy all the demand and it will not be available because requests will time out or be queued up and not processed fast enough.

This is the realm of capacity planning. One simple approach is to over-provision your cluster. Anticipate the demand and make sure you have enough of a buffer for spikes of activity. But, this approach suffers from several deficiencies:

- For highly dynamic and complicated distributed systems it's difficult to forecast the demand even approximately
- Over-provisioning is expansive. You spend a lot of money on resources that are rarely or never used.
- You have to periodically redo the whole process because the average and peak load on the system changes over time   

A much better approach is to use intent-based capacity planning where high-level abstraction is used and the system adjusts itself accordingly. In the context of Kubernetes, there is the horizontal pod autoscaler that can grow and shrink the number of pods needed to handle requests for a particular service. But, that works only to change the ratio of resources allocated to different services. When the entire cluster approaches saturation you simply need more resources. This is where the cluster autoscaler comes into play. It is a Kubernetes project that became available with Kubernetes 1.8. It works particularly well in cloud environments where additional resources can be provisioned via programmatic APIs.

 When the cluster autoscaler (CA) determines that pods can't be scheduled (are in pending state) it provisions a new node for the cluster. It can also removes nodes from the cluster if it determines that the cluster has more nodes than necessary to handle the load. The CA will check for pending pods every 30 seconds. It will remove nodes only after 10 minutes of not being used to avoid thrashing.
 
 Here are some issues to consider:
 - A cluster may require more nodes even if the total CPU or memory utilization is low due to control mechanisms like affinity, anti-affinity, taints, tolerations, pod priorities, and pod disruption budgets
 - In addition to the built-in delays in triggering scale up or scale down of nodes there is additional delay of several minutes when provisioning a new node from the cloud provider
 - The interactions between HPA and the CA can be subtle
 
 ## Installing the cluster autoscaler
 
 Note that you can't test the CA locally. You must use have a Kubernetes cluster running on one of the supported cloud providers:
 - GCE
 - GKE
 - AWS/EKS
 - Azure
 - Alibaba cloud
 - Baidu cloud
 
 I have installed it successfully on GKE as well as AWS EKS.
 
 The eks-cluster-autoscaler.yaml file contains all the Kubernetes resources needed to install the cluster autoscaler on EKS. It involves creating a service account, giving it various RBAC permissions because it needs to monitor node usage across the cluster and be able to act on it. Finally, there is a Deployment that actually deploys the cluster autoscaler image itself with a command-line that includes the range of nodes (minimum and maximum number) it should maintain and in the case of EKS, a node group is needed too. The maximum number is important to prevent a situation where an attack or error causes the cluster autoscaler to just add more and more nodes uncontrollably and racking up a huge bill. Here is a snippet from the pod template:
 
```
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - image: k8s.gcr.io/cluster-autoscaler:v1.2.2
        name: cluster-autoscaler
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 300Mi
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --nodes=2:5:eksctl-project-nodegroup-ng-name-NodeGroup-suffix
        env:
        - name: AWS_REGION
          value: us-east-1
        volumeMounts:
        - name: ssl-certs
          mountPath: /etc/ssl/certs/ca-certificates.crt
          readOnly: true
        imagePullPolicy: "Always"
      volumes:
      - name: ssl-certs
        hostPath:
          path: "/etc/ssl/certs/ca-bundle.crt"
``` 
 
The combination of the HPA and CA provides a truly elastic cluster where the HPA ensures that services use the proper amount of pods to handle the load per service and the CA makes sure that the number of nodes matches the overall load on the cluster. 
 
## Considering the vertical pod autoscaler
 
The vertical pod autoscaler is another autoscaler that operates on pods. Its job is to provide additional resources (cpu and memory) to pods that has too low limits. It is designed primarily for stateful services, but can work for stateless services too. It is based a CRD and has three components:

- Recommender - Watches cpu and memory usage and provides recommendation for new values for cpu and memory requests
- Updater - Kills managed pods whose cpu and memory requests don't match the recommendations made by the recommender
- Admission plugin - Sets the cpu and memory requests for new or recreated pods based on recommendations

The VPA is still in beta. Here are some of the main limitations:
- Unable to update running pod (hence the updater kills pods to get them restarted with the correct requests)
- Can't evict pods that aren't managed by a controller
- VPA is incompatible with the horizontal pod autoscaler (HPA)

This section covered the interactions between auto-salability and high-availability and looked at different approaches for scaling Kubernetes clusters and the applications running on these clusters.

# Live cluster updates

One of the most complicated and risky tasks involved in running a Kubernetes cluster is a live upgrade. The interactions between different parts of the system of different versions are often difficult to predict, but in many situations, it is required. Large clusters with many users can't afford to be offline for maintenance. The best way to attack complexity is to divide and conquer. Microservice architecture helps a lot here. You never upgrade your entire system. You just constantly upgrade several sets of related microservices, and if APIs have changed then you upgrade their clients, too. A properly designed upgrade will preserve backward-compatibility at least until all clients have been upgraded, and then deprecate old APIs across several releases.

In this section, we will discuss how to go about updating your cluster using various strategies, such as rolling updates, blue-green deployments and canary deployments. We will also discuss when it's appropriate to introduce breaking upgrades versus backward-compatible upgrades. Then we will get into the critical topic of schema and data migrations.

## Rolling updates

Rolling updates are updates where you gradually update components from the current version to the next. This means that your cluster will run current and new components at the same time. There are two cases to consider here:

- New components are backward-compatible
- New components are not backward-compatible

If the new components are backward-compatible, then the upgrade should be very easy. In earlier versions of Kubernetes, you had to manage rolling updates very carefully with labels and change the number of replicas gradually for both the old and new version (although kubectl rolling-update is a convenient shortcut for replication controllers). But, the Deployment resource introduced in Kubernetes 1.2 makes it much easier and supports replica sets. It has the following capabilities built-in:

- Running server-side (it keeps going if your machine disconnects)
- Versioning
- Multiple concurrent rollouts
- Updating deployments
- Aggregating status across all pods
- Rollbacks
- Canary deployments
- Multiple upgrade strategies (rolling upgrade is the default)

Here is a sample manifest for a deployment that deploys three nginx pods:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.7.9
        ports:
        - containerPort: 80
```

The resource kind is Deployment and it's got the name nginx-deployment, which you can use to refer to this deployment later (for example, for updates or rollbacks). The most important part is, of course, the spec, which contains a pod template. The replicas determine how many pods will be in the cluster, and the template spec has the configuration for each container. In this case, just a single container.

To start the rolling update, create the deployment resource and check that it rolled out successfully

```
$ k create -f nginx-deployment.yaml
deployment.apps/nginx-deployment created

$ k rollout status deployment/nginx-deployment
deployment "nginx-deployment" successfully rolled out
```

Deployments have an update strategy, which defaults to rollingUpdate:

```
$ k get deployment nginx-deployment -o yaml | grep strategy -A 4
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
```

The following diagram illustrates how rolling update works:

????? images/ch3 - rolling update.png

### Complex deployments

The Deployment resource is great when you just want to upgrade one pod, but you may often need to upgrade multiple pods, and those pods sometimes have version inter-dependencies. In those situations, you sometimes must forgo a rolling update or introduce a temporary compatibility layer. For example, suppose service A depends on service B. Service B now has a breaking change. The v1 pods of service A can't interoperate with the pods from service B v2. It is also undesirable from a reliability and change-management point of view to make the v2 pods of service B support the old and new APIs. In this case, the solution may be to introduce an adapter service that implements the v1 API of the B service. This service will sit between A and B, and will translate requests and responses across versions. This adds complexity to the deployment process and require several steps, but the benefit is that the A and B services themselves are simple. You can do rolling updates across incompatible versions and all indirection can go away once everybody upgrades to v2 (all A pods and all B pods).

But, rolling updates are not always the answer.

## Blue-green deployments

Rolling updates are great for availability, but sometimes the complexity involved in managing a proper rolling update is considered too high, or it adds a significant amount of work that pushes back more important projects. In these cases, blue-green upgrades provide a great alternative. With a blue-green release, you prepare a full copy of your production environment with the new version. Now you have two copies, old (blue) and new (green). It doesn't matter which one is blue and which one is green. The important thing is that you have two fully independent production environments. Currently, blue is active and services all requests. You can run all your tests on green. Once you're happy, you flip the switch and green becomes active. If something goes wrong, rolling back is just as easy; just switch back from green to blue. 

The following diagram illustrates how blue-green deployments works using two deployments, two labels and a single service that uses label selector to switch from the blue deployment to the green deployment:

????? images/ch3 - blue green deployment.png

I totally ignored the storage and in-memory state in the previous discussion. This immediate switch assumes that blue and green are composed of stateless components only and share a common persistence layer.

If there were storage changes or breaking changes to the API accessible to external clients, then additional steps need to be taken. For example, if blue and green have their own storage, then all incoming requests may need to be sent to both blue and green, and green may need to ingest historical data from blue to get in sync before switching.

## Canary deployments

Blue-green deployments are cool. However, there are times where a more nuanced approach is needed. Suppose you are responsible
for a large distributed system with many of users. The developer  plan to deploy a new version of
their service. They tested the nee version of the service in the test and staging environment. But, the production environment is too complicated to replicated one to one for testing purposes. This means there is a risk that the service will misbehave in production. That's where canary deployments shine.  

The basic idea is to test the service in production, but in a limited capacity. This way if the something is wrong with the new version only a small fraction of your users or a small fraction of requests will be impacted. This is can be implemented very easily in Kubernetes at the pod level. If a service is backed up by 10 pods then you deploy the new version and then only 10% of the requests wil be routed by the service load balancer to the canary pod, while 90% of the requests are still services by the current version.

The following diagram illustrates this approach:

????? images/ch3 - canary deployment.png

There are most sophisticated ways to route traffic to a canary deployment using a service mesh. We will examine it in a later chapter.

Let's address the hard problem of managing data-contract changes. 

## Managing data-contract changes

Data contracts describe how the data is organized. It's an umbrella term for structure metadata. The most common example is a relational database schema. Other examples include network payloads, file formats, and even the content of string arguments or responses. If you have a configuration file, then this configuration file has both a file format (JSON, YAML, TOML, XML, INI, custom format) and some internal structure that describes what kind of hierarchy, keys, values, and data types are valid. Sometimes the data contract is explicit and sometimes it's implicit. Either way, you need to manage it carefully, or else you'll get runtime errors when code that's reading, parsing, or validating encounters data with an unfamiliar structure.

## Migrating data

Data migration is a big deal. Many systems these days manage staggering amounts of data measured a terabytes, petabytes, or more. The amount of collected and managed data will continue to increase for the foreseeable future. The pace of data collection exceeds the pace of hardware innovation. The essential point is that if you have a lot of data and you need to migrate it, it can take a while. In a previous company, I oversaw a project to migrate close to 100 terabytes of data from one Cassandra cluster of a legacy system to another Cassandra cluster.

The second Cassandra cluster had different schema and was accessed by a Kubernetes cluster 24/7. The project was very complicated, and thus it kept getting pushed back when urgent issues popped up. The legacy system was still in place side-by-side with the next-gen system long after the original estimate.

There were a lot of mechanisms in place to split the data and send it to both clusters, but then we ran into scalability issues with the new system and we had to address those before we could continue. The historical data was important, but it didn't have to be accessed with the same service level as recent hot data. So, we embarked on yet another project to send historical data to cheaper storage. That meant, of course, that client libraries or frontend services had to know how to query both stores and merge the results. When you deal with a lot of data you can't take anything for granted. You run into scalability issues with your tools, your infrastructure, your third-party dependencies, and your processes. Large scale is not just quantity change; it is often qualitative change as well. Don't expect it to go smoothly. It is much more than copying some files from A to B.

## Deprecating APIs

API deprecation comes in two flavors: internal and external. Internal APIs are APIs used by components that are fully controlled by you and your team or organization. You can be sure that all API users will upgrade to the new API within a short time. External APIs are used by users or services outside your direct sphere of influence. There are a few gray-area situations where you work for a huge organization (think Google), and even internal APIs may need to be treated as external APIs. If you're lucky, all your external APIs are used by self-updating applications or through a web interface you control. In those cases, the API is practically hidden and you don't even need to publish it.

If you have a lot of users (or a few very important users) using your API, you should consider deprecation very carefully. Deprecating an API means you force your users to change their application to work with you or stay locked to an earlier version.

There are a few ways you can mitigate the pain:

- Don't deprecate. Extend the existing API or keep the previous API active. It is sometimes pretty simple, although it adds testing burden.
- Provide client libraries in all relevant programming languages to your target audience. This is always a good practice. It allows you to make many changes to the underlying API without disrupting users (as long as you keep the programming language interface stable).
- If you have to deprecate, explain why, allow ample time for users to upgrade, and provide as much support as possible (for example, an upgrade guide with examples). Your users will appreciate it.

# Large cluster performance, cost, and design trade-offs

In the previous section, we looked at live cluster upgrades and application updates. We explored various techniques and how Kubernetes supports them. We also discussed difficult problems such as breaking changes, data contract changes, data migration, and API deprecation. In this section, we will consider the various options and configurations of large clusters with different reliability and high-availability properties. When you design your cluster, you need to understand your options and choose wisely based on the needs of your organization.

The topics we will cover include various availability requirements, from best effort all the way to the holy grail of zero downtime. Finally, we will settle down on the practical site reliability engineering approach. For each category of availability, we will consider what it means from the perspectives of performance and cost.

## Availability requirements

Different systems have very different requirements for reliability and availability. Moreover, different sub-systems have very different requirements. For example, billing systems are always a high priority because if the billing system is down, you can't make money. But, even within the billing system, if the ability to dispute charges is sometimes unavailable, it may be OK from the business point of view.

## Best effort

Best effort means, counter-intuitively, no guarantee whatsoever. If it works, great! If it doesn't work – oh well, what are you going to do?. This level of reliability and availability may be appropriate for internal components that change often and the effort to make them robust is not worth it. As long the services or clients  that invoke the unreliable services are able to handle the occasional errors or outages then all is well. It may also be appropriate for services released in the wild as beta.

Best effort is great for developers. Developers can move fast and break things. They are not worried about the consequences and they don't have to go through a gauntlet of rigorous tests and approvals. The performance of best effort services may be better than more robust services because the best effort service can often skip expensive steps such as verifying requests, persisting intermediate results, and replicating data. But, on the other hand, more robust services are often heavily optimized and their supporting hardware is fine-tuned to their workload. The cost of best effort services is usually lower because they don't need to employ redundancy, unless the operators neglect to do basic capacity planning and just over-provision needlessly.

In the context of Kubernetes, the big question is whether all the services provided by the cluster are best effort. If this is the case, then the cluster itself doesn't have to be highly available. You can probably have a single master node with a single instance of etcd, and Heapster or another monitoring solution may not need to be deployed. This is typically appropriate for local development clusters only. Even a shared development cluster that multiple developers use should have a decent level of reliability and robustness or else all the developers will be twiddling their thumbs whenever the cluster goes down unexpectedly.

## Maintenance windows

In a system with maintenance windows, special times are dedicated for performing various maintenance activities, such as applying security patches, upgrading software, pruning log files, and database cleanups. With a maintenance window, the system (or a sub-system) becomes unavailable. This is planned off-time and often, users are notified. The benefit of maintenance windows is that you don't have to worry how your maintenance actions are going to interact with live requests coming into the system. It can drastically simplify operations. System administrators and operators love maintenance windows just as much as developers love best effort systems.

The downside, of course, is that the system is down during maintenance. It may only be acceptable for systems where user activity is limited to certain times (e.g. US office hours or week days only).

With Kubernetes, you can do maintenance windows by redirecting all incoming requests via the load balancer to a web page (or JSON response) that notifies users about the maintenance window.

But in most cases, the flexibility of Kubernetes should allow you to do live maintenance. In extreme cases, such as upgrading the Kubernetes version, or the switch from etcd v2 to etcd v3, you may want to resort to a maintenance window. Blue-green deployment is another alternative. But the larger the cluster, the more expansive the blue-green alternative because you must duplicate your entire production cluster, which is both costly and can cause you to run into problems like insufficient quota.

## Quick recovery

Quick recovery is another important aspect of highly available clusters. Something will go wrong at some point. Your unavailability clock starts running. How quickly can you get back to normal?

Sometimes it's not up to you. For example, if your cloud provider has an outage (and you didn't implement a federated cluster, as we will discuss later) then you just have to sit and wait until they sort it out. But the most likely culprit is a problem with a recent deployment. There are, of course, time-related issues, and even calendar-related issues. Do you remember the leap-year bug that took down Microsoft Azure on February 29, 2012?

The poster boy of quick recovery is, of course, the blue-green deployment–if you keep the previous version running when the problem is discovered. But, that's usually good for problems that happen during deployment or shortly after. If a sneaky bug lays dormant and is discovered only hours after the deployment then you will have tor down your blue deployment already and you will not be able to revert to it. 

On the other hand, rolling updates mean that if the problem is discovered early then most of your pods still run the previous version.

Data-related problems can take a long time to reverse, even if your backups are up to date and your restore procedure actually works (definitely test this regularly).

Tools like Heptio Velero can help in some scenarios by creating snapshot backup of your cluster that you can just restore, in case something goes wrong and you're not sure how to fix it.

## Zero-downtime

Finally, we arrive at the zero-downtime system. There is no such thing as a zero-downtime system. All systems fail and all software systems definitely fail. Sometimes the failure is serious enough that the system or some of its services will be down. Think about zero-downtime as a best effort distributed system design. You design for zero-downtime in the sense that you provide a lot of redundancy and mechanisms to address expected failures without bringing the system down. As always, remember that, even if there is a business case for zero-downtime, it doesn't mean that every component must be zero-downtime. Reliable (within reason) systems can be constructed from highly unreliable components. 

The plan for zero-downtime is as follows:

- Redundancy at every level: This is a required condition. You can't have a single point of failure in your design because when it fails, your system is down.
- Automated hot swapping of failed components: Redundancy is only as good as the ability of the redundant components to kick into action as soon as the original component has failed. Some components can share the load (for example, stateless web servers), so there is no need for explicit action. In other cases, such as the Kubernetes scheduler and controller manager, you need leader election in place to make sure the cluster keeps humming along.
- Tons of metrics, monitoring and alerts to detect problems early: Even with careful design, you may miss something or some implicit assumption might invalidate your design. Often such subtle issues creep up on you and with enough attention, you may discover it before it becomes an all-out system failure. For example, suppose there is a mechanism in place to clean up old log files when disk space is over 90% full, but for some reason, it doesn't work. If you set an alert for when disk space is over 95% full, then you'll catch it and be able to prevent the system failure.
- Tenacious testing before deployment to production: Comprehensive tests have proven themselves as a reliable way to improve quality. It is hard work to have comprehensive tests for something as complicated as a large Kubernetes cluster running a massive distributed system, but you need it. What should you test? Everything. That's right. For zero-downtime, you need to test both the application and the infrastructure together. Your 100% passing unit tests are a good start, but they don't provide much confidence that when you deploy your application on your production Kubernetes cluster it will still run as expected. The best tests are, of course, on your production cluster after a blue-green deployment or identical cluster. In lieu of a full-fledged identical cluster, consider a staging environment with as much fidelity as possible to your production environment. Here is a list of tests you should run. Each of these tests should be comprehensive because if you leave something untested it might be broken:
- Unit tests
- Acceptance tests
- Performance tests
- Stress tests
- Rollback tests
- Data restore tests
- Penetration tests

Does that sound crazy? Good. Zero-downtime large-scale systems are hard. There is a reason why Microsoft, Google, Amazon, Facebook, and other big companies have tens of thousands of software engineers (combined) just working on infrastructure, operations, and making sure things are up and running.

- Keep the raw data: For many systems, the data is the most critical asset. If you keep the raw data, you can recover from any data corruption and processed data loss that happens later. This will not really help you with zero-downtime because it can take a while to re-process the raw data, but it will help with zero-data loss, which is often more important. The downside to this approach is that the raw data is often huge compared to the processed data. A good option may be to store the raw data in cheaper storage compared to the processed data.
- Perceived uptime as a last resort: OK. Some part of the system is down. You may still be able to maintain some level of service. In many situations, you may have access to a slightly stale version of the data or can let the user access some other part of the system. It is not a great user experience, but technically the system is still available.

## Site reliability engineering

SRE is a real-world approach for operating reliable distributed systems. SRE embraces failures and works with SLIs (service level indicators), SLOs (service level objectives) and SLAs (service level agreements). Each service has an objectives such as latency below 50 milliseconds for 95% of requests. If a service violates its objectives then the team focuses on fixing the issue before going back to work on new features and capabilities.

The beauty of SRE is that you get to play with the knobs for cost and performance. If you want to invest more in reliability then be ready to pay for it in resources and development time.

## Performance and data consistency

When you develop or operate distributed systems, the CAP theorem should always be in the back of your mind. CAP stands for consistency, availability and partition tolerance. 

Consistency means that every read receives the most recent write or an error
Availability means that every request receives a non-error response (but the response may be stale)
Partition tolerance means the system continues to operate even when an arbitrary number of messages between nodes ar dropped or delayed by the network.

The theorem says that you can have at most two out of the three. Since any distributed system can suffer from a network partition in practice you can choose between CP or AP. CP, means that in order to remain consistent the system will not be available in the event of a network partition. AP means that the system will always be available but might not be consistent. For example, reads from different partitions might return different results because one of the partitions didn't receive a write. In this section, we will focus on highly available systems, which means AP. To achieve high availability, we must sacrifice consistency. But that doesn't mean that our system will have corrupt or arbitrary data. The keyword is eventual consistency. Our system may be a little bit behind and provide access to somewhat stale data, but eventually you'll get what you expect. 

When you start thinking in terms of eventual consistency, it opens the door to potentially significant performance improvements. For example, if some important value is updated frequently (for example, every second), but you send its value only every minute, you have reduced your network traffic by a factor of 60 and you're on average only 30 seconds behind real-time updates. This is very significant. This is huge. You have just scaled your system to handle 60 times more users or requests with the same amount of resources.

# Summary

In this chapter, we looked at reliable and highly available large-scale Kubernetes clusters. This is arguably the sweet spot for Kubernetes. While it is useful to be able to orchestrate a small cluster running a few containers, it is not necessary, but at scale, you must have an orchestration solution in place you can trust to scale with your system, and provide the tools and the best practices to do that.

You now have a solid understanding of the concepts of reliability and high availability in distributed systems. You delved into the best practices for running reliable and highly available Kubernetes clusters. You explored the nuances of live Kubernetes cluster upgrades and you can make wise design choices regarding levels of reliability and availability, as well as their performance and cost.

In the next chapter, we will address the important topic of security in Kubernetes. We will also discuss the challenges of securing Kubernetes and the risks involved. We will learn all about namespaces, service accounts, admission control, authentication, authorization, and encryption.

# Reference

https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/ha-topology/
https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/
https://medium.com/magalix/kubernetes-autoscaling-101-cluster-autoscaler-horizontal-pod-autoscaler-and-vertical-pod-2a441d9ad231

