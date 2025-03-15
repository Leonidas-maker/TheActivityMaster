import enum

class PriceType(enum.Enum):
    PACKAGE = "package"
    PER_SESSION = "per_session"


class SessionType(enum.Enum):
    COURSE = "course"  # Recurring Course
    EVENT = "event"  # One-time Event

class ProgramStatusPublic(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"

class Weekday(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class OccurrenceStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class DurationUnit(enum.Enum):
    DAY = "day"
    MONTH = "month"

class MembershipStatusPublic(enum.Enum):
    DRAFT = "draft"
    BOOKABLE = "bookable"
    NOT_BOOKABLE = "not_bookable"