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
  - [:globe_with_meridians: Website](#globe_with_meridians-website)
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

### :globe_with_meridians: Website

The front page of the Hub23 site is described by HTML stored in the [`templates`](./templates) directory.
Any additional images (such as logos) are kept in the [`static`](./static) directory.

These templates extend the [BinderHub web framework](https://github.com/jupyterhub/binderhub/tree/master/binderhub/templates) that ships with the BinderHub Helm chart.

## :gift: How can I contribute?

## :art: Styleguides
