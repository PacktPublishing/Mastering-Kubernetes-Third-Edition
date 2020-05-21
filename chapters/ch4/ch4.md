In _Chapter 3, _High Availability and Reliability_, we looked at reliable and highly available Kubernetes clusters, the basic concepts, the best practices, how to do live updates, and the many design trade-offs regarding performance and cost.

In this chapter, we will explore the important topic of security. Kubernetes clusters are complicated systems composed of multiple layers of interacting components. Isolation and compartmentalization of different layers is very important when running critical applications. To secure the system and ensure proper access to resources, capabilities, and data, we must first understand the unique challenges facing Kubernetes as a general-purpose orchestration platform that runs unknown workloads. Then we can take advantage of various securities, isolation, and access control mechanisms to make sure the cluster, the applications running on it, and the data are all safe. We will discuss various best practices and when it is appropriate to use each mechanism.

At the end of this chapter, you will have a good understanding of Kubernetes security challenges. You will gain practical knowledge of how to harden Kubernetes against various potential attacks, establishing defense in depth, and will even be able to safely run a multi-tenant cluster while providing different users full isolation as well as full control over their part of the cluster.

# Understanding Kubernetes security challenges

Kubernetes is a very flexible system that manages very low-level resources in a generic way. Kubernetes itself can be deployed on many operating systems and hardware or virtual-machine solutions, on-premises or in the cloud. Kubernetes runs workloads implemented by runtimes it interacts with through a well-defined runtime interface, but without understanding how they are implemented. Kubernetes manipulates critical resources such as networking, DNS, and resource allocation on behalf or in service of applications it knows nothing about. This means that Kubernetes is faced with the difficult task of providing good security mechanisms and capabilities in a way that application developers and cluster administrators can utilize, while protecting itself, the developers and the administrators from common mistakes.

In this section, we will discuss security challenges in several layers or components of a Kubernetes cluster: nodes, network, images, pods, and containers. Defense in depth is an important security concept that requires systems to protect themselves at each level, both to mitigate attacks that penetrated other layers and to limit the scope and damage of a breach. Recognizing the challenges in each layer is the first step towards defense in depth.

## Node challenges

The nodes are the hosts of the runtime engines. If an attacker gets access to a node, this is a serious threat. It can control at least the host itself and all the workloads running on it. But it gets worse. The node has a kubelet running that talks to the API server. A sophisticated attacker can replace the kubelet with a modified version and effectively evade detection by communicating normally with the Kubernetes API server, yet running its own workloads instead of the scheduled workloads, collecting information about the overall cluster and disrupt the API server and the rest of the cluster by sending malicious messages. The node will have access to shared resources and to secrets that may allow it to infiltrate even deeper. A node breach is very serious, both because of the possible damage and the difficulty of detecting it after the fact.

Nodes can be compromised at the physical level too. This is more relevant on bare-metal machines where you can tell which hardware is assigned to the Kubernetes cluster.

Another attack vector is resource drain. Imagine that your nodes become part of a bot network that, unrelated to your Kubernetes cluster, just runs its own workloads like crypto currency mining and drains CPU and memory. The danger here is that your cluster will choke and run out of resources to run your workloads or alternatively your infrastructure may scale automatically and allocate more resources until.

Another problem is installation of debugging and troubleshooting tools or modifying configuration outside of automated deployment. Those are typically untested and, if left behind and active, can lead to at least degraded performance, but can also cause more sinister problems. At the least that increase the attack surface.

Where security is concerned, it's a numbers game. You want to understand the attack surface of the system and where you're vulnerable. Let's list all the node challenges:

- Attacker takes control of the host
- Attacker replaces the kubelet
- Attacker takes control over a node that runs master components (API server, scheduler, controller manager)
- Attacker gets physical access to a node
- Attacker drains resources unrelated to the Kubernetes cluster
- Self-inflicted damage through installation of debugging and troubleshooting tools or configuration change

## Network challenges

Any non-trivial Kubernetes cluster spans at least one network. There are many challenges related to networking. You need to understand how your system components are connected at a very fine level. Which components are supposed to talk to each other? What network protocols do they use? What ports? What data do they exchange? How is your cluster connected to the outside world?

There is a complex chain of exposing ports and capabilities or services:

- Container to host
- Host to host within the internal network
- Host to the world

Using overlay networks (which will be discussed more in Chapter 10, Advanced Kubernetes Networking) can help with defense in depth where, even if an attacker gains access to a container, they are sandboxed and can't escape to the underlay network's infrastructure.

Discovering components is a big challenge too. There are several options here, such as DNS, dedicated discovery services, and load balancers. Each comes with a set of pros and cons that take careful planning and insight to get right for your situation.

Making sure two containers can find each other and exchange information is not trivial.

You need to decide which resources and endpoints should be publicly accessible. Then you need to come up with a proper way to authenticate users and services, and authorize them to operate on resources. Often you may want to control access between internal services too.

Sensitive data must be encrypted on the way in and out of the cluster and sometimes at rest, too. That means key management and safe key exchange, which is one of the most difficult problems to solve in security.

If your cluster shares networking infrastructure with other Kubernetes clusters or non-Kubernetes processes then you have to be diligent about isolation and separation.

The ingredients are network policies, firewall rules, and **software-defined networking** ( **SDN** ). The recipe is often customized. This is especially challenging with on-premise and bare-metal clusters. Let's recap:

- Come up with a connectivity plan
- Choose components, protocols, and ports
- Figure out dynamic discovery
- Public versus private access
- Authentication and authorization (including between internal services)
- Design firewall rules
- Decide on a network policy
- Key management and exchange

There is a constant tension between making it easy for containers, users, and services to find and talk to each other at the network level versus locking down access and preventing attacks through the network or attacks on the network itself.

