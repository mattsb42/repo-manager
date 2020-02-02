"""Handler for applying milestones settings."""
import logging
from datetime import datetime

from .._util import HandlerRequest

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)


def apply(request: HandlerRequest):
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
    _LOGGER.info("Applying milestone settings")
    _LOGGER.info("Milestones configuration:\n%s", request.data)

    new_milestones = {}
    for milestone in request.data:
        # PyGithub sanely requires due_on to be a date or datetime rather than a string
        if "due_on" in milestone:
            # Something strange is going on here:
            # https://github.com/mattsb42/repo-manager/issues/26
            milestone["due_on"] = datetime.fromisoformat(milestone["due_on"])
        new_milestones[milestone["title"]] = milestone

    for milestone in request.repository.get_milestones(state="all"):
        if milestone.title not in new_milestones:
            _LOGGER.info("Found milestone '%s' that is not in config. Deleting.", milestone.title)
            milestone.delete()
        else:
            new_values = new_milestones[milestone.title]
            if all(
                (
                    milestone.state == new_values["state"],
                    milestone.description == new_values.get("description"),
                    milestone.due_on == new_values.get("due_on"),
                )
            ):
                _LOGGER.info(
                    "Found milestone '%s' that matches config. Skipping milestone.", milestone.title
                )
            else:
                _LOGGER.info(
                    "Found milestone '%s' that is updated in config. Updating milestone.",
                    milestone.title,
                )
                milestone.edit(**new_milestones[milestone.title])

            del new_milestones[milestone.title]

    for milestone in new_milestones.values():
        _LOGGER.info("Adding new milestone '%s'.", milestone["title"])
        request.repository.create_milestone(**milestone)
