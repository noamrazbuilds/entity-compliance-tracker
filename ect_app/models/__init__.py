# Import all models so Base.metadata discovers them
from ect_app.models.document import Document  # noqa: F401
from ect_app.models.entity import Entity  # noqa: F401
from ect_app.models.filing import FilingDeadline  # noqa: F401
from ect_app.models.notification import NotificationLog, NotificationSetting  # noqa: F401
from ect_app.models.officer import OfficerDirector  # noqa: F401
from ect_app.models.relationship import EntityRelationship  # noqa: F401
