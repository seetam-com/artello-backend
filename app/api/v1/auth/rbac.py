from enum import Enum

class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "org:admin"
    EDITOR = "editor"
    VIEWER = "viewer"

ROLE_PERMISSIONS = {
    UserRole.OWNER: ["full_access"],
    UserRole.ADMIN: ["org:admin:full","manage_team", "edit_project", "view_project"],
    UserRole.EDITOR: ["edit_project", "view_project"],
    UserRole.VIEWER: ["view_project"],
}