Many of these challenges are not Kubernetes-specific. However, the fact that Kubernetes is a generic platform that manages key infrastructure and deals with low-level networking makes it necessary to think about dynamic and flexible solutions that can integrate system-specific requirements into Kubernetes.

## Image challenges

Kubernetes runs containers that comply with one of its runtime engines. It has no idea what these containers are doing (except collecting metrics). You can put certain limits on containers via quotas. You can also limit their access to other parts of the network via network policies. But, in the end, containers do need access to host resources, other hosts in the network, distributed storage, and external services. The image determines the behavior of a container. There are two categories of problems with images:

- Malicious images
- Vulnerable images

Malicious images are images that contain code or configuration that was designed by an attacker to do some harm,  collect information or just take advantage of your infrastructure for their purposes (e.g. crypto mining). Malicious code can be injected into your image preparation pipeline, including any image repositories you use. Alternatively, you may install third party images that were compromised themselves and now contain malicious code.

Vulnerable images are images you designed (or third party images you install) that just happen to contain some vulnerability that allows an attacker to take control of the running container or cause some other harm, including injecting their own code later.

It's hard to tell which category is worse. At the extreme, they are equivalent because they allow seizing total control of the container. The other defenses that are in place (remember defense in depth?), and the restrictions you put on the container will determine how much damage it can do. Minimizing the danger of bad images is very challenging. Fast-moving companies utilizing microservices may generate many images daily. Verifying an image is not an easy task either. Consider, for example, how Docker images are made of layers.

The base images that contain the operating system may become vulnerable any time a new vulnerability is discovered. Moreover, if you rely on base images prepared by someone else (very common) then malicious code may find its way into those base images, which you have no control over and you trust implicitly.

When a vulnerability in a 3rd party dependency is discovered, ideally there is already a fixed version and you should patch it as soon as possible.

To summarize image challenges:

- Kubernetes doesn't know what images are doing
- Kubernetes must provide access to sensitive resources for the designated function
- It's difficult to protect the image preparation and delivery pipeline (including image repositories)
- Speed of development and deployment of new images conflict with careful review of changes
- Base images that contain the OS or other common dependencies can easily get out of date and become vulnerable
- Base images are often not under your control and might be more prone to injection of malicious code


Integrating a static image analyzer like CoreOS Clair or Anchor engine into your CI/CD pipeline can help a lot. In addition minimizing the blast radius by limiting the resources access of containers only to what they need to perform their job, can reduce the impact on your system if a container gets compromised. You must also be diligent about patching known vulnerabilities.  

## Configuration and deployment challenges

Kubernetes clusters are administered remotely. Various manifests and policies determine the state of the cluster at each point in time. If an attacker gets access to a machine with administrative control over the cluster, they can wreak havoc, such as collecting information, injecting bad images, weakening security, and tempering with logs. As usual, bugs and mistakes can be just as harmful; by neglecting important security measures and leaving the cluster open for an attack. It is very common these days for employees with administrative access to the cluster to work remotely from home or a coffee shop and have their laptops with them, where you are just one kubectl command from opening the flood gates.

Let's reiterate the challenges:

- Kubernetes is administered remotely
- An attacker with remote administrative access can gain complete control over the cluster
- Configuration and deployment is typically more difficult to test than code
- Remote or out-of-office employees risk extended exposure, allowing an attacker to gain access to their laptops or phones with administrative access

There are some best practices to minimize this risk such as layer of indirection in the form of a jump box, requiring a VPN connection, using multi-factor authentication and one time passwords. 

## Pod and container challenges

In Kubernetes, pods are the unit of work and contain one or more containers. The pod is a grouping and deployment construct. But, often containers that are deployed together in the same pod interact through direct mechanisms. The containers all share the same localhost network and often share mounted volumes from the host. This easy integration between containers in the same pod can result in exposing parts of the host to all the containers. This might allow one bad container (either malicious or just vulnerable) to open the way for escalated attack on other containers in the pod and later taking over the node itself and the entire cluster. Master add-ons are often collocated with master components and present that kind of danger, especially because many of them are experimental. The same goes for daemon sets that run pods on every node. The practice of sidecar containers where additional containers are deployed in a pod along your application container is very popular especially with service meshes. That increases that risk because the sidecar containers are often outside your control and if compromised can provide access to your infrastructure. 

Multi-container pod challenges include the following:

- Same pod containers share the localhost network
- Same pod containers sometimes share a mounted volume on the host filesystem
- Bad containers might poison other containers in the pod
- Bad containers have an easier time attacking the node if co-located with the another container that access crucial node resources
- Experimental add-ons that are collocated with master components might be experimental and less secure
- Service meshes introduce sidecar container that might become an attack vector

Consider carefully the interaction between containers running in the same pod. You should realize that a bad container might try to compromise its sibling containers in the same pod as its first attack.  

## Organisational, cultural, and process challenges

Security is often in contrast with productivity. This is a normal trade-off and nothing to worry about. Traditionally, when developers and operations were separate, this conflict was managed at an organizational level. Developers pushed for more productivity and treated security requirements as the cost of doing business. Operations controlled the production environment and were responsible for access and security procedures. The DevOps movement brought down the wall between developers and operations. Now, speed of development often takes a front row seat. Concepts such as continuous deployment deploying multiple times a day without human intervention were unheard of in most organizations. Kubernetes was designed for this new world of cloud-native applications. But, it was developed based on Google's experience. Google had a lot of time and skilled experts to develop the proper processes and tooling to balance rapid deployments with security. For smaller organizations, this balancing act might be very challenging and security could be weakened by focusing too much on productivity.

The challenges facing organizations that adopt Kubernetes are as follows:

- Developers that control operation of Kubernetes might be less security-oriented
- Speed of development might be considered more important than security
- Continuous deployment might make it difficult to detect certain security problems before they reach production
- Smaller organizations might not have the knowledge and expertise to manage security properly in Kubernetes clusters

