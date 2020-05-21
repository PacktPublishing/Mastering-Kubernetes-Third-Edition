In this chapter, we will design a fictional massive-scale platform that will challenge Kubernetes' capabilities and scalability. The Hue platform is all about creating an omniscient and omnipotent digital assistant. Hue is a digital extension of you. Hue will help you do anything, find anything, and, in many cases will do a lot on your behalf. It will obviously need to store a lot information, integrate with many external services, respond to notifications and events, and be smart about interacting with you.

We will take the opportunity in this chapter to get to know kubectl and related tools a little better and explore in detail familiar resources we've seen before, such as pods, as well as new resources such as Jobs. We will explore advanced scheduling and resource management. At the end of this chapter, you will have a clear picture of how impressive Kubernetes is and how it can be used as the foundation for hugely complex systems.

# Designing the Hue platform

In this section, we will set the stage and define the scope of the amazing Hue platform. Hue is not Big Brother, Hue is Little Brother! Hue will do whatever you allow it to do. Hue will be able to do a lot, but some people might be concerned, so you get to pick how much or how little Hue can help you with. Get ready for a wild ride!

## Defining the scope of Hue

Hue will be manage your digital persona. It will know you better than you know yourself. Here is a list of some of the services Hue can manage and help you with:

- Search and content aggregation
- Medical - Electronic heath record, DNA sequencing
- Smart home
- Finance – bank, savings, retirement, investing
- Office
- Social
- Travel
- Wellbeing
- Family
 
### Smart reminders and notifications

Let's think of the possibilities. Hue will know you, but also know your friends, the aggregate of other users across all domains. Hue will update its models in real-time. It will not be confused by stale data. It will act on your behalf, present relevant information, and learn your preferences continuously. It can recommend new shows or books that you may like, make restaurant reservations based on your schedule and your family or friends, and control your house automation.

### Security, identity, and privacy

Hue is your proxy online. The ramifications of someone stealing your Hue identity, or even just eavesdropping on your Hue interactions, are devastating. Potential users may even be reluctant to trust the Hue organization with their identity. Let's devise a non-trust system where users have the power to pull the plug on Hue at any time. Here are a few ideas in the right direction.

- Strong identity via a dedicated device with multi-factor authorization, including multiple biometric reasons:
- Frequently rotating credentials
- Quick service pause and identity verification of all external services (will require original proof of identity to each provider)
- The Hue backend will interact with all external services via short-lived tokens
- Architecting Hue as a collection of loosely-coupled microservices with strong compartmentalization
- GDPR compliance
- End to end encryption
- Avoid owning critical data (let external providers manage it)

Hue's architecture will need to support enormous variation and flexibility. It will also need to be very extensible where existing capabilities and external services are constantly upgraded, and new capabilities and external services are integrated into the platform. That level of scale calls for microservices, where each capability or service is totally independent of other services except for well-defined interfaces via standard and/or discoverable APIs.

### Hue components

Before embarking on our microservice journey, let's review the types of component we need to construct for Hue.

**User profile**

The user profile is a major component, with lots of sub-components. It is the essence of the user, their preferences, history across every area, and everything that Hue knows about them. The benefit you can get from Hue is impacted strongly by the richness of the profile. But, the more information is managed by the profile the more damage you can suffer if the data (or part of it) is compromised.

A big piece of managing the user profile is the reports and insights that Hue will provide to the user. Hue will employ sophisticated machine learning to better understand the user and their interactions with other users and external service providers. 

**User graph**

The user graph component models networks of interactions between users across multiple domains. Each user participates in multiple networks: social networks such as Facebook, Instagram and Twitter, professional networks, hobby networks, and volunteer communities. Some of these networks are ad-hoc and Hue will be able to structure them to benefit users. Hue can take advantage of the rich profiles it has of user connections to improve interactions even without exposing private information.

**Identity**

Identity management is critical, as mentioned previously, so it merits a separate component. A user may prefer to manage multiple mutually exclusive profiles with separate identities. For example, maybe users are not comfortable with mixing their health profile with their social profile at the risk of inadvertently exposing personal health information to their friends. While Hue can find useful connections for you, you may prefer to tradeoff capabilities with more privacy. 

**Authorizer**

The authorizer is a critical component where the user explicitly authorizes Hue to perform certain actions or collect various data on its behalf. This includes access to physical devices, accounts of external services, and level of initiative.

**External service**

Hue is an aggregator of external services. It is not designed to replace your bank, your health provider, or your social network. It will keep a lot of metadata about your activities, but the content will remain with your external services. Each external service will require a dedicated component to interact with the external service API and policies. When no API is available, Hue emulates the user by automating the browser or native apps.

**Generic sensor**

A big part of Hue's value proposition is to act on the user's behalf. In order to do that effectively, Hue needs to be aware of various events. For example, if Hue reserved a vacation for you but it senses that a cheaper flight is available, it can either automatically change your flight or ask you for confirmation. There is an infinite number of things to sense. To reign in sensing, a generic sensor is needed. The generic sensor will be extensible, but exposes a generic interface that the other parts of Hue can utilize uniformly even as more and more sensors are added.

**Generic actuator**

This is the counterpart of the generic sensor. Hue needs to perform actions on your behalf. For example, reserving a flight or a doctor appointment. To do that, Hue needs a generic actuator that can be extended to support particular functions but can interact with other components, such as the identity manager and the authorizer, in a uniform fashion.

**User learner**

This is the brain of Hue. It will constantly monitor all your interactions (that you authorize) and update its model of you and other users in your networks. This will allow Hue to become more and more useful over time, predict what you need and what will interest you, provide better choices, surface more relevant information at the right time, and avoid being annoying and overbearing.

### Hue microservices

The complexity of each of the components is enormous. Some of the components, such as the external service, the generic sensor, and generic actuator, will need to operate across hundreds, thousands, or more external services that constantly change outside the control of Hue. Even the user learner needs to learn the user's preferences across many areas and domains. Microservices address this need by allowing Hue to evolve gradually and grow more isolated capabilities without collapsing under its own complexity. Each microservice interacts with generic Hue infrastructure services through standard interfaces and, optionally, with a few other services through well-defined and versioned interfaces. The surface area of each microservice is manageable and the orchestration between microservices is based on standard best practices.

**Plugins**

Plugins are the key to extending Hue without a proliferation of interfaces. The thing about plugins is that often, you need plugin chains that cross multiple abstraction layers. For example, if we want to add a new integration for Hue with YouTube, then you can collect a lot of YouTube-specific information – your channels, favorite videos, recommendation, and videos you watched. To display this information to users and allow them to act on it, you need plugins across multiple components and eventually in the user interface as well. Smart design will help by aggregating categories of actions such as recommendations, selections, and delayed notifications to many different services.

The great thing about plugins is that they can be developed by anyone. Initially, the Hue development team will have to develop the plugins, but as Hue becomes more popular, external services will want to integrate with Hue and build Hue plugins to enable their service.

That will lead, of course, to a whole eco system of plugin registration, approval, and curation.

**Data stores**

Hue will need several types of data stores, and multiple instances of each type, to manage its data and metadata:

- Relational database
- Graph database
- Time-series database
- In-memory caching
- Blob storage

Due to the scope of Hue, each one of these databases will have to be clustered, scalable and distributed.

In addition, Hue will use local storage on edge devices. 

**Stateless microservices**

The microservices should be mostly stateless. This will allow specific instances to be started and killed quickly, and migrated across the infrastructure as necessary. The state will be managed by the stores and accessed by the microservices with short-lived access tokens. Hue will store frequently accessed data in easily hydrated fast caches when appropriate.

**Serverless functions**

