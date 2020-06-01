# repo-manager

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

`repo-manager` is a GitHub Action that manages your repository for you
based on a configuration file in your repository.

## Configuration

## Usage

### Inputs

`repo-manager` offers three inputs that you can use to configure its behavior.
The only required input is `github-token`.

**NOTE: The token you provide MUST have full admin permissions on your repo.
The [built-in GitHub Actions token][github actions token] will not work.**

1. `github-token` (required) :
    The OAuth token that `repo-manager` should use.
    * This token MUST have full admin permissions on your repo.
        Because of this,
        the [built-in GitHub Actions token][github actions token] will not work.
    * NOTE: Make sure that you never put tokens in your workflow files directly.
        Always use [GitHub Secrets] to store these values.
1. `config-file` (optional) :
    The location of the config file that `repo-manager` should use.
    By default, `repo-manager` assumes that your config file is
    where [Probot Settings] needs it to be (`.github/settings.yml`).
    If you want to put your config file somewhere else in your repo,
    you can control that using this value.
1. `debug` (optional) :
    If you set this value to `true`, `repo-manager` will output more granular logs.

### Examples

To use `repo-manager`, simply define a step in your workflow, providing your GitHub Token.

```yaml
- uses: mattsb42/repo-manager@v1
  with:
    github-token: ${{ secrets.ADMIN_GITHUB_TOKEN }}
```


If you want to enable debug logging or use a special config file location,
you indicate that with the other input values.

```yaml
- uses: mattsb42/repo-manager@v1
  with:
    github-token: ${{ secrets.ADMIN_GITHUB_TOKEN }}
    config-file: .github/config/repository.yaml
    debug: true
```

## Design Goals

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
[github actions token]: https://help.github.com/en/actions/automating-your-workflow-with-github-actions/authenticating-with-the-github_token#permissions-for-the-github_token
[Github Secrets]: https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets
