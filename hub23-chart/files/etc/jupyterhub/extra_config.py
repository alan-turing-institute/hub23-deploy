"""
Custom KubeSpawner and JupyterHub handlers for persistent BinderHub deployment
"""
import json
from os.path import join
from tornado import web
from tornado.escape import json_decode
from kubespawner import KubeSpawner
from jupyterhub.utils import admin_only
from jupyterhub.apihandlers.base import APIHandler
from jupyterhub.apihandlers.users import admin_or_self


class PersistentBinderSpawner(KubeSpawner):
    default_project = [
        "https://github.com/gesiscss/data_science_image",
        "gesiscss/singleuser-orc:r2d-dd93b3e",
        "master",
    ]

    def strip_repo_url(self, repo_url):
        p = "http://"
        if repo_url.startswith(p):
            repo_url = repo_url[len(p) :]
        p = "https://"
        if repo_url.startswith(p):
            repo_url = repo_url[len(p) :]
        p = ".git"
        if repo_url.endswith(p):
            repo_url = repo_url[: -len(p)]
        return repo_url.rstrip("/")

    def url_to_dir(self, url):
        url = self.strip_repo_url(url)
        return "_".join(reversed(url.split("/")[-2:]))

    def start(self):
        # Clean attributes, so we don't save wrong values in state when error happens
        for attr in ("repo_url", "ref", "image"):
            self.__dict__.pop(attr, None)

        # Get image spec from user_options
        if (
            "image" in self.user_options
            and "repo_url" in self.user_options
            and "token" in self.user_options
        ):
            # Binder service sets the image spec via user options
            # NOTE: user can pass any options through API (without using Binder) too
            self.image = self.user_options["image"]
            self.ref = self.image.split(":")[-1]
            self.repo_url = self.user_options[
                "repo_url"
            ]  # repo_url is generated in BHub by RepoProviders
        else:
            # Get saved projects
            projects = self.get_state_field("projects")
            if projects:
                # User starts server without Binder form (default)
                # For example via spawn url or by refreshing user page when server was stopped
                # Launch last repo in projects
                self.repo_url, self.image, self.ref, _ = projects[-1]
            else:
                # If user has no projects (e.g. user makes first login, deletes default project
                # and uses spawn url), start default repo
                self.repo_url, self.image, self.ref = self.default_project

        # Perpare initContainer
        # NOTE: First initContainer runs and when it is done, then notebook container runs
        # https://kubernetes.io/docs/concepts/workloads/pods/init-containers/
        # https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod/initialization/#create-a-pod-that-has-an-init-container
        # https://github.com/jupyterhub/kubespawner/blob/v0.8.1/kubespawner/spawner.py#L638-L664
        mount_path = "/projects/"
        # First it deletes projects on disk (if there are any to delete)
        # # Get list of projects to delete from disk before spawn in initContainer
        deleted_projects = self.get_state_field("deleted_projects")
        delete_cmd = (
            f"rm -rf {' '.join([join(mount_path, self.url_to_dir(d)) for d in deleted_projects])}"
            if deleted_projects
            else ""
        )
        # Then copies image's home folder (repo content after r2d process)
        # into project's dir on disk (if project_path doesn't exist on persistent disk)
        project_dir = self.url_to_dir(self.repo_url)
        project_path = join(mount_path, project_dir)
        copy_cmd = (
            f"if [ -d {project_path} ]; "
            f"then echo 'directory {project_path} exists'; "
            f"elif [ -L {project_path} ]; "
            f"then echo '{project_path} is a symlink'; "
            f"else mkdir {project_path} && cp -a ~/. {project_path}; fi"
        )
        init_container_cmds = (
            [delete_cmd, copy_cmd] if delete_cmd else [copy_cmd]
        )
        projects_volume_mount = {
            "name": self.volumes[0]["name"],
            "mountPath": mount_path,
        }
        self.init_containers = [
            {
                "name": "project-manager",
                "image": self.image,
                "command": ["/bin/sh", "-c", " && ".join(init_container_cmds)],
                # Volumes is already defined for notebook container (self.volumes)
                "volume_mounts": [projects_volume_mount],
            }
        ]

        # Notebook container (user server)
        # Mount all projects (complete user disk) to /projects
        # https://kubernetes.io/docs/concepts/storage/volumes/#using-subpath
        self.volume_mounts.append(projects_volume_mount)
        # mountPath is /home/jovyan, this is set in z2jh helm chart values.yaml
        # mount_path is "~/"
        # mount_path = "$(HOME)"
        # self.volume_mounts[0]['mountPath'] = mount_path
        # Mount only project_path to home
        self.volume_mounts[0]["subPath"] = project_dir

        self.reset_deleted_projects = True
        return super().start()

    def get_state_field(self, name):
        """Returns just current value of a field in state, doesn't update anything in state"""
        self.update_projects = False
        reset_deleted_projects = getattr(self, "reset_deleted_projects", False)
        self.reset_deleted_projects = False
        state = self.get_state()
        self.update_projects = True
        self.reset_deleted_projects = reset_deleted_projects
        return state[name]

    def get_state(self):
        """Use this method to update projects, because this method is called both in
        start and stop of the server (see JupyterHub.User's `start` and `stop` methods),
        db.commit is called after these methods.
        """
        # default_projects is only to use when first login
        default_projects = [self.default_project + ["never"]]
        _state = self.orm_spawner.state
        projects = _state.get("projects", []) if _state else default_projects
        deleted_projects = _state.get("deleted_projects", []) if _state else []

        state = super().get_state()
        state["projects"] = projects
        state["deleted_projects"] = deleted_projects

        if (
            getattr(self, "update_projects", True) is True
            and hasattr(self, "repo_url")
            and hasattr(self, "image")
            and hasattr(self, "ref")
        ):
            # Project is started or already running or is stopped,
            # so move project to the end and update the last launched time (last seen)
            from datetime import datetime

            e = [
                self.repo_url,
                self.image,
                self.ref,
                datetime.utcnow().isoformat() + "Z",
            ]
            new_projects = []
            for p in projects:
                if p[0] != e[0]:
                    new_projects.append(p)
            new_projects.append(e)
            state["projects"] = new_projects

        if getattr(self, "reset_deleted_projects", False) is True:
            state["deleted_projects"] = []

        return state

    def get_env(self):
        env = super().get_env()
        if "repo_url" in self.user_options:
            env["BINDER_REPO_URL"] = self.user_options["repo_url"]
        for key in (
            "binder_ref_url",
            "binder_launch_host",
            "binder_persistent_request",
            "binder_request",
        ):
            if key in self.user_options:
                env[key.upper()] = self.user_options[key]
        return env


