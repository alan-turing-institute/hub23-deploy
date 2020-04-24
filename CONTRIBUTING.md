# Contributing Guidelines

:space_invader: :tada: Thank you for contributing to the Hub23-deploy repository! :tada: :space_invader:

The following is a set of guidelines for contributing to Hub23, the Alan Turing Institute's private BinderHub instance.
These are mostly guidelines, not rules.
Use your best judgement and feel free to propose changes to this document in a Pull Request.

**Table of Contents:**

- [:purple_heart: Code of Conduct](#purple_heart-code-of-conduct)
- [:question: What do I need to know?](#question-what-do-i-need-to-know)
  - [:zap: Hub23](#zap-hub23)
  - [:wheel_of_dharma: Kubernetes and Helm](#wheel_of_dharma-kubernetes-and-helm)
  - [:robot: HelmUpgradeBot - Managing Dependencies](#robot-helmupgradebot---managing-dependencies)
  - [:globe_with_meridians: Website](#globe_with_meridians-website)
  - [:recycle: Continuous Deployment](#recycle-continuous-deployment)
  - [:white_check_mark: Tests](#white_check_mark-tests)
- [:gift: How can I contribute?](#gift-how-can-i-contribute)
- [:art: Styleguides](#art-styleguides)

---

## :purple_heart: Code of Conduct

Everyone participating in this project is expecting to abide by and uphold our [Code of Conduct](CODE_OF_CONDUCT.md).
Please report any unacceptable behaviour to [Dr Sarah Gibson](mailto:sgibson@turing.ac.uk).

## :question: What do I need to know?

### :zap: Hub23

Hub23 is a [BinderHub](https://binderhub.readthedocs.io) instance.
BinderHub is computational infrastructure that makes sharing reproducible computational environments and analyses in the cloud as simple as clicking a link in your browser.
Sarah has given [many talks](https://sgibson91.github.io/speaking/) on what Binder/BinderHub/[mybinder.org](https://mybinder.org) is and how it works, so for the sake of brevity we'll just focus on Hub23 here.

Hub23 was set up to provide members of the Turing with an alternative to the public BinderHub, [mybinder.org](https://mybinder.org), which allows for authenticating users.
Eventually we also hope to support, private code repositories and datasets.

Hub23 got it's name as a derivative of the [Research Engineering team's](https://www.turing.ac.uk/research/research-programmes/research-engineering) nickname Hut23, which derives from the [hut that housed the engineering team at Bletchley Park](https://en.wikipedia.org/wiki/Bletchley_Park#Huts) during World War Two.
This, of course, was where Alan Turing and his team cracked the German Enigma code.

### :wheel_of_dharma: Kubernetes and Helm

Hub23 is deployed on a [Kubernetes cluster](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/).
This allows for effective and efficient scaling in response to demand.

This repository (<https://github.com/alan-turing-institute/hub23-deploy>) houses the [Helm chart](https://helm.sh/docs/topics/charts/), a YAML formatted set of instructions to Kubernetes on how to deploy and configure the resources and services to run BinderHub.

This chart is located in the [`hub23-chart`](./hub23-chart) folder.

### :robot: HelmUpgradeBot - Managing Dependencies

The Hub23 Helm chart is dependent on a range of other published Helm charts:

- **BinderHub:** The main software
- **`nginx-ingress`:** To monitor traffic from the internet and outside sources
- **`cert-manager`:** To automatically request HTTPS certificates from Let's Encrypt for our internet-facing endpoints

These charts are also under active development and regularly updated, so how do we make sure Hub23 is running the latest version?
With a bot of course!

[HelmUpgradeBot](https://github.com/HelmUpgradeBot/hub23-deploy-upgrades) regularly checks the Helm chart version we're running against the published versions.
If it finds a newer version, the bot will open a Pull Request updating Hub23's [`requirements.yaml`](hub23-chart/requirements.yaml) file with the most up-to-date versions.
Providing the [tests](#white_check_mark-tests) pass on the Pull Request, these are generally safe to merge.

### :globe_with_meridians: Website

The front page of the Hub23 site is described by HTML stored in the [`templates`](./templates) directory.
Any additional images (such as logos) are kept in the [`static`](./static) directory.

These templates extend the [BinderHub web framework](https://github.com/jupyterhub/binderhub/tree/master/binderhub/templates) that ships with the BinderHub Helm chart.

### :recycle: Continuous Deployment

This repository uses an [Azure Pipeline](https://docs.microsoft.com/en-gb/azure/devops/pipelines/?view=azure-devops) to keep the Hub23 deployment up-to-date with the master branch of this repository.
Any push to the master branch (such as merging a Pull Request) will [trigger the pipeline and upgrade the deployment](.az-pipelines/cd-pipeline.yml) with any changes implemented in the Helm chart.

:rotating_light: It is therefore strongly recommended that developers avoid manually upgrading the deployment.
Instead, please use a Pull Request that can be reverted if needed.
This will help maintain a consistent state of the deployment. :rotating_light:

### :white_check_mark: Tests

Kubernetes resources and Helm charts are compromised of YAML files.
Unfortunately, Helm is sensitive to malformed YAML files but fails silently during an upgrade if such a file is found.

Therefore, there is a [linting and validation pipeline](.az-pipelines/lint-pipeline.yml) implemented on the repository which runs in all Pull Requests to master branch.
This verifies that the helm chart is well-formed and can be understood by Kubernetes and Helm when applied.

The pipeline uses [YAMLlint](https://github.com/adrienverge/yamllint), [`helm lint`](https://helm.sh/docs/helm/helm_lint/), [`helm template`](https://helm.sh/docs/helm/helm_template/), and [`kubeval`](https://github.com/instrumenta/kubeval).

:rotating_light: This linting and validation test is a [Required Status Check](https://help.github.com/en/github/administering-a-repository/about-required-status-checks) and must pass before a Pull Request can be merged into master.
Again, this is to help us maintain a consistent state of the deployment. :rotating_light:

There are also two [GitHub Actions](https://help.github.com/en/actions) that check any Python code in the repository conforms to [`black`](https://github.com/psf/black) and [`flake8`](https://flake8.pycqa.org/en/latest/) conventions.
The configurations for these tests can be found in the [`.github/workflows`](.github/workflows) folder.

Lastly, another Azure Pipeline runs a nightly check to see if the deployment [subscription is still active](.az-pipelines/subscription-test.yml).
The most likely cause for the subscription to be disabled is lack of funds and all resources will be unreachable during this time.

## :gift: How can I contribute?

## :art: Styleguides
