# Hub23 Documentation

This branch hosts documentation around deploying, maintaining and customising the Hub23 BinderHub instance.

They are built with jekyll and hosted at by GitHub pages at <https://alan-turing-institute.github.io/hub23-deploy/>

## Recommended Reading Order

1. Creating an Azure Key Vault for Hub23

2. Methods of deploying a Kubernetes Cluster

   1. Deploy a standard Kubernetes cluster

   2. Deploy an Autoscaling Kubernetes Cluster

   3. Deploy a Kubernetes Cluster with Multiple Nodepools

3. Setup Helm

4. Enabling HTTPS with `cert-manager`

5. Methods of Installing BinderHub

    1. Installing BinderHub

    2. Installing BinderHub with a Local Helm Chart

6. Creating an Azure Container Registry and connecting to the Kubernetes Cluster

7. Customising the JupyterHub

8. Enabling Authentication

9. Changing the logo on the Binder page

10. Enabling Page Redirection

11. Optimizing the JupyterHub for Autoscaling

## Locally Buidling the Documentation

Install [Ruby](https://www.ruby-lang.org/en/documentation/installation/) and [Bundler](https://bundler.io/).

```bash
git clone https://github.com/alan-turing-institute/hub23-deploy.git
git checkout gh-pages
bundle install
bundle exec jekyll serve --livereload
```
