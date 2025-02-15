import enum


class ClubPermissions(enum.Enum):
    READ_CLUB_CONFIDANTIAL_DATA = "club_read_club_confidential_data"
    READ_CLUB_DATA = "club_read_club_data"
    MODIFY_CLUB_DATA = "club_modify_club_data"
    DELETE_CLUB_DATA = "club_delete_club_data"
    READ_ROLES = "club_read_roles"
    MODIFY_ROLES = "club_modify_roles"
    DELETE_ROLES = "club_delete_roles"
    READ_EMPLOYEES = "club_read_employees"
    MODIFY_EMPLOYEES = "club_modify_employees"
    DELETE_EMPLOYEES = "club_delete_employees"
    READ_PROGRAMS = "club_read_programs"
    MODIFY_PROGRAMS = "club_modify_programs"
    DELETE_PROGRAMS = "club_delete_programs"
    READ_MEMBERSHIPS = "club_read_memberships"
    MODIFY_MEMBERSHIPS = "club_modify_memberships"
    DELETE_MEMBERSHIPS = "club_delete_memberships"
    READ_BOOKINGS = "club_read_bookings"


DEFAULT_CLUB_ROLES = {
    "Owner": {
        "description": "The owner of the club, has full control over the club and its settings.",
        "permissions": ["club_*"],
        "level": 0,
    },
    "Manager": {
        "description": "Can manage club settings, courses, and bookings.",
        "permissions": [
            ClubPermissions.READ_CLUB_CONFIDANTIAL_DATA.value,
            ClubPermissions.READ_CLUB_DATA.value,
            ClubPermissions.MODIFY_CLUB_DATA.value,
            ClubPermissions.DELETE_CLUB_DATA.value,
            ClubPermissions.READ_ROLES.value,
            ClubPermissions.MODIFY_ROLES.value,
            ClubPermissions.DELETE_ROLES.value,
            ClubPermissions.READ_PROGRAMS.value,
            ClubPermissions.MODIFY_PROGRAMS.value,
            ClubPermissions.DELETE_PROGRAMS.value,
            ClubPermissions.READ_MEMBERSHIPS.value,
            ClubPermissions.MODIFY_MEMBERSHIPS.value,
            ClubPermissions.DELETE_MEMBERSHIPS.value,
            ClubPermissions.READ_BOOKINGS.value,
        ],
        "level": 1,
    },
    "Instructor": {
        "description": "Can manage courses and see bookings, but not club settings.",
        "permissions": [
            ClubPermissions.READ_CLUB_DATA.value,
            ClubPermissions.READ_PROGRAMS.value,
            ClubPermissions.MODIFY_PROGRAMS.value,
            ClubPermissions.DELETE_PROGRAMS.value,
            ClubPermissions.READ_BOOKINGS.value,
        ],
        "level": 2,
    },
    "Trainer": {
        "description": "Can see bookings and manage their own courses.",
        "permissions": [
            ClubPermissions.READ_PROGRAMS.value,
            ClubPermissions.READ_BOOKINGS.value,
        ],
        "level": 10,
    },
}