A big part of Hue's functionality per user will involve relatively short interactions with external services or other Hue services. For those activities it may not be necessary to run a full-fledged persistent microservice that needs to be scaled and managed. A more appropriate solution may be to use a serverless function that is more lightweight. 

**Queue-based interactions**

All these microservices need to talk to each other. Users will ask Hue to perform tasks on their behalf. External services will notify Hue of various events. Queues coupled with stateless microservices provide the perfect solution. Multiple instances of each microservice will listen to various queues and respond when relevant events or requests are popped from the queue. Serverless functions may be triggered as a result of particular events too. This arrangement is very robust and easy to scale. Every component can be redundant and highly available. While each component is fallible, the system is very fault-tolerant.

A queue can be used for asynchronous RPC or request-response style interactions too, where the calling instance provides a private queue name and the collie posts the response to the private queue.

That said, sometimes direct service to service interaction (or serverless function to service interaction) though a well-defined interface makes more sense and simplifies the architecture.

## Planning workflows

Hue often needs to support workflows. A typical workflow will get a high-level task, such as make a dentist appointment; it will extract the user's dentist details and schedule, match it with the user's schedule, choose between multiple options, potentially confirm with the user, make the appointment, and set up a reminder. We can classify workflows into fully automatic and human workflows where humans are involved. Then there are workflows that involve spending money and might require additional level of approval.

### Automatic workflows

Automatic workflows don't require human intervention. Hue has full authority to execute all the steps from start to finish. The more autonomy the user allocates to Hue the more effective it will be. The user will be able to view and audit all workflows, past and present.

### Human workflows

Human workflows require interaction with a human. Most often it will be the user that needs to make a choice from multiple options or approve an action. But it may involve a person on another service. For example, to make an appointment with a dentist, Hue may have to get a list of available times from the secretary. In the future, Hue will be able to handle conversation with humans and possibly automate some of these workflows too.

### Budget-aware workflows

Some workflows, such as paying bills or purchasing a gift, require spending money. While, in theory, Hue can be granted unlimited access to the user's bank account, most users will probably be more comfortable with setting budgets for different workflows or just making spending a human-approved activity. Potentially, the user can grant Hue access to a dedicated account or set of accounts and based on reminders and reports allocate more or less funds to Hue as needed.

# Using Kubernetes to build the Hue platform

In this section, we will look at various Kubernetes resources and how they can help us build Hue. First, we'll get to know the versatile kubectl a little better, then we will look at how to run long-running processes in Kubernetes, exposing services internally and externally, using namespaces to limit access, launching ad-hoc jobs, and mixing in non-cluster components. Obviously, Hue is a huge project, so we will demonstrate the ideas on a local cluster and not actually build a real Hue Kubernetes cluster. Consider it primarily a thought experiment. If you wish to explore building a real microservice-based distributed system on Kubernetes check out [Hands-On Microservices with Kubernetes](https://www.packtpub.com/virtualization-and-cloud/hands-microservices-kubernetes). 

## Using Kubectl effectively

Kubectl is your Swiss Army Knife. It can do pretty much anything around the cluster. Under the hood, kubectl connects to your cluster via the API. It reads your `~/.kube/config` file, which contains information necessary to connect to your cluster or clusters. The commands are divided into multiple categories:

- **Generic commands** : Deal with resources in a generic way: create, get, delete, run, apply, patch, replace, and so on
- **Cluster management commands** : Deal with nodes and the cluster at large: cluster-info, certificate, drain, and so on
- **Troubleshooting commands** : Describe, logs, attach, exec, and so on
- **Deployment commands** : Deal with deployment and scaling: rollout, scale, auto-scale, and so on
- **Settings commands** : Deal with labels and annotations: label, annotate, and so on
- **Misc commands** : Help, config, and version
- **Custimization commands**: Integrate the kustomize.io capabilities into kubectl


You can view the configuration with kubernetes config view.

Here is the configuration for my local k3s cluster:

```
$ k config view
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://localhost:6443
  name: default
contexts:
- context:
    cluster: default
    user: default
  name: default
current-context: default
kind: Config
preferences: {}
users:
- name: default
  user:
    password: 6ce7b64ff48ac13f06af428d92b3d4bf
    username: admin
```

## Understanding Kubectl resource configuration files

Many kubectl operations such as create require complicated hierarchical structure (since the API requires this structure). Kubectl uses YAML or JSON configuration files. YAML is more concise and human-readable. Here is a YAML configuration file for creating a pod:

```
apiVersion: v1
kind: Pod
metadata:
  name: ""
  labels:
    name: ""
  namespace: ""
  annotations: []
  generateName: ""
spec:
     ...
```     

### ApiVersion

The very important Kubernetes API keeps evolving and can support different versions of the same resource via different versions of the API.

### Kind

Kind tells Kubernetes what type of resource it is dealing with. In this case, Pod. This is always required.

### Metadata

A lot of information that describes the pod and where it operates:

- **Name** : Identifies the pod uniquely within its namespace
- **Labels** : Multiple labels can be applied
- **Namespace** : The namespace the pod belongs to
- **Annotations** : A list of annotations available for query

### Spec

Spec is a pod template that contains all the information necessary to launch a pod. It can be quite elaborate, so we'll explore it in multiple parts:

```
spec:
  containers: [
      ...
  ],
  "restartPolicy": "",
  "volumes": []
```

#### Container spec

The pod spec's containers section is a list of container specs. Each container spec has the following structure:

```
name: "",
image: "",
command: [""],
args: [""],
env:
    - name: "",
      value: ""

imagePullPolicy: "",
ports: 
    - containerPort": 0,
      name: "",
      protocol: ""
resources:
    cpu: ""
    memory: ""
```

Each container has an image, a command that, if specified, replaces the Docker image command. It also has arguments and environment variables. Then, there are of course the image pull policy, ports, and resource limits. We covered those in earlier chapters.

## Deploying long-running microservices in pods

Long-running microservices should run in pods and be stateless. Let's look at how to create pods for one of Hue's microservices. Later, we will raise the level of abstraction and use a deployment.

### Creating pods

Let's start with a regular pod configuration file for creating a Hue learner internal service. This service doesn't need to be exposed as a public service and it will listen to a queue for notifications and store its insights in some persistent storage.

We need a simple container that will run in the pod. Here is possibly the simplest Docker file ever, which will simulate the Hue learner:

```
FROM busybox

CMD ash -c "echo 'Started...'; while true ; do sleep 10 ; done"
```

It uses the `busybox` base image, prints to standard output `Started...` and then goes into an infinite loop, which is, by all accounts, long-running :-)

I have built two Docker images tagged as "g1g1/hue-learn:0.3" and "g1g1/hue-learn:v0.4" and pushed them to the DockerHub registry ("g1g1" is my user name).

```
$ docker build . -t g1g1/hue-learn:0.3
$ docker build . -t g1g1/hue-learn:0.4
$ docker push g1g1/hue-learn:0.3
$ docker push g1g1/hue-learn:0.4
```

Now these images are available to be pulled into containers inside of Hue's pods.

We'll use YAML here because it's more concise and human-readable. Here are the boilerplate and metadata labels:

```
apiVersion: v1
kind: Pod
metadata:
  name: hue-learner
  labels:
    app: hue
    service: learner
    runtime-environment: production
    tier: internal-service
```    

The reason I use an annotation for the version and not a label is that labels are used to identify the set of pods in the deployment. Modifying labels is not allowed.

Next comes the important containers spec, which defines for each container the mandatory name and image:

```
spec:
  containers:
  - name: hue-learner
    image: g1g1/hue-learn:0.3
```
The resources section tells Kubernetes the resource requirements of the container, which allows for more efficient and compact scheduling and allocations. Here, the container requests 200 milli-cpu units (0.2 core) and 300 MiB (2 to the power 28 bytes):

