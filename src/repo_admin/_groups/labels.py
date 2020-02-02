"""Handler for applying labels settings."""
import logging
from typing import Dict

from .._util import HandlerRequest

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)


def apply(request: HandlerRequest):
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
    _LOGGER.info("Applying label settings")
    _LOGGER.info("Labels configuration:\n%s", request.data)

    requested_new_or_update: Dict[str, Dict[str, str]] = {}
    requested_rename: Dict[str, Dict[str, str]] = {}

    for label in request.data:
        # YAML can interpret these as numbers but the API requires strings.
        # Also, make sure that any leading # values are removed.
        label["color"] = str(label["color"]).replace("#", "")
        if "oldname" in label:
            old_name = label["oldname"]
            # prep rename and update scenarios
            rename = label.copy()
            del rename["oldname"]

            # add to rename in case the label has not yet been renamed
            requested_rename[old_name] = rename
            # add to updates in case it has
            requested_new_or_update[rename["name"]] = rename

        else:
            requested_new_or_update[label["name"]] = label

    for label in request.repository.get_labels():
        if label.name in requested_rename:
            _LOGGER.info("Found label '%s' that is renamed in config. Updating label.", label.name)
            new_values = requested_rename[label.name].copy()
            old_name = label.name
            label.edit(**new_values)
            del requested_rename[old_name]
            # The label has not previously been renamed, so remove it from the update request
            del requested_new_or_update[label.name]
            continue

        if label.name in requested_new_or_update:
            new_values = requested_new_or_update[label.name].copy()
            if not all(
                (
                    label.color == new_values["color"],
                    label.description == new_values["description"],
                )
            ):
                _LOGGER.info(
                    "Found label '%s' that is updated in config. Updating label.", label.name,
                )
                label.edit(**new_values)
            del requested_new_or_update[label.name]
            continue

        _LOGGER.info("Found label '%s' that is not in config. Deleting label.", label.name)
        label.delete()

    for name, label in requested_new_or_update.items():
        _LOGGER.info("New label '%s' in config. Adding label.", name)
        request.repository.create_label(**label)
