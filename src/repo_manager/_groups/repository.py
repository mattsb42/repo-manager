"""Handler for applying repository settings.

See https://developer.github.com/v3/repos/#edit for all available settings.
"""
import logging

from .._util import HandlerRequest

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)

HEADERS = dict(
    Accept=",".join(
        [
            "application/vnd.github.nebula-preview+json",
            "application/vnd.github.baptiste-preview+json",
        ]
    )
)


def apply(request: HandlerRequest):
    """Manage repository-level settings.

    .. code-block:: yaml

        repository:
          # See https://developer.github.com/v3/repos/#edit for all available settings.

          # The name of the repository. Changing this will rename the repository
          name: repo-name

          # A short description of the repository that will show up on GitHub
          description: description of repo

          # A URL with more information about the repository
          homepage: https://example.github.io/

          # A comma-separated list of topics to set on the repository
          topics: github, probot

          # Either `true` to make the repository private, or `false` to make it public.
          private: false

          # Either `true` to enable issues for this repository, `false` to disable them.
          has_issues: true

          # Either `true` to enable projects for this repository, or `false` to disable them.
          # If projects are disabled for the organization, passing `true` will cause an API error.
          has_projects: true

          # Either `true` to enable the wiki for this repository, `false` to disable it.
          has_wiki: true

          # Either `true` to enable downloads for this repository, `false` to disable them.
          has_downloads: true

          # Updates the default branch for this repository.
          default_branch: master

          # Either `true` to allow squash-merging pull requests, or `false` to prevent
          # squash-merging.
          allow_squash_merge: true

          # Either `true` to allow merging pull requests with a merge commit, or `false`
          # to prevent merging pull requests with merge commits.
          allow_merge_commit: true

          # Either `true` to allow rebase-merging pull requests, or `false` to prevent
          # rebase-merging.
          allow_rebase_merge: true

    """
    _LOGGER.info("Applying repository settings")
    _LOGGER.info("Repository configuration:\n%s", request.data)

    request.arepo.patch(body=request.data, headers=HEADERS)