```
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
```

The environment section allows the cluster administrator to provide environment variables that will be available to the container. Here it tells it to discover the queue and the store via dns. In a testing environment, it may use a different discovery method:

```
    env:
    - name: DISCOVER_QUEUE
      value: dns
    - name: DISCOVER_STORE
      value: dns
```


### Decorating pods with labels

Labeling pods wisely is key for flexible operations. It lets you evolve your cluster live, organize your microservices into groups you can operate on uniformly, and drill down on the fly to observe different subsets.

For example, our Hue learner pod has the following labels:

- **runtime-environment** : production
- **tier** : internal-service

 The runtime-environment label allows performing global operations on all pods that belong to a certain environment. The "tier" label can be used to query all pods that belong to a particular tier. These are just examples; your imagination is the limit here.
 
 Here is how to list the labels with the get pods command:
 
```
$ kubectl get po -n kube-system --show-labels

NAME                       READY   STATUS    RESTARTS   AGE   LABELS
coredns-b7464766c-s4z28    1/1     Running   3          15d   k8s-app=kube-dns,pod-template-hash=b7464766c
svclb-traefik-688zv        2/2     Running   6          15d   app=svclb-traefik,controller-revision-hash=66fd644d6,pod-template-generation=1,svccontroller.k3s.cattle.io/svcname=traefik
svclb-traefik-hfk8t        2/2     Running   6          15d   app=svclb-traefik,controller-revision-hash=66fd644d6,pod-template-generation=1,svccontroller.k3s.cattle.io/svcname=traefik
svclb-traefik-kp9wh        2/2     Running   6          15d   app=svclb-traefik,controller-revision-hash=66fd644d6,pod-template-generation=1,svccontroller.k3s.cattle.io/svcname=traefik
svclb-traefik-sgmbg        2/2     Running   6          15d   app=svclb-traefik,controller-revision-hash=66fd644d6,pod-template-generation=1,svccontroller.k3s.cattle.io/svcname=traefik
traefik-56688c4464-c4sfq   1/1     Running   3          15d   app=traefik,chart=traefik-1.64.0,heritage=Tiller,pod-template-hash=56688c4464,release=traefik
```
 
Now, if you want to filter and list only the pods of the traefik app type:

```
$ kubectl get po -n kube-system -l app=traefik
NAME                       READY   STATUS    RESTARTS   AGE
traefik-56688c4464-c4sfq   1/1     Running   3          15d
``` 

### Deploying long-running processes with deployments

In a large-scale system, pods should never be just created and let loose. If a pod dies unexpectedly for whatever reason, you want another one to replace it to maintain overall capacity. You can create replication controllers or replica sets yourself, but that leaves the door open to mistakes, as well as the possibility of partial failure. It makes much more sense to specify how many replicas you want when you launch your pods in a declarative manner. This is what Kubernetes deployments are for.

Let's deploy three instances of our Hue learner microservice with a Kubernetes deployment resource. Note that deployment objects became stable at Kubernetes 1.9.

```
apiVersion: apps/v1
kind: Deployment
metadata:
    name: hue-learn
    labels:
        app: hue
        service: learn
    spec:
        replicas: 3
        selector:
            matchLabels:
               app: hue
               service: learn
        template:
         metadata:
           labels:
             app: hue
        spec:
            <same spec as in the pod template>
```

The pod spec is identical to the spec section from the pod configuration file previously.

Let's create the deployment and check its status:

```
$ kubectl create -f hue-learn-deployment.yaml
deployment.apps/hue-learn created

$ kubectl get deployment hue-learn
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
hue-learn   3/3     3            3           32s

$ kubectl get pods -l app=hue
NAME                         READY   STATUS    RESTARTS   AGE
hue-learn-558f5c45cd-fbvpj   1/1     Running   0          81s
hue-learn-558f5c45cd-s6vkk   1/1     Running   0          81s
hue-learn-558f5c45cd-tdlpq   1/1     Running   0          81s
```

You can get a lot more information about the deployment using the kubectl describe command.


### Updating a deployment

The Hue platform is a large and ever-evolving system. You need to upgrade constantly. Deployments can be updated to roll out updates in a painless manner. You change the pod template to trigger a rolling update fully managed by Kubernetes.

Currently, all the pods are running with version 0.3:

```
$ kubectl get pods -o jsonpath='{.items[*].spec.containers[0].image}'
g1g1/hue-learn:0.3
g1g1/hue-learn:0.3
g1g1/hue-learn:0.3
```

Let's update the deployment to upgrade to version 0.4. Modify the image version in the deployment file. Don't modify labels; it will cause an error. Save it to hue-learn-deployment-0.4.yaml. Then we can use the apply command to upgrade the version and verify that the pods now run 0.4

```
$ kubectl apply -f hue-learn-deployment-0.4.yaml
deployment "hue-learn" updated

$ kubectl get pods -o jsonpath='{.items[*].spec.containers[0].image}'
g1g1/hue-learn:0.4
g1g1/hue-learn:0.4
g1g1/hue-learn:0.4
```

Note, that new pods are created and the original 0.3 pods are terminated in a rolling update manner.

```
$ kubectl get pods
NAME                         READY   STATUS        RESTARTS   AGE    IP           NODE                    
hue-learn-558f5c45cd-fbvpj   1/1     Terminating   0          8m7s   10.42.3.15   k3d-k3s-default-server  
hue-learn-558f5c45cd-s6vkk   0/1     Terminating   0          8m7s   10.42.0.7    k3d-k3s-default-worker-0
hue-learn-558f5c45cd-tdlpq   0/1     Terminating   0          8m7s   10.42.2.15   k3d-k3s-default-worker-2
hue-learn-5c9bb545d9-lggk7   1/1     Running       0          38s    10.42.2.16   k3d-k3s-default-worker-2
hue-learn-5c9bb545d9-pwflv   1/1     Running       0          31s    10.42.1.10   k3d-k3s-default-worker-1
hue-learn-5c9bb545d9-q25hl   1/1     Running       0          35s    10.42.0.8    k3d-k3s-default-worker-0
```

# Separating internal and external services

Internal services are services that are accessed directly only by other services or jobs in the cluster (or administrators that log in and run ad-hoc tools). In some cases, internal services are not accessed at all, and just perform their function and store their results in a persistent store that other services access in a decoupled way.

But some services need to be exposed to users or external programs. Let's look at a fake Hue service that manages a list of reminders for a user. It doesn't really do much - just returns a fixed list of reminders - but we'll use it to illustrate how to expose services. I already pushed a hue-reminders image to DockerHub:

```
docker push g1g1/hue-reminders:3.0
```

## Deploying an internal service

Here is the deployment, which is very similar to the Hue-learner deployment, except that I dropped the annotations, env, and resources sections, kept just one two labels to save space, and added a ports section to the container. That's crucial, because a service must expose a port through which other services can access it:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hue-reminders
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hue
      service: reminders
  template:
    metadata:
      name: hue-reminders
      labels:
        app: hue
        service: reminders
    spec:
      containers:
      - name: hue-reminders
        image: g1g1/hue-reminders:3.0
        ports:
        - containerPort: 8080
```

When we run the deployment, two hue-reminders pods are added to the cluster:

```
$ kubectl create -f hue-reminders-deployment.yaml
deployment.apps/hue-reminders created

