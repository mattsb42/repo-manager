"""Handler for applying milestones settings."""
import logging
from typing import Any

from github.Repository import Repository

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)


def apply(repo: Repository, data: Any):
    """Manage milestones.

    https://developer.github.com/v3/issues/milestones/#create-a-milestone

    .. code-block:: yaml

        # Milestones: define milestones for Issues and Pull Requests
        milestones:
          - title: milestone-title
            description: milestone-description
            # The state of the milestone. Either `open` or `closed`
            state: open

    """
    _LOGGER.info("Applying branch milestone settings")
    _LOGGER.info("Milestones configuration:\n%s", data)

    new_milestones = {milestone["title"]: milestone for milestone in data}

    for milestone in repo.get_milestones():
        if milestone.title not in new_milestones:
            _LOGGER.info(
                "Found milestone '%s' that is not in config. Deleting.", milestone.title
            )
            milestone.delete()
        else:
            new_values = new_milestones[milestone.title]
            if not all(
                (
                    milestone.state == new_values["state"],
                    milestone.description == new_values.get("description"),
                    milestone.due_on.isoformat() == new_values.get("due_on"),
                )
            ):
                _LOGGER.info(
                    "Found milestone '%s' that is updated in config. Updating milestone.",
                    milestone.title,
                )
                milestone.edit(**new_milestones[milestone.title])

            new_milestones.pop(milestone.title)

    for milestone in data:
        _LOGGER.info("Adding new milestone '%s'.", milestone["title"])
        repo.create_milestone(**milestone)
