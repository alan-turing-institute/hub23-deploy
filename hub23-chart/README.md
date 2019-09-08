# hub23-chart

See the [developing helm chart docs](https://helm.sh/docs/developing_charts/) for more info on the contents of this folder.

## Links for Chart Dependencies

* https://github.com/jupyterhub/binderhub
* https://jupyterhub.github.io/helm-chart/
* https://github.com/helm/charts/tree/master/stable/nginx-ingress
* https://github.com/helm/charts/tree/master/stable/cert-manager

## Installing the Chart

To install the chart:
```
cd hub23-chart && helm dependency update && cd ..
helm install ./hub23-chart --name=hub23 --namespace=hub23 -f deploy/prod.yaml -f .secret/prod.yaml
```

## Packaging the Chart

To package the chart:
```
helm package hub23-chart
```