$ kubectl get pods
NAME                            READY   STATUS    RESTARTS   AGE
hue-learn-5c9bb545d9-lggk7      1/1     Running   0          22m
hue-learn-5c9bb545d9-pwflv      1/1     Running   0          22m
hue-learn-5c9bb545d9-q25hl      1/1     Running   0          22m
hue-reminders-9b7d65d86-4kf5t   1/1     Running   0          7s
hue-reminders-9b7d65d86-tch4w   1/1     Running   0          7s
```

OK. The pods are running. In theory, other services can look up or be configured with their internal IP address and just access them directly because they are all in the same network address space. But this doesn't scale. Every time a reminders pod dies and is replaced by a new one, or when we just scale up the number of pods, all the services that access these pods must know about it. Kubernetes Services solve this issue by providing a single stable access point to all the pods. Here is the the service definition:

```
apiVersion: v1
kind: Service
metadata:
  name: hue-reminders
  labels:
    app: hue
    service: reminders
spec:
  ports:
  - port: 8080
    protocol: TCP
  selector:
    app: hue
    service: reminders
```

The service has a selector that determines the backing pods by their matching labels. It also exposes a port, which other services will use to access it (it doesn't have to be the same port as the container's port).

The protocol field can be one of TCP, UDP and since Kubernetes 1.12 also SCTP (if the feature gate is enabled). 

## Creating the Hue-reminders service

Let's create the service and explore it a little bit:

```
$ kubectl create -f hue-reminders-service.yaml
service/hue-reminders created


$ kubectl describe svc hue-reminders
Name:              hue-reminders
Namespace:         default
Labels:            app=hue
                   service=reminders
Annotations:       <none>
Selector:          app=hue,service=reminders
Type:              ClusterIP
IP:                10.43.166.58
Port:              <unset>  8080/TCP
TargetPort:        8080/TCP
Endpoints:         10.42.1.12:8080,10.42.2.17:8080
Session Affinity:  None
Events:            <none>
```

The service is up-and-running. Other pods can find it through environment variables or DNS. The environment variables for all services are set at pod creation time. That means that, if a pod is already running when you create your service, you'll have to kill it and let Kubernetes recreate it with the environment variables (you create your pods via a deployment, right?):

```
$ kubectl exec hue-learn-5c9bb545d9-w8hrr -- printenv | grep HUE_REMINDERS_SERVICE
HUE_REMINDERS_SERVICE_HOST=10.43.166.58
HUE_REMINDERS_SERVICE_PORT=8080
```

But using DNS is much simpler. Your service DNS name is

`<service name>.<namespace>.svc.cluster.local`

```
$ kubectl exec hue-learn-5c9bb545d9-w8hrr -- nslookup hue-reminders.default.svc.cluster.local
Server:    10.43.0.10
Address 1: 10.43.0.10 kube-dns.kube-system.svc.cluster.local

Name:      hue-reminders.default.svc.cluster.local
Address 1: 10.43.247.147 hue-reminders.default.svc.cluster.local
```

Now, all the services in the default namespace can access the hue-reminders service though its service endpoint and port 8080:

```
$ kubectl exec hue-learn-5c9bb545d9-w8hrr -- wget -q -O - hue-reminders.default.svc.cluster.local:8080
Dentist appointment at 3pm
Dinner at 7pm
```

Yes, at the moment hue-reminders always returns the same two reminders:
```
Dentist appointment at 3pm
Dinner at 7pm
```

## Exposing a service externally

The service is accessible inside the cluster. If you want to expose it to the world, Kubernetes provides three ways to do it:

- Configure NodePort for direct access
- Configure a cloud load balancer if you run it in a cloud environment
- Configure your own load balancer if you run on bare metal

Before you configure a service for external access, you should make sure it is secure. The Kubernetes documentation has a good example that covers all the gory details here:

https://github.com/kubernetes/examples/blob/master/staging/https-nginx/README.md.

We've already covered the principles in _Chapter 4_, _Securing Kubernetes_.

Here is the spec section of the hue-reminders service when exposed to the world through NodePort:

```
spec:
  type: NodePort
  ports:
  - port: 8080
    targetPort: 8080
    protocol: TCP
    name: http

  - port: 443
    protocol: TCP
    name: https
  selector:
    app: hue-reminders
```

The main downside of exposing services though NodePort is that the port numbers are shared across all services and you must must coordinate them globally across your entire cluster to avoid conflicts. 

But, there are other reasons that you may want to avoid exposing a Kubernetes service directly and you may prefer to use an Ingress resource in front of the service. 


### Ingress

Ingress is a Kubernetes configuration object that lets you expose a service to the outside world and take care of a lot of details. It can do the following:

- Provide an externally visible URL to your service
- Load-balance traffic
- Terminate SSL
- Provide name-based virtual hosting

To use Ingress, you must have an Ingress controller running in your cluster. Note that Ingress was introduced in Kubernetes 1.1, but it is still in Beta and has many limitations. If you're running your cluster on GKE, you're probably OK. Otherwise, proceed with caution. One of the current limitations of the Ingress controller is that it isn't built for scale. As such, it is not a good option for the Hue platform yet. We'll cover the Ingress controller in greater detail in _Chapter 10_, _Exploring Advanced Networking_.

Here is what an Ingress resource looks like:

```
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: test-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /testpath
        backend:
          serviceName: test
          servicePort: 80
```

Note the annotation, which hints that it is an Ingress object that works with the Nginx ingress controller. There are many other ingress controllers and they typically use annotations to encode information they need that is not captured by the Ingress object itself and its rules.

Other ingress controllers include:
- Traefic
- Gloo
- Contour
- AWS ALB Ingress controller
- HAPRoxy Ingress
- Voyager


# Advanced scheduling

One of the strongest suits of Kubernetes is its powerful yet flexible scheduler. The job of the scheduler in simple words is to choose nodes to run newly created pods. In theory the scheduler could even move existing pods around between nodes, but in practice it doesn't do that at the moment and leave this functionality for other components.
  
By default, the scheduler follows several guiding principles like:

- Split pods from the same replica set or stateful set across nodes
- Schedule pods to nodes that have enough resources to satisfy the pod requests
- Balance out the overall resource utilization of nodes 

This is a pretty good default behavior, but sometimes you may want better control over specific pod placement. Kubernetes 1.6 introduced several advanced scheduling options that give you fine grained control over which pods are scheduled or not scheduled on which nodes as well as which pods are to be scheduled together or separately. 

Let's review these mechanisms in the context of Hue.

## Node selector

The node selector is pretty simple. A pod can specify which nodes it wants to be scheduled on in its spec. For example, the trouble-shooter pod has a nodeSelector that specifies the kubernetes.io/hostname label of the worker-2 node:

```
apiVersion: v1
kind: Pod
metadata:
  name: trouble-shooter
  labels:
    role: trouble-shooter
spec:
  nodeSelector:
    kubernetes.io/hostname: k3d-k3s-default-worker-2
  containers:
  - name: trouble-shooter
    image: g1g1/py-kube:0.2
    command: ["bash"]
    args: ["-c", "echo started...; while true ; do sleep 1 ; done"]

``` 

When creating this pod it is indeed scheduled to the worker-2 node:

```
$ k apply -f trouble-shooter.yaml
pod/trouble-shooter created

