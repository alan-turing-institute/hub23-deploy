# :wheel_of_dharma: :chart_with_upwards_trend: hub23-chart

See the [developing helm chart docs](https://helm.sh/docs/developing_charts/) for more info on the contents of this folder.

## Links for Chart Dependencies

- **BinderHub repository:** <https://github.com/jupyterhub/binderhub>
- **BinderHub Helm chart:** <https://jupyterhub.github.io/helm-chart/>
- **`ingress-nginx` Helm chart:** <https://github.com/kubernetes/ingress-nginx>

## :rocket: Installing the Chart

To install the chart:

```bash
cd hub23-chart && helm dependency update && cd ..
helm install hub23-chart --name=hub23 --namespace=hub23 -f deploy/prod.yaml -f .secret/prod.yaml
```

## :package: Packaging the Chart

To package the chart:

```bash
helm package hub23-chart
```
