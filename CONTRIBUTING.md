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
  - [:book: Documentation](#book-documentation)
  - [:sparkles: Extras](#sparkles-extras)
- [:gift: How can I contribute?](#gift-how-can-i-contribute)
  - [:bug: Bug Reports](#bug-bug-reports)
  - [:rocket: Feature Requests](#rocket-feature-requests)
  - [:twisted_rightwards_arrows: Pull Requests](#twisted_rightwards_arrows-pull-requests)
- [:art: Styleguides](#art-styleguides)
  - [:snake: Python Styleguide](#snake-python-styleguide)
  - [:pencil: Markdown styleguide](#pencil-markdown-styleguide)
- [:notebook: Additional Notes](#notebook-additional-notes)
  - [:label: Issue and Pull Request Labels](#label-issue-and-pull-request-labels)

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
Eventually we also hope to support private code repositories and datasets.

Hub23 got it's name as a derivative of the [Research Engineering team's](https://www.turing.ac.uk/research/research-programmes/research-engineering) nickname Hut23, which derives from the [hut that housed the engineering team at Bletchley Park](https://en.wikipedia.org/wiki/Bletchley_Park#Huts) during World War Two.
This, of course, was where Alan Turing and his team cracked the German Enigma code.

### :wheel_of_dharma: Kubernetes and Helm

Hub23 is deployed on a [Kubernetes cluster](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/).
This allows for effective and efficient scaling in response to demand.

This repository (<https://github.com/alan-turing-institute/hub23-deploy>) houses the [Helm chart](https://helm.sh/docs/topics/charts/), a YAML formatted set of instructions to Kubernetes on how to deploy and configure the resources and services to run BinderHub.

This chart is located in the [`hub23-chart`](./hub23-chart) folder and the deployment configuration is stored in [`deploy`](./deploy).

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

This repository uses an [Azure Pipeline](https://docs.microsoft.com/en-gb/azure/devops/pipelines/?view=azure-devops) to keep the Hub23 deployment up-to-date with the main branch of this repository.
Any push to the master branch (such as merging a Pull Request) will [trigger the pipeline and upgrade the deployment](.az-pipelines/cd-pipeline.yml) with any changes implemented in the Helm chart.

:rotating_light: It is therefore strongly recommended that developers avoid manually upgrading the deployment.
Instead, please use a Pull Request that can be reverted if needed.
This will help maintain a consistent state of the deployment. :rotating_light:

### :white_check_mark: Tests

Kubernetes resources and Helm charts are compromised of YAML files.
Unfortunately, Helm is sensitive to malformed YAML files but fails silently during an upgrade if such a file is found.

Therefore, there is a [linting and validation pipeline](.az-pipelines/lint-pipeline.yml) implemented on the repository which runs in all Pull Requests to main branch.
This verifies that the helm chart is well-formed and can be understood by Kubernetes and Helm when applied.

The pipeline uses [YAMLlint](https://github.com/adrienverge/yamllint), [`helm lint`](https://helm.sh/docs/helm/helm_lint/), [`helm template`](https://helm.sh/docs/helm/helm_template/), and [`kubeval`](https://github.com/instrumenta/kubeval).

:rotating_light: This linting and validation test is a [Required Status Check](https://help.github.com/en/github/administering-a-repository/about-required-status-checks) and must pass before a Pull Request can be merged into main.
Again, this is to help us maintain a consistent state of the deployment. :rotating_light:

There are also two [GitHub Actions](https://help.github.com/en/actions) that check any Python code in the repository conforms to [`black`](https://github.com/psf/black) and [`flake8`](https://flake8.pycqa.org/en/latest/) conventions.
The configurations for these tests can be found in the [`.github/workflows`](.github/workflows) folder.

Lastly, another Azure Pipeline runs a nightly check to see if the deployment [subscription is still active](.az-pipelines/subscription-test.yml).
The most likely cause for the subscription to be disabled is lack of funds and all resources will be unreachable during this time.

### :book: Documentation

The Hub23 Deployment Guide is written in Markdown files kept in the [`docs/_posts`](./docs/_posts) folder.
These are then rendered using [Jekyll](https://jekyllrb.com/) and [GitHub Pages](https://help.github.com/en/github/working-with-github-pages/about-github-pages) and served at [alan-turing-instutite.github.io/hub23-deploy](https://alan-turing-instutite.github.io/hub23-deploy), using the [So Simple theme](https://github.com/mmistakes/so-simple-theme).

### :sparkles: Extras

- **CLI tool:** There is a command line interface tool called [`hub-manager`](./cli-tool) that can make interacting with Hub23 easier.
  Please read the [README](cli-tool/README.md).
- **Billing:** There is a Python script under [`billing`](./billing) that helps calculate running costs for the deployment.
  If the subscription runs out of funds, a [request for more credits](https://turingcomplete.topdesk.net/tas/public/ssp/content/serviceflow?unid=b6672711a411404482aedce2fcc981be&openedFromService=true) should be filed on Turing Complete (TopDesk).

## :gift: How can I contribute?

### :bug: Bug Reports

If something doesn't work the way you expect it to, please check it hasn't already been reported in the repository's [issue tracker](https://github.com/alan-turing-institute/hub23-deploy/issues).
Bug reports should have the [bug label]([is:issue is:open label:bug ](https://github.com/alan-turing-institute/hub23-deploy/issues?q=is%3Aissue+is%3Aopen+label%3Abug)), or have a title beginning with [`[BUG]`](https://github.com/alan-turing-institute/hub23-deploy/issues?q=is%3Aissue+is%3Aopen+%5BBUG%5D).

If you can't find an issue already reporting your bug, then please feel free to [open a new issue](https://github.com/alan-turing-institute/hub23-deploy/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBUG%5D).
This repository has a [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) to reports be as descriptive as possible so we can squash that bug! :muscle:

### :rocket: Feature Requests

If there is something extra you wish Hub23 could do, please check that the feature hasn't already been requested in the project's [issue tracker](https://github.com/alan-turing-institute/hub23-deploy/issues).
Feature requests should have the [enhancement label](https://github.com/alan-turing-institute/hub23-deploy/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement).
Please also check the [closed issues](https://github.com/alan-turing-institute/hub23-deploy/issues?q=is%3Aissue+is%3Aclosed) to make sure the feature has not already been requested but the project maintainers decided against developing it.

If you find an open issue describing the feature you wish for, you can "+1" the issue by giving a thumbs up reaction on the top comment.
You may also leave any thoughts or offers for support as new comments on the issue.

If you don't find an issue describing your feature, please [open a feature request](https://github.com/alan-turing-institute/hub23-deploy/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=%5BFEATURE%5D).
This repository has a [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) to help map out the feature you'd like.

### :twisted_rightwards_arrows: Pull Requests

A Pull Request is a means for [people to collaboratively review and work on changes](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests) before they are introduced into the base branch of the code base.

To prepare your contribution for review, please follow these steps:

1. [Fork this repository](https://help.github.com/en/github/getting-started-with-github/fork-a-repo)
2. [Create a new branch](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-and-deleting-branches-within-your-repository) on your fork
   1. Where possible and appropriate, please use the following convention when naming your branch: `<type>/<issue-number>/<short-description>`.
      For example, if your contribution is fixing a a typo that was flagged in issue number 11, your branch name would be as follows: `fix/11/typo`.
3. Edit files or add new ones!
4. [Open your Pull Request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork)
   1. This repository has a [pull request template](.github/PULL_REQUEST_TEMPLATE.md) which will help you summarise your contribution and help reviewers know where to focus their feedback.
      Please complete it where possible and appropriate.

Congratulations! :tada:
You are now a Hub23 developer! :space_invader:

The project maintainers will then review your Pull Request and may ask for some changes.
Once you and the maintainers are happy, your contribution will be merged!

## :art: Styleguides

### :snake: Python Styleguide

When writing Python scripts for this repository, it is recommended that contributors use [black](https://github.com/psf/black) and [flake8](https://flake8.pycqa.org/en/latest/) for formatting and linting styles.
The repository has [GitHub Actions to check files are conforming to this styleguide](#white_check_mark-tests), though not doing so will not prevent your contribution from being merged.
These tools are used as the maintainers believe this makes the code easier to read and keeps consistent formatting as more people contribute to the project.

While flake8 commands can be [disabled](https://flake8.pycqa.org/en/latest/user/violations.html), we only recommend doing this for [specific lines](https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors) in such cases where reformatting would produce "ugly code".
The maintainers retain final say on what is "ugly code" on a case-by-case basis.

This repository also contains configuration files to install a [pre-commit hook](https://githooks.com/) that will run black and flake8 on each commit so you don't have to worry!
To install the pre-commit hook, do the following:

```bash
# Install the development requirements
pip install -r dev-requirements.txt

# Install the pre-commit configuration
pre-commit install
```

And you're good to go! :tada:

### :pencil: Markdown Styleguide

Documentation files are written in [Markdown](https://guides.github.com/features/mastering-markdown/).

When writing Markdown, it is recommended to start a new sentence on a new line and define a new paragraph by leaving a single blank line.
(Check out the raw version of this file for an example!)
While the sentences will render as a single paragraph; when suggestions are made on Pull Requests, the GitHub User Interface will only highlight the affected sentence - not the whole paragraph.
This makes reviews much easier to read!

## :notebook: Additional Notes

### :label: Issue and Pull Request Labels

Issues and Pull Requests can have labels assigned to them which indicate at a glance what aspects of the project they describe.
It is also possible to [sort issues by label](https://help.github.com/en/github/managing-your-work-on-github/filtering-issues-and-pull-requests-by-labels) making it easier to track down specific issues.
Below is a table with the currently used labels in the repo.

| Label | Description |
| :--- | :--- |
| `bug` | Something isn't working |
| `documentation` | Improvements or additions to the documentation |
| `enhancement` | New feature or request |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention is needed |
| `question` | Looking for input on a topic |
| `wip` | Work in progress |