$ k get po trouble-shooter -o jsonpath='{.spec.nodeName}'
k3d-k3s-default-worker-2
```

## Taints and tolerations

You can taint a node in order to prevent pods from being scheduled on this node. This can be useful for example, if you don't want pods to be scheduled on your master nodes. Tolerations allow pods to declare that they can "tolerate" a specific node taint and then these pods can be scheduled on the tainted node. A node can have multiple taints and a pod can have multiple tolerations. A taint is a triplet key, value, effect. The key and value are used to identify the taint. The effect is one of:
- NoSchedule (no pods will be scheduled to the node unless it tolerates the taint)
- PreferNoSchedule (soft version of NoSchedule. the scheduler will attempt not to schedule pods that don't tolerate the taint)
- NoExecute (no new pods will be scheduled, but also existing pods that don't tolerate the taint will be evicted) 


Currently, there is a hue-learn pod that runs on the master node (k3d-k3s-default-server):

```
$ kubectl get po -o wide 
NAME                            READY   STATUS    RESTARTS   AGE     IP           NODE                       
hue-learn-5c9bb545d9-dk4c4      1/1     Running   0          7h40m   10.42.3.17   k3d-k3s-default-server
hue-learn-5c9bb545d9-sqx28      1/1     Running   0          7h40m   10.42.2.18   k3d-k3s-default-worker-2
hue-learn-5c9bb545d9-w8hrr      1/1     Running   0          7h40m   10.42.0.11   k3d-k3s-default-worker-0
hue-reminders-6f9f54d8f-hwjwd   1/1     Running   0          3h51m   10.42.0.13   k3d-k3s-default-worker-0
hue-reminders-6f9f54d8f-p4z8z   1/1     Running   0          3h51m   10.42.1.14   k3d-k3s-default-worker-1
```

Let's taint our master node

```
$ k taint nodes k3d-k3s-default-server master=true:NoExecute
node/k3d-k3s-default-server tainted
```

We can now review the taint:

```
$ k get nodes k3d-k3s-default-server -o jsonpath='{.spec.taints[0]}'
map[effect:NoExecute key:master value:true]
```

Yeah, it worked! there are now no pods scheduled on the master node. The pod on the master was terminated and a new pod (hue-learn-5c9bb545d9-nn4xk) is now running on worker-1.  

```
$ kubectl get po -o wide
NAME                            READY   STATUS    RESTARTS   AGE     IP           NODE
hue-learn-5c9bb545d9-nn4xk      1/1     Running   0          3m46s   10.42.1.15   k3d-k3s-default-worker-1
hue-learn-5c9bb545d9-sqx28      1/1     Running   0          9h      10.42.2.18   k3d-k3s-default-worker-2
hue-learn-5c9bb545d9-w8hrr      1/1     Running   0          9h      10.42.0.11   k3d-k3s-default-worker-0
hue-reminders-6f9f54d8f-hwjwd   1/1     Running   0          6h      10.42.0.13   k3d-k3s-default-worker-0
hue-reminders-6f9f54d8f-p4z8z   1/1     Running   0          6h      10.42.1.14   k3d-k3s-default-worker-1
trouble-shooter                 1/1     Running   0          16m     10.42.2.20   k3d-k3s-default-worker-2
```

To allow pods to tolerate the taint add a toleration to their spec such as:

```
tolerations:
- key: "master"
  operator: "Equal"
  value: "true"
  effect: "NoSchedule"
``` 
 
## Node affinity and anti-affinity

Node affinity is a more sophisticated form of the nodeSelector. It has two main advantages:
- Rich selection criteria (nodeSelector is just AND of exact matches on the labels)
- Rules can be soft
- You can achieve anti-affinity using operators like NotIn and DoesNotExist

Note that if you specify both nodeSelector and nodeAffinity then the pod will be scheduled only to a node that satisfies both requirements.

For example, if we add the following section to our trouble-shooter pod it will not be able to run on any node because it conflict with the nodeSelector:

```
affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/hostname
            operator: NotIn
            values:
            - k3d-k3s-default-worker-2
```  

## Pod affinity and anti-affinity

Pod affinity and anti-affinity provide yet another avenue for managing where your workloads run. All the methods we discussed so far - node selectors, taints/tolerations, node affinity/anti-affinity - where about assigning pods to nodes. But, pod affinity is about the relationships between different pods. Pod affinity has several other concepts associated with it: namespacing (since pods are namespaced), topology zone (node, rack, cloud provider zone, cloud provider region), weight (for preferred scheduling). A simple example is if you want hue-reminders to always be scheduled with a trouble-shooter pod. Let's see how to define it in the pod template spec of the hue-reminders deployment:

```
      affinity:
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: role
                operator: In
                values:
                - trouble-shooter
            topologyKey: failure-domain.beta.kubernetes.io/zone

```

Then after re-deploying hue-reminders all the hue-reminders pod are scheduled to run on worker-2 next to the trouble-shooter pod

```
$ k get po -o wide
NAME                             READY   STATUS    RESTARTS   AGE    IP           NODE                       
hue-learn-5c9bb545d9-nn4xk       1/1     Running   0          156m   10.42.1.15   k3d-k3s-default-worker-1
hue-learn-5c9bb545d9-sqx28       1/1     Running   0          12h    10.42.2.18   k3d-k3s-default-worker-2
hue-learn-5c9bb545d9-w8hrr       1/1     Running   0          12h    10.42.0.11   k3d-k3s-default-worker-0
hue-reminders-5cb9b845d8-kck5d   1/1     Running   0          14s    10.42.2.24   k3d-k3s-default-worker-2
hue-reminders-5cb9b845d8-kpvx5   1/1     Running   0          14s    10.42.2.23   k3d-k3s-default-worker-2
trouble-shooter                  1/1     Running   0          14m    10.42.2.21   k3d-k3s-default-worker-2
```

# Using namespaces to limit access

The Hue project is moving along nicely, and we have a few hundred microservices and about 100 developers and DevOps engineers working on it. Groups of related microservices emerge, and you notice that many of these groups are pretty autonomous. They are completely oblivious to the other groups. Also, there are some sensitive areas such as health and finance that you want to control access to more effectively. Enter namespaces.

Let's create a new service, Hue-finance, and put it in a new namespace called restricted.

Here is the YAML file for the new restricted namespace:

```
kind: Namespace
apiVersion: v1
metadata:
  name: restricted
  labels:
    name: restricted
```

We can create it as usual: 

```
$ kubectl create -f restricted-namespace.yaml
namespace "restricted" created
```

Once the namespace has been created, we can to configure a context for the namespace. This will allow restricting access just to this namespace to specific users:

```
$ kubectl config set-context restricted --namespace=restricted --cluster=default --user=default
Context "restricted" set.

$ kubectl config use-context restricted
Switched to context "restricted".
```

Let's check our cluster configuration:

```
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: DATA+OMITTED
    server: https://localhost:6443
  name: default
contexts:
- context:
    cluster: default
    user: default
  name: default
- context:
    cluster: default
    namespace: restricted
    user: default
  name: restricted
current-context: restricted
kind: Config
preferences: {}
users:
- name: default
  user:
    password: <REDACTED>
    username: admin
```    
As you can see, there are two contexts now and the current context is restricted. If we wanted too, we could even create dedicated users with their own credentials that are allowed to operate in the restricted namespace. This is not necessary in this case since we are the cluster admin.

Now, in this empty namespace, we can create our hue-finance service, and it will be on its own:

```
$ kubectl create -f hue-finance-deployment.yaml
deployment.apps/hue-learn created

$ kubectl get pods
NAME                           READY     STATUS    RESTARTS   AGE
hue-finance-7d4b84cc8d-gcjnz   1/1       Running   0          6s
hue-finance-7d4b84cc8d-tqvr9   1/1       Running   0          6s
hue-finance-7d4b84cc8d-zthdr   1/1       Running   0          6s
```

You don't have to switch contexts. You can also use the `--namespace=<namespace>` and `--all-namespaces` command-line switches, but when operating for a while in the same non-default namespace it's nice to set the context to that namespace.

# Using Kustomization for hierarchical cluster structures

This is not a typo. Kubectl recently incorporated the functionality of kustomize (https://kustomize.io/). It is a way to configure Kubernetes without templates. There was a lot of drama about the way the kustomize functionality was integrated into kubectl itself, since there are other options and it was an open question if kubectl should be that opinionated. But, that's all in the past. The bottom line is that `kubectl apply -k` unlocks a treasure trove of configuration options. Let's understand what problem  it helps us to solve and play take advantage of it to help us manage Hue.

## Understanding the basics of kustomize

Kustomize was created as a response to template-heavy approaches like Helm to configure and customize Kubernetes clusters. It is designed around the principle of declarative application management. It takes a valid Kubernetes YAML manifest (base) and specialize it or extend it by overlaying additional YAML patches (overlays). Overlays depend on their bases. All files are valid YAML files. There are no placeholders.

A kustomization.yaml file controls the process. Any directory that contains a kustomization.yaml fiel is called a root. For example:

```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: staging
commonLabels:
    environment: staging
