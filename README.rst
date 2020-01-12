##########
repo-admin
##########

.. image:: https://img.shields.io/badge/code_style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code style: black

.. important::

    This project is a work in progress and is not yet ready for use.

`repo-admin` is a GitHub Action that manages your repository for you
based on a configuration file in your repository.

`repo-admin` was inspired by `Probot Settings`_
but is designed to solve two issues with that app:

#. **Permissions** : Out of necessity,
   `Probot Settings`_ requires you to either
   hand over administrator control of your repository to the Probot app
   or to run an instance of the app yourself.
   Granting these permissions is not always possible,
   and running your own app is extra overhead that I would rather not have to deal with.

   * `repo-admin` solves this problem by running as a GitHub Action
     using the credentials that *you* provide.

#. **Debugging** : `Probot Settings`_ lacks a feedback mechanism to let you know
   when it ran and what happened.
   This is especially frustrating if you are attempting to debug a bad config,
   when the only feedback you can get is that nothing happened.

   * Because `repo-admin` runs as a GitHub Action,
     you can see exactly when it ran and what happened.


Because it runs as a GitHub Action,
you can also exert more fine control over when `repo-admin` runs,
rather than simply running on any pushes to your default branch.

`repo-admin` is fully backwards compatible with `Probot Settings`_ config files.


.. _Probot Settings: https://probot.github.io/apps/settings/
