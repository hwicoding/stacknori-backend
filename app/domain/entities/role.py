from enum import Enum


class UserRole(str, Enum):
    """User role enumeration for access control."""

    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"  # Alias for backward compatibility with is_superuser

    def __str__(self) -> str:
        return self.value

