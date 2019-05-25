# Changing the logo on the Binder page

See these docs:
* https://binderhub.readthedocs.io/en/latest/customizing.html#template-customization

The html content must be publicly hosted so these changes must happen in the [alan-turing-institute/hub23-custom-files](https://github.com/alan-turing-institute/hub23-custom-files) repo.

#### 1. Add the logo image file to the `static` folder

This can be any valid image file.

#### 2. Extend `templates/page.html`

In `templates/page.html`, change the name of the image to match that of your chosen file.

The line should look as follows.

```
<img id="logo" src={% block logo_image %}"/extra_static/<image-name>"{% endblock logo_image %} width="390px" />
```

####3. Update `config.yaml`

Add the following to `.secret/config.yaml`.

```
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
      - --branch=master
      - --depth=1
      - --
      - https://github.com/alan-turing-institute/hub23-custom-files
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

**NOTE:** If you are testing the logo on a branch of this repo, you will need to update the `--branch` argument to match.

#### 4. Upgrade the BinderHub deployment and visit the Binder page!

Upgrade the Chart with the following command.
The most recent commit-hash used should be logged in the Changelog section of the root README.

```
helm upgrade hub23 jupyterhub/binderhub --version=0.2.0-<commit-hash> -f .secret/secret.yaml -f .secret/config.yaml
```

Get the IP address of the Binder page with the following command.

```
kubectl --namespace hub23 get svc binder
```
