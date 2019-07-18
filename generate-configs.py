import os
import json
import subprocess

SUBSCRIPTION = "Turing-BinderHub"
RESOURCE_GROUP = "Hub23"
VAULT_NAME = "hub23-keyvault"
CLUSTER_NAME = "hub23cluster"
REGISTRY_NAME = "hub23registry"
IMAGE_PREFIX = "hub23/binder-dev"
ORG_NAME = "binderhub-test-org"
HUB_NAME = "hub23"
JUPYTERHUB_IP = "hub.hub23.turing.ac.uk"
BINDER_IP = "binder.hub23.turing.ac.uk"

secret_names = [
    "apiToken",
    "secretToken",
    "binderhub-access-token",
    "github-client-id",
    "github-client-secret",
    "SP-appID",
    "SP-key"
]

secrets = {}

# Get secrets
for secret in secret_names:
    # Get secret information and convert to json
    json_out = subprocess.check_output([
        "az", "keyvault", "secret", "show", "-n", secret,
        "--vault-name", VAULT_NAME
    ]).decode()
    secret_info = json.loads(json_out)

    # Save secret to dictionary
    secrets[secret] = secret_info["value"]

config_template = f"""config:
  BinderHub:
    template_path: /etc/binderhub/custom/templates
    extra_static_path: /etc/binderhub/custom/static
    extra_static_url_prefix: /extra_static/
    template_variables:
      EXTRA_STATIC_URL_PREFIX: "/extra_static/"
    use_registry: true
    image_prefix: {REGISTRY_NAME}/{IMAGE_PREFIX}-
    auth_enabled: true
    hub_url: https://{JUPYTERHUB_IP}
  DockerRegistry:
    token_url: "https://{REGISTRY_NAME}.azurecr.io/oauth2/token?service={REGISTRY_NAME}.azurecr.io"

jupyterhub:
  cull:
    every: 660
    timeout: 600
    maxAge: 21600
  hub:
    services:
      binder:
        oauth_redirect_uri: "http://{BINDER_IP}/oauth_callback"
        oauth_client_id: "binder-oath-client-test"
    extraConfig:
      hub_extra: |
        c.JupyterHub.redirect_to_server = False
      binder: |
        from kubespawner import Kubespawner

        class BinderSpawner(KubeSpawner):
          def start(self):
            if 'image' in self.user_options:
              self.image = self.user_options['image']
            return super().start()
        c.JupyterHub.spawner_class = BinderSpawner
  singleuser:
    cmd: jupyterhub-singleuser
    memory:
      limit: 1G
      guarantee: 1G
    cpu:
      limit: .5
      guarantee: .5
  prePuller:
    continuous:
      enabled: true
  scheduling:
    podPriority:
      enabled: true
    userPlaceholder:
      replicas: 3
    userScheduler:
      enabled: true
  auth:
    type: github
    admin:
      access: true
      users:
        - sgibson91
    github:
      clientId: "{secrets['github-client-id']}"
      clientSecret: "{secrets['github-client-secret']}"
      callbackUrl: "https://{JUPYTERHUB_IP}/hub/oauth_callback"
      orgWhitelist:
        - "{ORG_NAME}"
    scopes:
      - "read:user"
""" + """
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
"""

secret_template = f"""jupyterhub:
  hub:
    services:
      binder:
        apiToken: "{secrets['apiToken']}"
  proxy:
    secretToken: "{secrets['secretToken']}"
registry:
  url: https://{REGISTRY_NAME}.azurecr.io
  username: {secrets['SP-appID']}
  password: {secrets['SP-key']}
config:
  GitHubRepoProvider:
    access_token: {secrets['binderhub-access-token']}
"""

# Make a secrets folder
if not os.path.exists(".secret"):
    os.mkdir(".secret")

# Write the config files
with open(os.path.join(".secret", "config.yaml"), "w") as f:
    f.write(config_template)

with open(os.path.join(".secret", "secret.yaml"), "w") as f:
    f.write(secret_template)

print("Your BinderHub files have been configured:")
for bhub_file in os.listdir(".secret"):
    print(bhub_file)