bases:
  - ../base

patchesStrategicMerge:
  - hue-learn-patch.yaml

resources:
  - namespace.yaml
``` 

Kustomize can work well in GitOps environment where different kustomizations leave in a git repo and changes to the bases, overlays or kustomization.yaml files trigger a deployment.


One of the best use cases for kustomize is organizing your system into multiple namespaces such as staging and production. Let's restructure the Hue platform deployment manfiests.

## Configuring the directory structure

First, we need a base directory that will contain the commonalities of all the manifests. Then we will have an overlays directory that contains a staging and production sub-directories.

```
$ tree
.
├── base
│   ├── hue-learn.yaml
│   └── kustomization.yaml
├── overlays
│   ├── production
│   │   ├── kustomization.yaml
│   │   └── namespace.yaml
│   └── staging
│       ├── hue-learn-patch.yaml
│       ├── kustomization.yaml
│       └── namespace.yaml
```

The hue-learn.yaml file in the base directory is just an example. There may many files there. Let's review it quickly:

```
apiVersion: v1
kind: Pod
metadata:
  name: hue-learner
  labels:
    tier: internal-service
spec:
  containers:
  - name: hue-learner
    image: g1g1/hue-learn:0.3
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
    env:
    - name: DISCOVER_QUEUE
      value: dns
    - name: DISCOVER_STORE
      value: dns
```

It is very similar to the manifest we created earlier, but it doesn't have the "app: hue" label. It is not necessary because the label is provided by the kustomization.yaml file as a common label for all the listed resources.

```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
commonLabels:
  app: hue

resources:
  - hue-learn.yaml
```

## Applying kustomizations

We can observe the results by running the `kubectl kustomize` command on the base directory. You can see that the common label `app: hue`  was added:

```
$ kubectl kustomize base

apiVersion: v1
kind: Pod
metadata:
  labels:
    app: hue
    tier: internal-service
  name: hue-learner
spec:
  containers:
  - env:
    - name: DISCOVER_QUEUE
      value: dns
    - name: DISCOVER_STORE
      value: dns
    image: g1g1/hue-learn:0.3
    name: hue-learner
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
``` 

In order to actually deploy the kustomization we can run `kubectl -k apply`. But, the base is not supposed to be deployed on its own. Let's dive into the overlays/staging directory and examine it.

The namespace.yaml file just creates the staging namespace. It will also benefit from all the kustomizations as we'll soon see.

```
apiVersion: v1
kind: Namespace
metadata:
  name: staging
```

The kustomization.yaml file adds the common label `environment: staging`. It depends on the base directory and adds the namespace.yaml file to the resources list (which already includes the hue-learn.yaml from the base).

```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: staging
commonLabels:
    environment: staging
bases:
  - ../../base

patchesStrategicMerge:
  - hue-learn-patch.yaml

resources:
  - namespace.yaml
```

But, that's not all. The most interesting part of kustomizations is patching.

### Patching

Patches add or replace parts of manifests. They never remove exisitng resources or parts of resources. The hue-learn-patch.yaml update the image from `g1g1/hue-learn:0.3` to `g1g1/hue-learn:0.4`  

```
apiVersion: v1
kind: Pod
metadata:
  name: hue-learner
spec:
  containers:
  - name: hue-learner
    image: g1g1/hue-learn:0.4
```

This is a strategic merge. Kustomize supports another type of patch called `JsonPatches6902`. It is based on [RFC 6902](https://tools.ietf.org/html/rfc6902). It is often more concise than strategic merge. Note that since JSON is a subset of YAML we can use YAML syntax for JSON 6902 patches. Here is the same patch of changing the image version as   

```
- op: replace
  path: /spec/containers/0/image
  value: g1g1/hue-learn:0.4
```

### Kustomizing the entire staging namespace

Here is what kustomize generates when running it in on the overlays/staging directory:

```
$ kubextl kustomize overlays/staging

apiVersion: v1
kind: Namespace
metadata:
  labels:
    environment: staging
  name: staging
---
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: hue
    environment: staging
    tier: internal-service
  name: hue-learner
  namespace: staging
spec:
  containers:
  - env:
    - name: DISCOVER_QUEUE
      value: dns
    - name: DISCOVER_STORE
      value: dns
    image: g1g1/hue-learn:0.4
    name: hue-learner
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
```

Note that the namespace didn't inherit the `app: hue` label from the base, but only the `environment: staging` label from its local kustomization file. The hue-learn pod on the other hand got all labels as well the namespace designation.

It's time to deploy it to the cluster:

```
$ kubectl apply -k overlays/staging/
namespace/staging created
pod/hue-learner created
```

Now, we can review the pod in the newly created staging namespace:

```
$ kubectl get po -n staging
NAME          READY   STATUS    RESTARTS   AGE
hue-learner   1/1     Running   0          8s
```

# Launching jobs

Hue has evolved and has a lot of long-running processes deployed as microservices, but it also has a lot of tasks that run, accomplish some goal, and exit. Kubernetes supports this functionality via the Job resource. A Kubernetes job manages one or more pods and ensures that they run until success. If one of the pods managed by the job fails or is deleted, then the job will run a new pod until it succeeds.

There are also many serverless or function as a service solutions for Kubernetes, but they are built-on top of native Kubernetes. We will dedicate a whole chapter for serverless computing.


Here is a job that runs a Python process to compute the factorial of 5 (hint: it's 120):

```
apiVersion: batch/v1
kind: Job
metadata:
  name: factorial5
spec:
  template:
    metadata:
      name: factorial5
    spec:
      containers:
      - name: factorial5
        image: py-kube:0.2
        command: ["python",
                  "-c",
                  "import math; print(math.factorial(5))"]
      restartPolicy: Never
```

Note that the restartPolicy must be either Never or OnFailure. The default value - Always - is invalid because a job shouldn't restart after a successful completion.

Let's start the job and check its status:

```
$ kubectl create -f factorial-job.yaml
job.batch/factorial5 created

$ kubectl get jobs
NAME         COMPLETIONS   DURATION   AGE
factorial5   1/1           2s         2m53s
```

The pods of completed tasks are displayed with a status of "Completed":

```
$ kubectl get pods
NAME                             READY   STATUS      RESTARTS   AGE
factorial5-tf9qb                 0/1     Completed   0          26m
hue-learn-5c9bb545d9-nn4xk       1/1     Running     3          2d11h
hue-learn-5c9bb545d9-sqx28       1/1     Running     3          2d21h
hue-learn-5c9bb545d9-w8hrr       1/1     Running     3          2d21h
hue-reminders-5cb9b845d8-kck5d   1/1     Running     3          2d8h
hue-reminders-5cb9b845d8-kpvx5   1/1     Running     3          2d8h
trouble-shooter                  1/1     Running     3          2d9h
```

The factorial5 pod has a status of "Completed." Let's check out its output in the logs:

```
$ kubectl logs factorial5-tf9qb
120
```

## Running jobs in parallel

You can also run a job with parallelism. There are two fields in the spec, called completions and parallelism. The completions are set to 1 by default. If you want more than one successful completion, then increase this value. Parallelism determines how many pods to launch. A job will not launch more pods than needed for successful completions, even if the parallelism number is greater.

Let's run another job that just sleeps for 20 seconds until it has three successful completions. We'll use a parallelism factor of six, but only three pods will be launched:

```
apiVersion: batch/v1
kind: Job
metadata:
  name: sleep20
