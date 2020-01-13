"""Handler for applying team access settings.

https://developer.github.com/v3/teams/#add-or-update-team-repository
"""
import logging
from typing import Any

from github.Organization import Organization
from github.Repository import Repository

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)


def _organization_from_repo(repo: Repository) -> Organization:
    # TODO: More bad things here, though this one is me being lazy.
    headers, data = repo._requester.requestJsonAndCheck(
        "GET", "/orgs/" + repo.owner.login
    )
    return Organization(repo._requester, headers, data, completed=True)


def apply(repo: Repository, data: Any):
    """Manage team access.

    .. code-block:: yaml

        teams:
          - name: core
            permission: admin
          - name: docs
            permission: push
        # NOTE: name must be the "slug" not the given name

    """
    _LOGGER.info("Applying branch protection settings")
    _LOGGER.info("Teams configuration:\n%s", data)

    new_teams = {team["name"]: team for team in data}

    for team in repo.get_teams():
        current_permissions = team.permission

        if team.name not in new_teams:
            _LOGGER.info(
                "Team '%s' found with %s permissions not in config. Removing access for team.",
                team.name,
                current_permissions,
            )
            team.remove_from_repos(repo)
        else:
            new_permissions = new_teams[team.name]["permission"]
            if current_permissions != new_permissions:
                _LOGGER.info(
                    "Team '%s' found with %s permissions when %s permissions in config. Adjusting access for team.",
                    team.name,
                    current_permissions,
                    new_permissions,
                )
                team.set_repo_permission(repo, new_permissions)

            del new_teams[team.name]

    org = _organization_from_repo(repo)
    for team_data in new_teams.values():
        _LOGGER.info(
            "Adding new team access for team '%s' with %s permissions.",
            team_data["name"],
            team_data["permission"],
        )
        team = org.get_team_by_slug(team_data["name"])
        team.set_repo_permission(repo, team_data["permission"])