class ProjectAPIHandler(APIHandler):
    @admin_only
    async def get(self, name):
        # Get user's projects
        user = self.find_user(name)
        if not user:
            raise web.HTTPError(404)
        projects = {"projects": user.spawner.get_state_field("projects")}
        self.write(json.dumps(projects))

    @admin_or_self
    async def delete(self, name):
        # Delete a project of user
        user = self.find_user(name)
        response = {}
        if user.running:
            response[
                "error"
            ] = "Project deletion is not allowed while user server is running."
        else:
            body = json_decode(self.request.body)
            if "repo_url" in body and "name" in body and "id" in body:
                repo_url = body["repo_url"]
                delete_on_disk = body.get("delete_on_disk", False)
                projects = user.spawner.get_state_field("projects")
                new_projects = []
                deleted_projects = user.spawner.get_state_field(
                    "deleted_projects"
                )
                found = False
                for project in projects:
                    if repo_url != project[0]:
                        new_projects.append(project)
                    else:
                        found = True
                        if (
                            delete_on_disk is True
                            and repo_url not in deleted_projects
                        ):
                            deleted_projects.append(repo_url)
                if found is True:
                    # NOTE: This way we ensure that this JSONDict field (state) is updated with db.commit()
                    state = user.spawner.get_state()
                    state["projects"] = new_projects
                    state["deleted_projects"] = deleted_projects
                    user.spawner.orm_spawner.state = state
                    self.db.commit()

                    response["success"] = f"Project {body['name']} is deleted."
                    response["id"] = body["id"]
                else:
                    response[
                        "error"
                    ] = f"Project {body['name']} ({body['repo_url']}) doesn't exist."
            else:
                response["error"] = "Bad request."
        self.write(json.dumps(response))
