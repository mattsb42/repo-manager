# repo-manager

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**NOTICE: This project is a work in progress and is not yet ready for use.**

`repo-manager` is a GitHub Action that manages your repository for you
based on a configuration file in your repository.

`repo-manager` was inspired by [Probot Settings]
but is designed to solve two issues with that app:

1. **Permissions** : Out of necessity,
   [Probot Settings] requires you to either
   hand over administrator control of your repository to the Probot app
   or to run an instance of the app yourself.
   Granting these permissions is not always possible,
   and running your own app is extra overhead that I would rather not have to deal with.

   * `repo-manager` solves this problem by running as a GitHub Action
     using the credentials that *you* provide.

1. **Debugging** : [Probot Settings] lacks a feedback mechanism to let you know
   when it ran and what happened.
   This is especially frustrating if you are attempting to debug a bad config,
   when the only feedback you can get is that nothing happened.

   * Because `repo-manager` runs as a GitHub Action,
     you can see exactly when it ran and what happened.


Because it runs as a GitHub Action,
you can also exert more fine control over when `repo-manager` runs,
rather than simply running on any pushes to your default branch.

`repo-manager` is fully backwards compatible with [Probot Settings] config files,
but will expand in the future to support more repository administration features.


[Probot Settings]: https://probot.github.io/apps/settings/
