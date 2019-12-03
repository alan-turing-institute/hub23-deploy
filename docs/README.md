# Hub23 Documentation

This folder contains documentation around deploying, maintaining and customising the Hub23 BinderHub instance.

They are built with jekyll and hosted at by GitHub pages at <https://alan-turing-institute.github.io/hub23-deploy/>

## Recommended Reading Order

1. [Creating an Azure Key Vault for Hub23](./01-azure-keyvault.md)

2. Methods of deploying a Kubernetes Cluster

   1. [Deploy a standard Kubernetes cluster](./02i-deploy-standard-k8s-cluster.md)

   2. [Deploy an Autoscaling Kubernetes Cluster](./02ii-deploy-autoscaling-k8s-cluster.md)

   3. [Deploy a Kubernetes Cluster with Multiple Nodepools](./02iii-deploy-k8s-cluster-multiple-nodepools.md)

3. [Setup Helm](03-setup-helm.md)

4. Methods of Installing BinderHub

    1. [Installing BinderHub](./04i-installing-binderhub.md)

    2. [Installing BinderHub with a Local Helm Chart](./04ii-installing-binderhub-local-helm-chart.md)

5. [Creating an Azure Container Registry and connecting to the Kubernetes Cluster](./05-create-azure-container-registry.md)

6. [Customising the JupyterHub](./06-customise-jupyterhub.md)

7. [Enabling Authentication](./07-enabling-authentication.md)

8. [Changing the logo on the Binder page](./08-changing-logo.md)

9. [Enabling Page Redirection](./09-enabling-page-redirection.md)

10. [Optimizing the JupyterHub for Autoscaling](./10-optimising-autoscaling.md)

11. [Enabling HTTPS](./11-enabling-https.md)

## Locally Buidling the Documentation

Install [Ruby](https://www.ruby-lang.org/en/documentation/installation/) and [Bundler](https://bundler.io/).

```bash
git clone https://github.com/alan-turing-institute/hub23-deploy.git
cd hub23-deploy/docs
bundle install
bundle exec jekyll serve --livereload
```
