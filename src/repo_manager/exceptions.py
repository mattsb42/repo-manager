"""Exceptions for use in repo-manager."""

__all__ = ("RepoAdminError", "UserConfigError")


class RepoAdminError(Exception):
    """Base class for repo-manager exceptions."""


class UserConfigError(RepoAdminError):
    """Used for all configuration errors."""
