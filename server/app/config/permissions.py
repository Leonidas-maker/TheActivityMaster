import enum


class ClubPermissions(enum.Enum):
    READ_CLUB_CONFIDANTIAL_DATA = "club_read_club_confidential_data"
    READ_CLUB_DATA = "club_read_club_data"
    UPDATE_CLUB_DATA = "club_update_club_data"
    DELETE_CLUB_DATA = "club_delete_club_data"
    CREATE_ROLES = "club_create_roles"
    READ_ROLES = "club_read_roles"
    UPDATE_ROLES = "club_update_roles"
    DELETE_ROLES = "club_delete_roles"
    CREATE_EMPLOYEES = "club_create_employees"
    READ_EMPLOYEES = "club_read_employees"
    UPDATE_EMPLOYEES = "club_update_employees"
    DELETE_EMPLOYEES = "club_delete_employees"
    CREATE_PROGRAMS = "club_create_programs"
    READ_PROGRAMS = "club_read_programs"
    UPDATE_PROGRAMS = "club_update_programs"
    DELETE_PROGRAMS = "club_delete_programs"
    CREATE_MEMBERSHIPS = "club_create_memberships"
    READ_MEMBERSHIPS = "club_read_memberships"
    UPDATE_MEMBERSHIPS = "club_update_memberships"
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
            ClubPermissions.READ_CLUB_DATA.value,
            ClubPermissions.UPDATE_CLUB_DATA.value,
            ClubPermissions.DELETE_CLUB_DATA.value,
            ClubPermissions.CREATE_ROLES.value,
            ClubPermissions.READ_ROLES.value,
            ClubPermissions.UPDATE_ROLES.value,
            ClubPermissions.DELETE_ROLES.value,
            ClubPermissions.CREATE_PROGRAMS.value,
            ClubPermissions.READ_PROGRAMS.value,
            ClubPermissions.UPDATE_PROGRAMS.value,
            ClubPermissions.DELETE_PROGRAMS.value,
            ClubPermissions.READ_MEMBERSHIPS.value,
            ClubPermissions.UPDATE_MEMBERSHIPS.value,
            ClubPermissions.DELETE_MEMBERSHIPS.value,
            ClubPermissions.READ_BOOKINGS.value,
        ],
        "level": 1,
    },
    "Instructor": {
        "description": "Can manage courses and see bookings, but not club settings.",
        "permissions": [
            ClubPermissions.READ_CLUB_DATA.value,
            ClubPermissions.CREATE_PROGRAMS.value,
            ClubPermissions.READ_PROGRAMS.value,
            ClubPermissions.UPDATE_PROGRAMS.value,
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
