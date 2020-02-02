"""Handler for applying collaborators settings."""
import logging

from .._util import HandlerRequest, permission_to_string

__all__ = ("apply",)
_LOGGER = logging.getLogger(__name__)


def apply(request: HandlerRequest):
    """Manage collaborators.

    .. code-block:: yaml

        # Collaborators: give specific users access to this repository.
        collaborators:
          - username: bkeepers
            # Note: Only valid on organization-owned repositories.
            # The permission to grant the collaborator. Can be one of:
            # * `pull` - can pull, but not push to or administer this repository.
            # * `push` - can pull and push, but not administer this repository.
            # * `admin` - can pull, push and administer this repository.
            permission: push

          - username: hubot
            permission: pull

    """

    _LOGGER.info("Applying collaborator settings.")
    _LOGGER.info("Collaborators configuration:\n%s", request.data)

    new_collaborators = {user["username"]: user for user in request.data}

    # First, clear all pending invites
    for invite in request.repository.get_pending_invitations():
        request.repository.remove_invitation(invite.id)

    # Then, sync collaborators
    for collaborator in request.repository.get_collaborators():
        current_permissions = permission_to_string(collaborator.permissions)

        if (
            collaborator.login not in new_collaborators
            and collaborator.login != request.repository.owner
        ):
            _LOGGER.info(
                "Collaborator '%s' found with %s permissions not in config. Removing access for user.",
                collaborator.login,
                current_permissions,
            )
            request.repository.remove_from_collaborators(collaborator)
        else:
            new_permissions = new_collaborators[collaborator.login]["permission"]

            if current_permissions == new_permissions:
                _LOGGER.info(
                    "Found existing collaborator '%s' with expected %s permissions. Skipping.",
                    collaborator.login,
                    current_permissions,
                )
            else:
                _LOGGER.info(
                    "Collaborator '%s' found with %s permissions when %s permissions in config."
                    " Adjusting access for user.",
                    collaborator.login,
                    current_permissions,
                    new_permissions,
                )
                request.repository.remove_from_collaborators(collaborator)
                request.repository.add_to_collaborators(collaborator, permission=new_permissions)

            del new_collaborators[collaborator.login]

    for collaborator in new_collaborators.values():
        _LOGGER.info(
            "Adding new collaborator '%s' with %s permissions.",
            collaborator["username"],
            collaborator["permission"],
        )
        request.repository.add_to_collaborators(
            collaborator=collaborator["username"], permission=collaborator["permission"]
        )

    _LOGGER.info("Branch collaborator settings applied.")
