# Enabling Authentication

See the following docs:
* https://binderhub.readthedocs.io/en/latest/authentication.html
* https://zero-to-jupyterhub.readthedocs.io/en/stable/authentication.html

## Enabling Authentication using JupyterHub as an OAuth provider

#### Update `config.yaml` with the following config

* Also modify `config-template.yaml` and `make-config-files.sh`

```
config:
  BinderHub:
    auth_enabled: true

jupyterhub:
  cull:
    # don't cull authenticated users
    users: False

  hub:
    services:
      binder:
        oauth_redirect_uri: "http://<binder-ip>/oauth_callback"
        oauth_client_id: "binder-oauth-client-test"
    extraConfig:
      hub_extra: |
        c.JupyterHub.redirect_to_server = False

      binder: |
        from kubespawner import KubeSpawner

        class BinderSpawner(KubeSpawner):
          def start(self):
              if 'image' in self.user_options:
                # binder service sets the image spec via user options
                self.image = self.user_options['image']
              return super().start()
        c.JupyterHub.spawner_class = BinderSpawner

  singleuser:
    # to make notebook servers aware of hub
    cmd: jupyterhub-singleuser

  auth: {}
```

This will set up the redirection to the JupyterHub for login and spin up user servers.

## OAuth with GitHub

#### Modify the `auth:` section of `config.yaml` to include the following

* Also modify `config-template.yaml` and `make-config-files.sh`

```
auth:
  type: github
  github:
    clientId: "<your-github-client-id>"
    clientSecret: "<another-long-secret-string>"
    callbackUrl: "http://<jupyter-ip>/hub/oauth_callback"
```

Don't worry about `clientId` and `clientSecret` yet as we will generate these on GitHub.

#### Create an OAuth app on GitHub

Go to the `binderhub-test-org` organisation on `github.com`.
Under Settings -> Developer Settings -> OAuth Apps, click New OAuth App.
Fill in the form as per the image below and click Register Application:

<html><img src="figures/github_oauth_setup.png" alt="github_oauth_setup" height=567 width=561></html>

This will create an OAuth app owned by `binderhub-test-org` that will allow anyone with a valid GitHub account to login to Hub23.

The `clientId` and `clientSecret` values will be generated.
Add these to `config.yaml`.
Also add these values to the key vault (see `azure-keyvault.md`) and update `make-config-files.sh` to pull these from the keyvault and populate `config-template.yaml`.

#### Giving access to GitHub organisations

:construction: :construction: This section of the docs is a work in progress and needs improvement :construction: :construction:

Update `config.yaml` to include the following under `auth`:

```
auth:
  type: github
  github:
    # ...
    orgWhitelist:
      - "binderhub-test-org"
  scopes:
    - "read:user"
```

* Also update `config-template.yaml`

The `read:user` scope will read a user's organisation/team memberships and look for `binderhub-test-org`.
If the membership is not found, they will be forbidden from accessing Hub23.
**This scope requires a user's membership of `binderhub-test-org` to be public.**
