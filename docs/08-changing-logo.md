# Changing the logo on the Binder page

See these docs:

- https://binderhub.readthedocs.io/en/latest/customizing.html#template-customization

The html content must be publicly hosted so the repo must remain public.

---

#### 1. Add the logo image file to the `static` folder

This can be any valid image file.

#### 2. Extend `templates/page.html`

In `templates/page.html`, change the name of the image to match that of your chosen file.

The line should look as follows.

```html
<pre>
  <code>
    <img id="logo" src={% block logo_image %}"/extra_static/IMAGE_NAME"{% endblock logo_image %} width="390px" />
  </code>
</pre>
```

#### 3. Update `deploy/config.yaml`

Add the following to `deploy/config.yaml`.

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
      - --branch=master
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

**NOTE:** If you are testing the logo on a branch of this repo, you will need to update the `--branch` argument to match.

#### 4. Upgrade the BinderHub deployment and visit the Binder page!

Upgrade the Chart with the following command.
The most recent commit-hash used should be logged in the Changelog section of the root README.

```bash
helm upgrade hub23 jupyterhub/binderhub \
    --version=0.2.0-<commit=hash> \
    -f .secret/secret.yaml \
    -f deploy/config.yaml
```

Get the IP address of the Binder page with the following command.

```bash
kubectl get svc binder --namespace hub23
```
