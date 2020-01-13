"""Handler for applying labels settings.


"""
import logging
from typing import Any, Dict

from github.Repository import Repository

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)


def apply(repo: Repository, data: Any):
    """Manage labels.

    https://developer.github.com/v3/issues/labels/#create-a-label

    .. code-block:: yaml

        # Labels: define labels for Issues and Pull Requests
        labels:
          - name: bug
            color: CC0000
            description: An issue with the system 🐛.

          - name: feature
            # If including a `#`, make sure to wrap it with quotes!
            color: '#336699'
            description: New functionality.

          - name: first-timers-only
            # include the old name to rename an existing label
            oldname: Help Wanted

    """
    _LOGGER.info("Applying branch label settings")
    _LOGGER.info("Labels configuration:\n%s", data)

    new_labels: Dict[str, Dict[str, str]] = {}
    for label in data:
        label["color"] = str(label["color"]).replace("#", "")
        # TODO: Need to handle both cases where this is the renaming update
        #  AND for subsequent updates.
        #  Will probably require a second structure of "possible hanging labels".
        # if "oldname" in label:
        #     label["new_name"] = label["name"]
        #     label["name"] = label["oldname"]
        #     del label["oldname"]
        new_labels[label["name"]] = label

    # Delete or update any existing labels
    for label in repo.get_labels():
        if label.name not in new_labels:
            _LOGGER.info(
                "Found label '%s' that is not in config. Removing label.", label.name
            )
            label.delete()
        else:
            new_values = new_labels[label.name]
            if not all(
                (
                    label.color == new_values["color"],
                    label.description == new_values["description"],
                    "new_name" not in new_values,
                )
            ):
                _LOGGER.info(
                    "Found label '%s' that is updated in config. Updating label.",
                    label.name,
                )
                label.edit(**new_labels[label.name])
            new_labels.pop(label.name)

    # Add any new labels
    for label in new_labels.values():
        # YAML can interpret these as numbers but the API requires strings.
        # Also, make sure that any leading # values are removed.
        _LOGGER.info("Adding new label '%s'.", label["name"])
        repo.create_label(**label)