There are no easy answers here. You should be deliberate in striking the right balance between security and agility. I recommend to have a dedicated security team (or at least one person) that are focused on security, participate in all planning meetings and advocate for security. It's important to bake security into your system from the get go.

In this section, we reviewed the many challenges you face when you try to build a secure Kubernetes cluster. Most of these challenges are not specific to Kubernetes, but using Kubernetes means there is a large part of your system that is generic and is unaware of what the system is doing. This can pose problems when trying to lock down a system. The challenges are spread across different levels:

- Node challenges
- Network challenges
- Image challenges
- Configuration and deployment challenges
- Pod and container challenges
- Organizational and process challenges

In the next section, we will look at the facilities Kubernetes provides to address some of those challenges. Many of the challenges require solutions at the larger system scope. It is important to realize that just utilizing all of Kubernetes security features is not enough.

# Hardening Kubernetes

The previous section cataloged and listed the variety of security challenges facing developers and administrators deploying and maintaining Kubernetes clusters. In this section, we will hone in on the design aspects, mechanisms, and features offered by Kubernetes to address some of the challenges. You can get to a pretty good state of security by judicious use of capabilities such as service accounts, network policies, authentication, authorization, admission control, AppArmor, and secrets.

Remember that a Kubernetes cluster is one part of a bigger system that includes other software systems, people, and processes. Kubernetes can't solve all problems. You should always keep in mind general security principles, such as defense in depth, need-to-know basis, and the principle of least privilege. In addition, log everything you think may be useful in the event of an attack and have alerts for early detection when the system deviates from its state. It may be just a bug or it may be an attack. Either way, you want to know about it and respond.

## Understanding service accounts in Kubernetes

Kubernetes has regular users managed outside the cluster for humans connecting to the cluster (for example, via the kubectl command), and it has service accounts.

Regular user accounts are global and can access multiple namespaces in the cluster. Service accounts are constrained to one namespace. This is important. It ensures namespace isolation, because whenever the API server receives a request from a pod, its credentials will apply only to its own namespace.

Kubernetes manages service accounts on behalf of the pods. Whenever Kubernetes instantiates a pod it assigns the pod a service account. The service account identifies all the pod processes when they interact with the API server. Each service account has a set of credentials mounted in a secret volume. Each namespace has a default service account called default. When you create a pod, it is automatically assigned the default service account unless you specify a different service account.

You can create additional service accounts. Create a file called custom-service-account.yaml with the following content:

```
apiVersion: v1
kind: ServiceAccount
metadata:
  name: custom-service-account
```

Now type the following:

```
$ kubectl create -f custom-service-account.yaml
serviceaccount/custom-service-account created
```

Here is the service account listed alongside the default service account:

```
$ kubectl get serviceAccounts
NAME                                    SECRETS   AGE
custom-service-account                  1         39s
default                                 1         18d
```

Note that a secret was created automatically for your new service account.

To get more detail, type the following:

```
$ kubectl get serviceAccounts/custom-service-account -o yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  creationTimestamp: "2019-08-21T01:24:24Z"
  name: custom-service-account
  namespace: default
  resourceVersion: "654316"
  selfLink: /api/v1/namespaces/default/serviceaccounts/custom-service-account
  uid: 69393e47-c3b2-11e9-bb43-0242ac130002
secrets:
- name: custom-service-account-token-kdwhs
```


You can see the secret itself, which includes a ca.crt file and a token, by typing the following:

```
$ kubectl get secret custom-service-account-token-kdwhs -o yaml
```

### How does Kubernetes manage service accounts?

The API server has a dedicated component called service account admission controller. It is responsible for checking, at pod creation time, if it has a custom service account and, if it does, that the custom service account exists. If there is no service account specified, then it assigns the default service account.

It also ensures the pod has ImagePullSecrets, which are necessary when images need to be pulled from a remote image registry. If the pod spec doesn't have any secrets, it uses the service account's ImagePullSecrets.

Finally, it adds a volume with an API token for API access and a volumeSource mounted at /var/run/secrets/kubernetes.io/serviceaccount.

The API token is created and added to the secret by another component called the **Token Controller** whenever a service account is created. The Token Controller also monitors secrets and adds or removes tokens wherever secrets are added or removed to/from a service account.

The service account controller ensures the default service account exists for every namespace.

## Accessing the API server

Accessing the API server requires a chain of steps that include authentication, authorization, and admission control. At each stage the request may be rejected. Each stage consists of multiple plugins that are chained together. The following diagram illustrates this:

???? images/auth flow.png


### Authenticating users

When you first create the cluster some keys and certificates are created for you to authenticate against the cluster. Kubectl uses them to authenticate itself to the API server and vice versa over TLS (an encrypted HTTPS connection). You can view your configuration using this command:

```
$ kubectl config view
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
    password: DATA+OMITTED
    username: admin
```    

This is the configuration for a k3d cluster. It may look different for other types of clusters. 


Note that if multiple users need to access the cluster, the creator should provide the necessary client certificates and keys to the other users in a secure manner.

This is just establishing basic trust with the Kubernetes API server itself. You're not authenticated yet. Various authentication modules may look at the request and check for various additional client certificates, password, bearer tokens, and JWT tokens (for service accounts). Most requests require an authenticated user (either a regular user or a service account), although there are some anonymous requests too. If a request fails to authenticate with all the authenticators it will be rejected with a 401 HTTP status code (unauthorized, which is a bit of a misnomer).

The cluster administrator determines what authentication strategies to use by providing various command-line arguments to the API server:

- --client-ca-file=<filename> (for x509 client certificates specified in a file)
- --token-auth-file=<filename> (for bearer tokens specified in a file)
- --basic-auth-file=<filename> (for user/password pairs specified in a file)
- --experimental-bootstrap-token-auth (for bootstrap tokens used by kubeadm)

