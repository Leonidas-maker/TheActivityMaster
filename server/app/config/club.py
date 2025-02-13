import enum

class ClubPermissions(enum.Enum):
    READ_CLUB_CONFIDANTIAL_DATA = "club_read_club_confidential_data"
    READ_CLUB_DATA = "club_read_club_data"
    WRITE_CLUB_DATA = "club_write_club_data"
    DELETE_CLUB_DATA = "club_delete_club_data"
    UPDATE_CLUB_SETTINGS = "club_update_club_settings"
    READ_PROGRAMS = "club_read_programs"
    MODIFY_PROGRAMS = "club_modify_programs"
    READ_MEMBERSHIPS = "club_read_memberships"
    MODIFY_MEMBERSHIPS = "club_modify_memberships"
    READ_BOOKINGS = "club_read_bookings"