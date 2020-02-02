"""Handler for applying team access settings.

https://developer.github.com/v3/teams/#add-or-update-team-repository
"""
import logging

from .._util import HandlerRequest
from ..exceptions import RepoAdminError

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)


def apply(request: HandlerRequest):
    """Manage team access.

    .. code-block:: yaml

        teams:
          - name: core
            permission: admin
          - name: docs
            permission: push
        # NOTE: name must be the "slug" not the given name

    """
    _LOGGER.info("Applying team access settings")
    _LOGGER.info("Teams configuration:\n%s", request.data)

    new_teams = {team["name"]: team for team in request.data}

    for team in request.repository.get_teams():
        current_permissions = team.permission

        if team.name not in new_teams:
            _LOGGER.info(
                "Team '%s' found with %s permissions not in config. Removing access for team.",
                team.name,
                current_permissions,
            )
            team.remove_from_repos(request.repository)
        else:
            new_permissions = new_teams[team.name]["permission"]
            if current_permissions != new_permissions:
                _LOGGER.info(
                    "Team '%s' found with %s permissions when %s permissions in config. Adjusting access for team.",
                    team.name,
                    current_permissions,
                    new_permissions,
                )
                team.set_repo_permission(request.repository, new_permissions)

            del new_teams[team.name]

    # Apparently we can't just get the team by name :(
    # Also, since PyGithub lacks type stubs, mypy things it's an Any
    org_teams = {team.slug: team for team in request.organization.get_teams()}  # type: ignore

    for team_data in new_teams.values():
        _LOGGER.info(
            "Adding new team access for team '%s' with %s permissions.",
            team_data["name"],
            team_data["permission"],
        )
        name = team_data["name"]
        try:
            team = org_teams[name]
        except KeyError:
            raise RepoAdminError(f"Unknown team '{name}")

        team.set_repo_permission(request.repository, team_data["permission"])
