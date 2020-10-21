(content:cert-manager:context)=
# Context

To setup secure HTTPS communication, we need to have a _certificate_ associated with our _domain_ from a _Certificate Authority_ (CA).
Thankfully, there's [Let's Encrypt](https://letsencrypt.org/) which is a widely trusted CA that is also free to request certificates from.

But CA's don't just give away certificates.
They require proof of domain ownership through a _challenge_.
This is technically cumbersone and often automated by services like [`cert-manager`](https://github.com/jetstack/cert-manager).

```{note}
_HTTPS_ is the secured version of HTTP: HyperText Transfer Protocol.
HTTP is the protocol used by browsers and web servers to communicate and exchange information.
When that exchange of data is encrypted with SSL/_TLS_, then we call it _HTTPS_.
The S stands for Secure.
```

TLS termination, the transition from encrypted to unencrypted traffic, can be done in various locations.
A common place in the world of Kubernetes is to let this be managed by ingress controllers.
An ingress controller is something that acts to make Kubernetes ingress resources come to life.
It is possible to use an ingress controller made available by your cloud provider or one that you have hosted yourself within the cluster, such as [`nginx-ingress`](https://github.com/helm/charts/tree/master/stable/nginx-ingress).

Below is a guide on how to use `cert-manager` along with `nginx-ingress` to enable HTTPS.
Both of these can be installed as Helm Charts.

## How `cert-manager` works

`cert-manager` looks at [Kubernetes ingress resources](https://kubernetes.io/docs/concepts/services-networking/ingress/).
For each ingress resource it finds, it further looks for annotations attached this resource.
If the ingress resource has an annotation that indicates `cert-manager` needs to take action, then it will try to provide a certificate from Let's Encrypt.

An example of an annotation indicating the resource requires a certificate and `cert-manager` should request one looks as follows:

```yaml
kubernetes.io/tls-acme: "true"
```

If it decides action is required, `cert-manager` will further look at the ingress object.
What hosts or domains does it want to handle traffic to?
From what Kubernetes secret resource does it want to read the certificate from?
It will combine this information with any default settings such as what _Issuer_ to use.

An _Issuer_ is a `cert-manager` concept.
It describes what CA to speak with, what email to use as a contact person, and what kind of challenge to use.
This can be configured in `cert-manager`'s helm chart values like so:

```yaml
# Example configuration of cert-manager default values
# for requesting certificates
cert-manager:
  ingressShim:
    defaultIssuerName: "a-manually-created-issuer-resource"
    defaultIssuerKind: "Issuer"
    defaultACMEChallengeType: "http01"
```
