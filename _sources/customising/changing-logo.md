(content:customising:logo)=
# Changing the logo on the Binder page

The html content must be publicly hosted so the repo must remain public.
Also, to reduce the size of the container when it is cloned, the `static` and `templates` directories are hosted on the separate branch [`html-templates`](https://github.com/alan-turing-institute/hub23-deploy/tree/html-templates).

## Add the logo image file to the `static` folder

This can be any valid image file.

```{warning}
Remember to checkout the `html-templates` branch first!
```

## Extend `templates/page.html`

In `templates/page.html`, change the name of the image to match that of your chosen file.

The line should look as follows.

<script src="https://gist.github.com/sgibson91/c2201608c3d1ecb40a891a8b921c3a9b.js"></script>

```{warning}
Remember to checkout the `html-templates` branch first!
```

## Update `deploy/config.yaml` or `deploy/prod.yaml`

```{warning}
This change should be made to the `main` branch!
```

Add the following to your config file.

```yaml
config:
  BinderHub:
    template_path: /etc/binderhub/custom/templates
    extra_static_path: /etc/binderhub/custom/static
    extra_static_url_prefix: /extra_static/
    template_variables:
        EXTRA_STATIC_URL_PREFIX: "/extra_static/"

initContainers:
  - name: git-clone-templates
    image: alpine/git
    args:
      - clone
      - --single-branch
      - --branch=html-templates
      - --depth=1
      - --
      - https://github.com/alan-turing-institute/hub23-deploy
      - /etc/binderhub/custom
    securityContext:
      runAsUser: 0
    volumeMounts:
      - name: custom-templates
        mountPath: /etc/binderhub/custom
extraVolumes:
  - name: custom-templates
    emptyDir: {}
extraVolumeMounts:
  - name: custom-templates
    mountPath: /etc/binderhub/custom
```

## Upgrade the BinderHub deployment and visit the Binder page!

Upgrade the chart and visit the Binder page to see your updated homepage!