Service accounts use an automatically loaded authentication plugin. The administrator may provide two optional flags:

- --service-account-key-file=<filename> (PEM encoded key for signing bearer tokens. If unspecified, the API server's TLS private key will be used.)
- --service-account-lookup (If enabled, tokens that are deleted from the API will be revoked.)

There are several other methods, such as open ID connect, web hook, keystone (the OpenStack identity service), and authenticating proxy. The main theme is that the authentication stage is extensible and can support any authentication mechanism.

The various authentication plugins will examine the request and, based on the provided credentials, will associate the following attributes:

- **username** (user-friendly name),
- **uid** (unique identifier and more consistent than the username)
- **groups** (a set of group names the user belongs to).
- **extra fields** maps string keys to string values.

In Kubernetes 1.11 kubectl gained the ability to use credential plugins to receive an opaque token from a provider like an organizational LDAP server. These credentials are sent by kubectl to the API server that typically uses a webhook token authenticator to authenticate the credentials and accept the request. 

The authenticators have no knowledge whatsoever of what a particular user is allowed to do. They just map a set of credentials to a set of identities. The authenticators run in unspecified order, the first authenticator to accept the passed credentials will associate an identity with the incoming request and the authentication is considered successful. If all authenticators reject the credentials then authentication failed.

#### Impersonation

- It is possible for users to impersonate different users (with proper authorization). For example, an admin may want to troubleshoot some issue as a different user with less privileges. This requires passing impersonation headers to the API request. The headers are:
- **Impersonate-User** : The username to act as.
- **Impersonate-Group** : A group name to act as. Can be provided multiple times to set multiple groups. Optional. Requires 'Impersonate-User'
- **Impersonate-Extra-(extra name)**: A dynamic header used to associate extra fields with the user. Optional. Requires 'Impersonate-User'

With kubectl you pass --as and --as-group parameters.

### Authorizing requests

Once a user is authenticated, authorization commences. Kubernetes has generic authorization semantics. A set of authorization modules receives the request, which includes information such as the authenticated username and the request's verb (list, get, watch, create, and so on). Unlike authentication all authorization plugins will get a shot at any request. If a single authorization plugin rejects the request or no plugin had an opinion then it will be rejected with a 403 HTTP status code (forbidden). A request will be continue only if at least one plugin accepted and no other plugin rejected it.

The cluster administrator determines what authorization plugins to use by specifying the --authorization-mode command-line flag, which is a comma-separated list of plugin names.

The following modes are supported:

- --authorization-mode=AlwaysDeny rejects all requests; use if you don't need authorization
- --authorization-mode=AlwaysAllow allows all requests; use if you don't need authorization. useful during testing.
- --authorization-mode=ABAC allows for a simple local-file-based, user-configured authorization policy. ABAC stands for Attribute-Based Access Control.
- --authorization-mode=RBAC is a role-based mechanism where authorization policies are stored and driven by the Kubernetes API. RBAC stands for Role-Based Access Control.
- --authorization-mode=Node is a special mode designed to authorize API requests made by kubelets.
- --authorization-mode=Webhook allows for authorization to be driven by a remote service using REST.

You can add your own custom authorization plugin by implementing the following straightforward Go interface:

```
type Authorizer interface {

  Authorize(a Attributes) (authorized bool, reason string, err error)

}
```

The Attributes input argument is also an interface that provides all the information you need to make an authorization decision:

```
type Attributes interface {
  GetUser() user.Info
  GetVerb() string
  IsReadOnly() bool
  GetNamespace() string
  GetResource() string
  GetSubresource() string
  GetName() string
  GetAPIGroup() string
  GetAPIVersion() string
  IsResourceRequest() bool
  GetPath() string
}
```

You can find the source code here:
See https://github.com/kubernetes/apiserver/blob/master/pkg/authorization/authorizer/interfaces.go

Using the `kubectl can-i` command you check what actions you can perform and even impersonate other users:

```
$ kubectl auth can-i create deployments
yes

$ kubectl auth can-i create deployments --as jack
no
```

### Using admission control plugins

OK. The request was authenticated and authorized, but there is one more step before it can be executed. The request must go through a gauntlet of admission-control plugins. Similar to the authorizers, if a single admission controller rejects a request, it is denied.

Admission controllers are a neat concept. The idea is that there may be global cluster concerns that could be grounds for rejecting a request. Without admission controllers, all authorizers would have to be aware of these concerns and reject the request. But, with admission controllers, this logic can be performed once. In addition, an admission controller may modify the request. Admission controllers run in eaither validating mode or mutating mode. As usual, the cluster administrator decides which admission control plugins run by providing a command-line argument called _admission-control_. The value is a comma-separated and ordered list of plugins. Here is the list of recommended plugins for Kubernetes >= 1.9 (the order matters):

--admission-control=NamespaceLifecycle,LimitRanger,ServiceAccount,PersistentVolumeLabel,DefaultStorageClass,MutatingAdmissionWebhook,ValidatingAdmissionWebhook,ResourceQuota,DefaultTolerationSeconds

Let's look at some of the available plugins (more are added all the time):

- **DefaultStorageClass** : Adds a default storage class to requests for the creation of a PersistentVolumeClaim that doesn't specify a storage class
- **DefaultTolerationSeconds** : Set default toleration of pods for taints (if not set already): notready:NoExecute and notreachable:NoExecute .
- **EventRateLimit** : limit flooding of the API server with events (new in Kubernetes 1.9)
- **ExtendedResourceToleration** : combine taints on nodes with special resources like GPU and FPGA with toleration on pods that request those resources. The end result is that the node with the extra resources will be dedicated for pods with the proper toleration.
- **ImagePolicyWebhook** : This complicated plugin connects to an external backend to decide whether a request should be rejected based on the image
- **LimitPodHardAntiAffinity** : deny any pod that defines AntiAffinity topology key other than kubernetes.io/hostname in requiredDuringSchedulingRequiredDuringExecution.
- **LimitRanger** : Reject requests that violate resource limits
- **MutatingAdmissionWebhook** : Call in order registered mutating web hooks that are able to modify their target object. Note that there is no guarantee that the change will be effective due to potential changes by other mutating web hooks.
- **NamespaceAutoProvision**: Create the namespace in the request if it doesn't exist already
- **NamespaceLifecycle** : Reject object creation requests in namespaces that are in the process of being terminated or don't exist.
- **PodSecurityPolicy**: Reject request if the request security context doesn't conform to pod security policies
- **ResourceQuota** : Reject requests that violate the namespace's resource quota
- **ServiceAccount** : Automation for service accounts
- **ValidatingAdmissionWebhook** : This admission controller calls any validating webhooks which match the request. Matching webhooks are called in parallel; if any of them rejects the request, the request fails.

As you can see, the admission control plugins have very diverse functionality. They support namespace-wide policies and enforce validity of requests mostly from a resource management and security point of view. This frees the authorization plugins to focus on valid operations. The ImagePolicyWebHook is the gateway to validating images, which is a big challenge. The MutatingAdmissionWebhook and ValidatingAdmissionWebhook are the gateway to dynamic admission control where you can deploy your own admission controller without compiling it into Kubernetes. Dynamic admission control is suitable for tasks like semantic validation of resources (do all pods have the standard set of labels?).

The division of responsibility for validating an incoming request through the separate stages of authentication, authorization, and admission, each with its own plugins, makes a complicated process much more manageable to understand and use. The mutating admission controllers provide a lot of flexibility and the ability to automatically enforce certain policies without burdening the users (e.g. creating namespace automatically if it doesn't exist).  

## Securing pods

Pod security is a major concern, since Kubernetes schedules the pods and lets them run. There are several independent mechanisms for securing pods and containers. Together these mechanisms support defense in depth, where, even if an attacker (or a mistake) bypasses one mechanism, it will get blocked by another.

### Using a private image repository

This approach gives you a lot of confidence that your cluster will only pull images that you have previously vetted, and you can manage upgrades better. You can configure your $HOME/.dockercfg or $HOME/.docker/config.json on each node. But, on many cloud providers, you can't do it because nodes are provisioned automatically for you.

### ImagePullSecrets

This approach is recommended for clusters on cloud providers. The idea is that the credentials for the registry will be provided by the pod, so it doesn't matter what node it is scheduled to run on. This circumvents the problem with .dockercfg at the node level.

First, you need to create a secret object for the credentials:

```
$ kubectl create secret the-registry-secret
  --docker-server=<docker registry server>
  --docker-username=<username>
  --docker-password=<password>
  --docker-email=<email>
secret 'docker-registry-secret' created.
```

You can create secrets for multiple registries (or multiple users for the same registry) if needed. The kubelet will combine all the ImagePullSecrets.

But, since pods can access secrets only in their own namespace, you must create a secret on each namespace where you want the pod to run.

Once the secret is defined, you can add it to the pod spec and run some pods on your cluster. The pod will use the credentials from the secret to pull images from the target image registry:

```
apiVersion: v1
kind: Pod
metadata:
  name: cool-pod
  namespace: the-namespace
spec:
  containers:
    - name: cool-container
      image: cool/app:v1
  imagePullSecrets:
    - name: the-registry-secret
```

### Specifying a security context

A security context is a set of operating-system-level security settings such as UID, gid, capabilities, and SELinux role. These settings are applied at the container level as a container security content. You can specify a pod security context that will apply to all the containers in the pod. The pod security context can also apply its security settings (in particular, fsGroup and seLinuxOptions) to volumes.

Here is a sample pod security context:

```
apiVersion: v1
kind: Pod
metadata:
  name: hello-world
spec:
  containers:
    ...
  securityContext:
    fsGroup: 1234
    supplementalGroups: [5678]
    seLinuxOptions:
      level: 's0:c123,c456'
```

The container security context is applied to each container and it overrides the pod security context. It is embedded in the containers section of the pod manifest. Container context settings can't be applied to volumes, which remain at the pod level.

Here is a sample container security content:

```
apiVersion: v1
kind: Pod
metadata:
  name: hello-world
spec:
  containers:
    - name: hello-world-container
      # The container definition
      # ...
      securityContext:
        privileged: true
        seLinuxOptions:
          level: 's0:c123,c456'
```          

### Protecting your cluster with AppArmor

AppArmor is a Linux kernel security module. With AppArmor, you can restrict a process running in a container to a limited set of resources such as network access, Linux capabilities, and file permissions. You configure AppArmor though profiles.

#### Requirements

AppArmor support was added as Beta in Kubernetes 1.4. It is not available for every operating system, so you must choose a supported OS distribution in order to take advantage of it. Ubuntu and SUSE Linux support AppArmor and enable it by default. Other distributions have optional support. To check if AppArmor is enabled, type the following:

```
cat /sys/module/apparmor/parameters/enabled
Y
```


If the result is Y then it's enabled.

The profile must be loaded into the kernel. Check the following file:

```
/sys/kernel/security/apparmor/profiles
```

Also, only the Docker runtime supports AppArmor at this time.

#### Securing a pod with AppArmor

Since AppArmor is still in Beta, you specify the metadata as annotations and not as bonafide fields, when it gets out of Beta that will change.

To apply a profile to a container, add the following annotation:

container.apparmor.security.beta.kubernetes.io/<container-name>: <profile-ref>

The profile reference can be either the default profile, runtime/default, or a profile file on the host localhost/<profile-name>.

Here is a sample profile that prevents writing to files:

```
#include <tunables/global>
profile k8s-apparmor-example-deny-write flags=(attach\_disconnected) {
  #include <abstractions/base>
  file,
  # Deny all file writes.
  deny /\*\* w,
}
```

AppArmor is not a Kubernetes resource, so the format is not the YAML or JSON you're familiar with.

To verify the profile was attached correctly, check the attributes of process 1:

```
kubectl exec <pod-name> cat /proc/1/attr/current
```

Pods can be scheduled on any node in the cluster by default. This means the profile should be loaded into every node. This is a classic use case for DaemonSet.

#### Writing AppArmor profiles

Writing profiles for AppArmor by hand is not trivial. There are some tools that can help: aa-genprof and aa-logprof can generate a profile for you and assist in fine-tuning it by running your application with AppArmor in complain mode. The tools keep track of your application's activity and AppArmor warnings, and create a corresponding profile. This approach works, but it feels clunky.

My favorite tool is bane (https://github.com/jessfraz/bane), which generates AppArmor profiles from a simpler profile language based on TOML syntax. Bane profiles are very readable and easy to grasp. Here is a snippet from a bane profile:

```
Name = 'nginx-sample'
[Filesystem]
# read only paths for the container
ReadOnlyPaths = [
  '/bin/\*\*',
  '/boot/\*\*',
  '/dev/\*\*',
]
# paths where you want to log on write
LogOnWritePaths = [
  '/\*\*'
]

# allowed capabilities
[Capabilities]
Allow = [
  'chown',
  'setuid',
]
[Network]
Raw = false
Packet = false
Protocols = [
  'tcp',
  'udp',
  'icmp'
]
```

The generated AppArmor profile is pretty gnarly.

### Pod security policies

**Pod security policy** ( **PSP** ) is available as Beta since Kubernetes 1.4. It must be enabled, and you must also enable the PSP admission control to use them. A PSP is defined at the cluster-level and defines the security context for pods. There are a couple of differences between using a PSP and directly specifying a security content in the pod manifest as we did earlier:

- Apply the same policy to multiple pods or containers
- Let the administrator control pod creation so users don't create pods with inappropriate security contexts
- Dynamically generate different security context for a pod via the admission controller

PSPs really scale the concept of security contexts. Typically, you'll have a relatively small number of security policies compared to the number of pods (or rather, pod templates). This means that many pod templates and containers will have the same security policy. Without PSP, you have to manage it individually for each pod manifest.

Here is a sample PSP that allows everything:

```
kind: PodSecurityPolicy
apiVersion: extensions/v1beta1policy/v1beta1
metadata:
  name: permissive
spec:
  seLinux:
    rule: RunAsAny
  supplementalGroups:
    rule: RunAsAny
  runAsUser:
    rule: RunAsAny
  fsGroup:
    rule: RunAsAny
  volumes:
  - "\*"
```

As you can see it is much more human-readable than AppArmor and it is available on every OS and runtime.

### Authorizing Pod Security Policies via RBAC

This is the recommended way to enable the use of policies. Let's create a ClusterRole (Role works too) to grant access to use the target policies. It should look like:

```
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: <role name>
rules:
- apiGroups: ['extensionspolicy']
  resources: ['podsecuritypolicies']
  verbs:   ['use']
  resourceNames:
  - <list of policies to authorize>
```

Then, we need to bind the cluster role to the authorized users:

```
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: <binding name>
roleRef:
  kind: ClusterRole
  name: <role name>
  apiGroup: rbac.authorization.k8s.io
subjects:
 - < list of authorized service accounts:
```

Here is a specific service account:

```
- kind: ServiceAccount
  name: <authorized service account name>
  namespace: <authorized pod namespace>
```

You can also authorize specific users, but it's not recommended:

```
- kind: User
  apiGroup: rbac.authorization.k8s.io
  name: <authorized user name>
```

If using a role binding instead of cluster role binding then it will apply only to pods in the same namespace as the binding. This can be paired with system groups to grant access to all pods run in the namespace:

```
- kind: Group
  apiGroup: rbac.authorization.k8s.io
  name: system:serviceaccounts
```

Or equivalently, all authenticated users in a namespace:

```
- kind: Group
  apiGroup: rbac.authorization.k8s.io
  name: system:authenticated
```

## Managing network policies

Node, pod, and container security is imperative, but it's not enough. Network segmentation is critical to design secure Kubernetes clusters that allow multi-tenancy, as well as to minimize the impact of security breaches. Defense in depth mandates that you compartmentalize parts of the system that don't need to talk to each other, also carefully managing the direction, protocols, and ports of traffic.

Network policy allows you fine-grained control and proper network segmentation of your cluster. At the core, a network policy is a set of firewall rules applied to a set of namespaces and pods selected by labels. This is very flexible because labels can define virtual network segments and be managed as a Kubernetes resource.

This is a huge improvement over trying to segment your network using traditional approaches like IP address ranges and subnet masks where you often run out of IP addresses or allocate too much just in case.


### Choosing a supported networking solution

Some networking backends (network plugins) don't support network policies. For example, the popular Flannel can't be used to apply policies. This is critical. You will be able to define network policies even if your network plugin doesn't support them. Your policies simply will have no effect, giving you a false sense of security. 

Here is a list of network plugins that support network policies (both ingress and egress):

- Calico
- WeaveNet
- Canal
- Cillium
- Kube-Router
- Romana
- Contiv

If you run your cluster on a managed Kubernetes service then the choice has been already made for you.

We will explore the ins and out of network plugins in the "Advanced Networking" chapter. Here we focus on network policies.

### Defining a network policy

You define a network policy using a standard YAML manifest.

Here is a sample policy:

```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
 name: the-network-policy
 namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  ingress:
   - from:
     - namespaceSelector:
         matchLabels:
           project: cool-project
     - podSelector:
          matchLabels:
            role: frontend
    ports:
     - protocol: tcp
       port: 6379
```

The spec part has two important parts, the podSelector and the ingress. The podSelector governs which pods this network policy applies to. The ingress governs which namespaces and pods can access these pods and which protocols and ports they can use.

In the sample network policy, the pod selector specified the target for the network policy to be all the pods that are labeled role:db. The ingress section has a from sub-section with a namespace selector and a pod selector. All the namespaces in the cluster that are labeled project:cool-project, and within these namespaces, all the pods that are labeled role:frontend, can access the target pods labeled role:db. The ports section defines a list of pairs (protocol and port) that further restrict what protocols and ports are allowed. In this case, the protocol is tcp and the port is 6379 (Redis standard port).

Note that the network policy is cluster-wide, so pods from multiple namespaces in the cluster can access the target namespace. The current namespace is always included, so even if it doesn't have the project:cool label, pods with role:frontend can still have access.

It's important to realize that the network policy operates in a whitelist fashion. By default, all access is forbidden, and the network policy can open certain protocols and ports to certain pods that match the labels. However, the whitelist nature of the network policy applies only to pods that are selected for at least one network policy. If a pod is not selected it will allow all access. Always make sure all your pods are covered by a network policy.

Another implication of the whitelist nature is that, if multiple network policies exist, the union of all the rules apply. If one policy gives access to port 1234 and another gives access to port 5678 for the same set of pods, then a pod may be accessed through either 1234 or 5678.

To use network policies responsibly consider starting with a deny-all network policy:

```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Then, start adding network policies to allow ingress to specific pods explicitly. Note, that you must apply the deny-all policy for each namespace:  

```
$ kubectl -n <namespace> create -f deny-all-network-policy.yaml
```

### Limiting Egress to External Networks

Kubernetes 1.8 added egress network policy support, so you can control outbound traffic too.  Here is an example that prevents accessing external IP 1.2.3.4. The order: 999 ensures the policy is applied before other policies.

```
apiVersion: v1
kind: policy
metadata:
  name: default-deny-egress
spec:
  order: 999
  egress:
  - action: deny
    destination:
      net: 1.2.3.4
    source: {}
```

### Cross-Namespace Policies

If you divide your cluster into multiple namespaces it can come in handy sometimes if pods can communicate across namespaces. You can specify the `ingress.namespaceSelector` field in your network policy to enable access from multiple namespaces. For example, if you have a production and staging namespaces and you periodically populate your staging environments with snapshots of your production data.

## Using secrets

Secrets are paramount in secure systems. They can be credentials such as username and password, access tokens, API keys, certificates or crypto keys. Secrets are typically small. If you have large amounts of data you want to protect, you should encrypt it and keep the encryption/decryption keys as secrets.

### Storing secrets in Kubernetes

Kubernetes used to store secrets in etcd as plaintext by default. This means that direct access to etcd should be limited and carefully guarded. Starting with Kubernetes 1.7 you can now encrypt your secrets at rest (when they're stored by etcd).

Secrets are managed at the namespace level. Pods can mount secrets either as files via secret volumes or as environment variables. From a security standpoint, this means that any user or service that can create a pod in a namespace can have access to any secret managed for that namespace. If you want to limit access to a secret, put it in a namespace accessible to a limited set of users or services.

When a secret is mounted into a container it is never written to disk. It is stored in tmpfs. When the kubelet communicates with the API server it is uses TLS normally, so the secret is protected in transit.

### Configuring Encryption at Rest

You need to pass this argument when you start the API server:

 --encryption-provider-config <encryption config file>

Here is a sample encryption config:

```
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - identity: {}
    - aesgcm:
        keys:
        - name: key1
          secret: c2VjcmV0IGlzIHNlY3VyZQ==
        - name: key2
          secret: dGhpcyBpcyBwYXNzd29yZA==
    - aescbc:
        keys:
        - name: key1
          secret: c2VjcmV0IGlzIHNlY3VyZQ==
        - name: key2
          secret: dGhpcyBpcyBwYXNzd29yZA==
    - secretbox:
        keys:
        - name: key1
          secret: YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY=
```

### Creating secrets

Secrets must be created before you try to create a pod that requires them. The secret must exist; otherwise the pod creation will fail.

You can create secrets with the following command: `kubectl create secret`

Here I create a generic secret called hush-hash, which contains two keys, username and password:

```
$ kubectl create secret generic hush-hush --from-literal=username=tobias --from-literal=password=cutoffs
secret/hush-hush created
```

The resulting secret is opaque:

```
$ kubectl describe secrets/hush-hush
Name:         hush-hush
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
password:  7 bytes
username:  6 bytes
```

You can create secrets from files using --from-file instead of --from-literal, and you can also create secrets manually if you encode the secret value as base64.

Key names inside a secret must follow the rules for DNS sub-domains (without the leading dot).

### Decoding secrets

To get the content of a secret you can use `kubectl get secret`:

```
$ kubectl get secrets/hush-hush -o yaml
apiVersion: v1
data:
  password: Y3V0b2Zmcw==
  username: dG9iaWFz
kind: Secret
metadata:
  creationTimestamp: "2019-08-25T06:57:07Z"
  name: hush-hush
  namespace: default
  resourceVersion: "56655"
  selfLink: /api/v1/namespaces/default/secrets/hush-hush
  uid: 8d50c767-c705-11e9-ae89-0242ac120002
type: Opaque
```

The values are base64-encoded. You need to decode them yourself:
```
$ echo 'Y3V0b2Zmcw==' | base64 --decode
cutoffs
```

### Using secrets in a container

Containers can access secrets as files by mounting volumes from the pod. Another approach is to access the secrets as environment variables. Finally, a container (given its service account has the permission) can access the Kubernetes API directly or use `kubectl get secret`.

To use a secret mounted as a volume, the pod manifest should declare the volume and it should be mounted in the container's spec:

```
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-secret
spec:
  containers:
  - name: container-with-secret
    image: g1g1/py-kube:0.2
    command: ["/bin/bash", "-c", "while true ; do sleep 10 ; done"]
    volumeMounts:
    - name: secret-volume
      mountPath: "/mnt/hush-hush"
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: hush-hush
```   
      
The volume name (secret-volume) binds the pod volume to the mount in the container. Multiple containers can mount the same volume. When this pod is running, the username and password are available as files under /etc/hush-hush:

```
$ kubectl exec pod-with-secret cat /mnt/hush-hush/username
tobias

$ kubectl exec pod-with-secret cat /mnt/hush-hush/password
cutoffs
```

# Running a multi-user cluster

In this section, we will look briefly at the option to use a single cluster to host systems for multiple users or multiple user communities (AKA multi-tenancy). The idea is that those users are totally isolated and may not even be aware that they share the cluster with other users. Each user community will have its own resources, and there will be no communication between them (except maybe through public endpoints). The Kubernetes namespace concept is the ultimate expression of this idea.

## The case for a multi-user cluster

Why should you run a single cluster for multiple isolated users or deployments? Isn't it simpler to just have a dedicated cluster for each user? There are two main reasons: cost and operational complexity. If you have many relatively small deployments and you want to create a dedicated cluster to each one, then you'll have a separate master node and possibly a three-node etcd cluster for each one. That can add up. Operational complexity is very important too. Managing tens or hundreds or thousands of independent clusters is no picnic. Every upgrade and every patch needs to be applied to each cluster. Operations might fail and you'll have to manage a fleet of clusters where some of them are in slightly different state than the others. Meta-operations across all clusters may be more difficult. You'll have to aggregate and write your tools to perform operations and collect data from all clusters.

Let's look at some use cases and requirements for multiple isolated communities or deployments:

- A platform or service provider for <Blank>-as-a-service
- Managing separate testing, staging, and production environments
- Delegating responsibility to community/deployment admins
- Enforcing resource quotas and limits on each community
- Users see only resources in their community

## Using namespaces for safe multi-tenancy

Kubernetes namespaces are the perfect answer to safe multi-tenant clusters. This is not a surprise as this was one of the design goals of namespaces.

You can easily create namespaces in addition to the built-in kube-system and default. Here is a YAML file that will create a new namespace called custom-namespace. All it has is a metadata item called name. It doesn't get any simpler:

```
apiVersion: v1
kind: Namespace
metadata:
  name: custom-namespace
```

Let's create the namespace:

```
$ kubectl create -f custom-namespace.yaml
namespace/custom-namespace created

$ kubectl get namespaces
NAME               STATUS   AGE
custom-namespace   Active   36s
default            Active   26h
kube-node-lease    Active   26h
kube-public        Active   26h
kube-system        Active   26h
```

We can see the default namespace, our new custom-namespace and a few system namespaces prefized with "kube-"

The status field can be Active or Terminating. When you delete a namespace, it will get into the Terminating state. When the namespace is in this state you will not be able to create new resources in this namespace. This simplifies the clean-up of namespace resources and ensures the namespace is really deleted. Without it, the replication controllers might create new pods when existing pods are deleted.

To work with a namespace, you add the --namespace (or -n for short) argument to kubectl commands. Here is how to run a pod in interactive mode in the custom-namespace namespace:  

```
$ kubectl run trouble -it -n custom-namespace --image=g1g1/py-kube:0.2 --generator=run-pod/v1 bash
If you don't see a command prompt, try pressing enter.
root@trouble:/#
```

Listing pods in the custom-namespace returns only the pod we just launched:

```
$ kubectl get pods --namespace=custom-namespace
NAME      READY   STATUS    RESTARTS   AGE
trouble   1/1     Running   0          113s
```

Listing pods without the namespace returns the pods in the default namespace:

```
$ kubectl get pods
NAME              READY   STATUS    RESTARTS   AGE
pod-with-secret   1/1     Running   0          11h
```

## Avoiding namespace pitfalls

Namespaces are great, but they can add some friction. When you use just the default namespace, you can simply omit the namespace. When using multiple namespaces, you must qualify everything with the namespace. This can add some burden, but doesn't present any danger. However, if some users (for example, cluster administrators) can access multiple namespaces, then you're open to accidentally modifying or querying the wrong namespace. The best way to avoid this situation is to hermetically seal the namespace and require different users and credentials for each namespace. Just like you should use a user account for most operations on your machine or remote machines and use root via sudo only when you have too. 

In addition, you should use tools that help make it clear what namespace you're operating on (for example, shell prompt if working from command-line or listing the namespace prominently in a web interface). One of the most popular tools is kubens (available along with kubectx): https://github.com/ahmetb/kubectx

Make sure that users that can operate on a dedicated namespace don't have access to the default namespace. Otherwise, every time they forget to specify a namespace, they'll operate quietly on the default namespace.


# Summary

In this chapter, we covered the many security challenges facing developers and administrators building systems and deploying applications on Kubernetes clusters. But we also explored the many security features and the flexible plugin-based security model that provides many ways to limit, control, and manage containers, pods, and nodes. Kubernetes already provides versatile solutions to most security challenges, and it will only get better as capabilities such as AppArmor and various plugins move from Alpha/Beta status to general availability. Finally, we considered how to use namespaces to support multiple user communities or deployments in the same Kubernetes cluster.

In the next chapter, we will look in detail into many Kubernetes resources and concepts, and how to use them and combine them effectively. The Kubernetes object model is built on top of a solid foundation of a small number of generic concepts such as resources, manifests, and metadata. This empowers an extensible, yet surprisingly consistent, object model to expose a very diverse set of capabilities for developers and administrators.

# Reference

https://www.stackrox.com/post/2019/04/setting-up-kubernetes-network-policies-a-detailed-guide/
https://github.com/ahmetb/kubernetes-network-policy-recipes
https://jeremievallee.com/2018/05/28/kubernetes-rbac-namespace-user.html