spec:
  completions: 3
  parallelism: 6
  template:
    metadata:
      name: sleep20
    spec:
      containers:
      - name: sleep20
        image: g1g1/py-kube:0.2
        command: ["python",
                  "-c",
                  "import time; print('started...');
                   time.sleep(20); print('done.')"]
      restartPolicy: Never
```

We can now see that all jobs completed and the pods are not ready because they already did the job

```
$ kubectl get pods
NAME               READY     STATUS    RESTARTS   AGE
sleep20-2mb7g      0/1       Completed   0          17m
sleep20-74pwh      0/1       Completed   0          15m
sleep20-txgpz      0/1       Completed   0          15m
```

## Cleaning up completed jobs

When a job completes, it sticks around – and its pods, too. This is by design, so you can look at logs or connect to pods and explore. But normally, when a job has completed successfully, it is not needed anymore. It's your responsibility to clean up completed jobs and their pods. The easiest way is to simply delete the job object, which will delete all the pods too:

```
$ kubectl get jobs
NAME         COMPLETIONS   DURATION   AGE
factorial5   1/1           2s         6h59m
sleep20      3/3           3m7s       5h54m

$ kubectl delete job factorial5
job.batch "factorial5" deleted

$ kubectl delete job sleep20
job.batch "sleep20" deleted
```

## Scheduling cron jobs

Kubernetes cron jobs are jobs that run for a specified time, once or repeatedly. They behave as regular Unix cron jobs specified in the /etc/crontab file.

In Kubernetes 1.4 they were known as a ScheduledJob. But, in Kubernetes 1.5, the name was changed to CronJob. Starting with Kubernetes 1.8 the CronJob resource is enabled by default in the API server and there is no need to pass a --runtime-config flag anymore, but it's still in Beta. Here is the configuration to launch a cron job every minute to remind you to stretch. In the schedule, you may replace the \* with ?:

```
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: cron-demo
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            name: cron-demo
        spec:
          containers:
          - name: cron-demo
            image: g1g1/py-kube:0.2
            args:
            - python
            - -c
            - from datetime import datetime; print('[{}] CronJob demo here...'.format(datetime.now()))
          restartPolicy: OnFailure
```          

In the pod spec, under the job template, I added a label name: cron-demo.  The reason is that cron jobs and their pods are assigned names with a random prefix by Kubernetes. The label allows you to easily discover all the pods of a particular cron job.

See the following command lines:

```
$ kubectl get pods

NAME                         READY   STATUS      RESTARTS   AGE
cron-demo-1568250120-7jrq8   0/1     Completed   0          3m
cron-demo-1568250180-sw5qq   0/1     Completed   0          2m
cron-demo-1568250240-mmfzm   0/1     Completed   0          1m
```

Note that each invocation of a cron job launches a new job object with a new pod:

```
$ kubectl get jobs
NAME                   COMPLETIONS   DURATION   AGE
cron-demo-1568244780   1/1           2s         1m
cron-demo-1568250060   1/1           3s         88s
cron-demo-1568250120   1/1           3s         38s
```



As usual, you can check the output of the pod of a completed cron job using the logs command:

```
$ kubectl logs cron-demo-1568250240-mmfzm
[2019-09-12 01:04:03.245204] CronJob demo here...
```

When you delete a cron job it stops scheduling new jobs, delete all the existing job objects and all the pods it created.

You can use the designated label (name=cron-demo in this case) to locate all the job objects launched by the cron job. You can also suspend a cron job so it doesn't create more jobs without deleting completed jobs and pods. You can also manage previous job by setting in the spec history limits: .spec.successfulJobsHistoryLimit and .spec.failedJobsHistoryLimit.

# Mixing non-cluster components

Most real-time system components in the Kubernetes cluster will communicate with out-of-cluster components. Those could be completely external third-party services accessible through some API, but can also be internal services running in the same local network that, for various reasons, are not part of the Kubernetes cluster.

There are two categories here: inside the cluster network and outside the cluster network. Why is the distinction important?

## Outside-the-cluster-network components

These components have no direct access to the cluster. They can only access it through APIs, externally visible URLs, and exposed services. These components are treated just like any external user. Often, cluster components will just use external services, which pose no security issue. For example, in a previous job we had a Kubernetes cluster that reported exceptions to a third-party service (https://sentry.io/welcome/). It was one-way communication from the Kubernetes cluster to the third-party service.

## Inside-the-cluster-network components

These are components that run inside the network but are not managed by Kubernetes. There are many reasons to run such components. They could be legacy applications that have not been kubernetized yet, or some distributed data store that is not easy to run inside Kubernetes. The reason to run these components inside the network is for performance, and to have isolation from the outside world so traffic between these components and pods can be more secure. Being part of the same network ensures low-latency, and the reduced need for authentication is both convenient and can avoid authentication overhead.

## Managing the Hue platform with Kubernetes

In this section, we will look at how Kubernetes can help operate a huge platform such as Hue. Kubernetes itself provides a lot of capabilities to orchestrate pods and manage quotas and limits, detecting and recovering from certain types of generic failures (hardware malfunctions, process crashes, unreachable services). But, in a complicated system such as Hue, pods and services may be up-and-running but in an invalid state or waiting for other dependencies in order to perform their duties. This is tricky because if a service or pod is not ready yet but is already receiving requests, then you need to manage it somehow: fail (puts responsibility on the caller), retry (how many times? for how long? how often?), and queue for later (who will manage this queue?).

It is often better if the system at large can be aware of the readiness state of different components, or if components are visible only when they are truly ready. Kubernetes doesn't know Hue, but it provides several mechanisms such as liveness probes, readiness probes, and init containers to support application-specific management of your cluster.

### Using liveness probes to ensure your containers are alive

kubelet watches over your containers. If a container process crashes, kubelet will take care of it based on the restart policy. But this is not always enough. Your process may not crash, but instead run into an infinite loop or a deadlock. The restart policy might not be nuanced enough. With a liveness probe, you get to decide when a container is considered alive. Here is a pod template for the Hue music service. It has a livenessProbe section, which uses the httpGet probe. An HTTP probe requires a scheme (http or https, default to http, a host [default to PodIp], a path, and a port). The probe is considered successful if the HTTP status is between 200 and 399. Your container may need some time to initialize, so you can specify an initialDelayInSeconds. The Kubelet will not hit the liveness check during this period:

```
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: music
    service: music
  name: hue-music
spec:
  containers:
    image: g1g1/hue-music
    livenessProbe:
      httpGet:
        path: /pulse
        port: 8888
        httpHeaders:
          - name: X-Custom-Header
            value: ItsAlive
      initialDelaySeconds: 30
      timeoutSeconds: 1
    name: hue-music
```

If a liveness probe fails for any container, then the pod's restart policy goes into effect. Make sure your restart policy is not Never, because that will make the probe useless.

There are two other types of probe:

- TcpSocket – Just check that a port is open
- Exec – Run a command that returns 0 for success

## Using readiness probes to manage dependencies

Readiness probes are used for different purpose. Your container may be up-and-running, but it may depend on other services that are unavailable at the moment. For example, Hue-music may depend on access to a data service that contains your listening history. Without access, it is unable to perform its duties. In this case, other services or external clients should not send requests to the Hue music service, but there is no need to restart it. Readiness probes address this use case. When a readiness probe fails for a container, the container's pod will be removed from any service endpoint it is registered with. This ensures that requests don't flood services that can't process them. Note that you can also use readiness probes to temporarily remove pods that are overbooked until they drain some internal queue.

Here is a sample readiness probe. I use the exec probe here to execute a custom command. If the command exits a non-zero exit code, the container will be torn down:

```
readinessProbe:
  exec:
    command:
        - /usr/local/bin/checker
        - --full-check
        - --data-service=hue-multimedia-service
  initialDelaySeconds: 60
  timeoutSeconds: 5
```

It is fine to have both a readiness probe and a liveness probe on the same container as they serve different purposes.

## Employing init containers for orderly pod bring-up

Liveness and readiness probes are great. They recognize that, at startup, there may be a period where the container is not ready yet, but shouldn't be considered failed. To accommodate that there is the initialDelayInSeconds setting where containers will not be considered failed. But, what if this initial delay is potentially very long? Maybe, in most cases, a container is ready after a couple of seconds and ready to process requests, but because the initial delay is set to five minutes just in case, we waste a lot of time where the container is idle. If the container is part of a high-traffic service, then many instances can all sit idle for five minutes after each upgrade and pretty much make the service unavailable.

Init containers address this problem. A pod may have a set of init containers that run to completion before other containers are started. An init container can take care of all the non-deterministic initialization and let application containers with their readiness probe have minimal delay.

Init containers came out of Beta in Kubernetes 1.6. You specify them in the pod spec as the initContainers field, which is very similar to the containers field. Here is an example:

```
apiVersion: v1
kind: Pod
metadata:
  name: hue-fitness
spec:
  containers:
    name: hue-fitness
    Image: hue-fitness:v4.4
  InitContainers:
    name: install
    Image: busybox
    command: /support/safe_init
    volumeMounts:
    - name: workdir
      mountPath: /workdir
```

## Pod readiness and readiness gates

Pod readiness was introduced in Kubernetes 1.11 and became stable in Kubernetes 1.14. While readiness probes allow you to determine at the pod level if it's ready to serve requests the overall infrastructure that supports delivering traffic to the pod might not be ready yet. For example, the service, network policy and load balancer might take some extra time. This can be a problem especially during rolling deployments where Kubernetes might terminate the old pods before the new pods are really ready, which will cause degradation is service capacity and even cause a service outage in extreme cases (all old pods where terminated and no new pod is fully ready).

This the problem that the [Pod ready++](https://github.com/kubernetes/enhancements/blob/master/keps/sig-network/0007-pod-ready%2B%2B.md) proposal addresses. The idea is to extend the concept of pod readiness to check additional conditions in addition to making sure all the containers are ready. This is done by adding a new field to the PodSpec called `readinessGates`. You can specify a set of conditions that must be satisfied for the pod to be considered ready. In the following example the pod is not ready because the "www.example.com/feature-1" condition has status: "False".

```
Kind: Pod
...
spec:
  readinessGates:
    - conditionType: "www.example.com/feature-1"
status:
  conditions:
    - type: Ready  # this is a builtin PodCondition
      status: "False"
      lastProbeTime: null
      lastTransitionTime: 2018-01-01T00:00:00Z
    - type: "www.example.com/feature-1"   # an extra PodCondition
      status: "False"
      lastProbeTime: null
      lastTransitionTime: 2018-01-01T00:00:00Z
  containerStatuses:
    - containerID: docker://abcd...
      ready: true
...
```   

## Sharing with DaemonSet pods

DaemonSet pods are pods that are deployed automatically, one per node (or a designated subset of the nodes). They are typically used for keeping an eye on nodes and ensuring they are operational. This is a very important function, which we will cover in _Chapter 13,_ _Monitoring, Logging, Tracing and Troubleshooting_. But they can be used for much more. The nature of the default Kubernetes scheduler is that it schedules pods based on resource availability and requests. If you have lots of pods that don't require a lot of resources, similarly many pods will be scheduled on the same node. Let's consider a pod that performs a small task and then, every second, sends a summary of all its activities to a remote service. Now, imagine that, on average, 50 of these pods are scheduled on the same node. This means that, every second, 50 pods make 50 network requests with very little data. How about we cut it down by 50× to just a single network request? With a DaemonSet pod, all the other 50 pods can communicate with it instead of talking directly to the remote service. The DaemonSet pod will collect all the data from the 50 pods and, once a second, will report it in aggregate to the remote service. Of course, that requires the remote service API to support aggregate reporting. The nice thing is that the pods themselves don't have to be modified; they will just be configured to talk to the DaemonSet pod on localhost instead of the remote service. The DaemonSet pod serves as an aggregating proxy.

The interesting part about this configuration file is that the hostNetwork, hostPID, and hostIPC options are set to true. This enables the pods to communicate efficiently with the proxy, utilizing the fact they are running on the same physical host:

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: hue-collect-proxy
  labels:
    tier: stats
    app: hue-collect-proxy
spec:
  template:
    metadata:
      labels:
        hue-collect-proxy
    spec:
      hostPID: true
      hostIPC: true
      hostNetwork: true
      containers:
          image: the_g1g1/hue-collect-proxy
          name: hue-collect-proxy
```

# Evolving the Hue platform with Kubernetes

In this section, we'll discuss other ways to extend the Hue platform and service additional markets and communities. The question is always, what Kubernetes features and capabilities can we use to address new challenges or requirements?

## Utilizing Hue in the enterprise

The enterprise often can't run in the Cloud, either due to security and compliance reasons, or for performance reasons because the system has work with data and legacy systems that are not cost-effective to move to the Cloud. Either way, Hue for enterprise must support on-premise clusters and/or bare-metal clusters.

While Kubernetes is most often deployed on the Cloud, and even has a special Cloud-provider interface, it doesn't depend on the Cloud and can be deployed anywhere. It does require more expertise, but enterprise organizations that already run systems on their own data centers have that expertise.


## Advancing science with Hue

Hue is so great at integrating information from multiple sources that it would be a boon for the scientific community. Consider how Hue can help multi-disciplinary collaboration between scientists from different disciplines.

A network of scientific communities might require deployment across multiple geographically distributed clusters. Enter cluster federation. Kubernetes has this use use case in mind and evolves its support. We will discuss it at length in a later chapter.

## Educating the kids of the future with hue

Hue can be utilized for education and provide many services to online education systems. But, privacy concerns may prevent deploying Hue for kids as a single, centralized system. One possibility is to have a single cluster, with namespaces for different schools. Another deployment option is that each school or county has its own Hue Kubernetes cluster. In the second case, Hue for education must be extremely easy to operate to cater for schools without a lot of technical expertise. Kubernetes can help a lot by providing self-healing and auto-scaling features and capabilities for Hue, to be as close to zero-administration as possible.

# Summary

In this chapter, we designed and planned the development, deployment, and management of the Hue platform – an imaginary omniscient and omnipotent service – built on microservice architecture. We used Kubernetes as the underlying orchestration platform, of course, and delved into many of its concepts and resources. In particular, we focused on deploying pods for long-running services as opposed to jobs for launching short-term or cron jobs, explored internal services versus external services, and also used namespaces to segment a Kubernetes cluster. Then we looked at the management of a large system such as Hue with liveness and readiness probes, init containers, and daemon sets.

You should now feel comfortable architecting web-scale systems composed of microservices and understand how to deploy and manage them in a Kubernetes cluster.

In the next chapter, we will look into the super-important area of storage. Data is king, but often the least flexible element of the system. Kubernetes provides a storage model, and many options for integrating with various storage solutions.

# Reference

https://blog.jetstack.io/blog/kustomize-cert-manager/
https://skryvets.com/blog/2019/05/15/kubernetes-kustomize-json-patches-6902
