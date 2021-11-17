"""Events for the Gitlab Connector."""
from typing import Optional

from opsdroid.events import Event

"""
TODO:  We need to remove the 'url' argument from the events,
url will become 'target' which is available in the base class
Event!
"""


class GenericGitlabEvent(Event):
    """Event class that triggers when an unhandled event is sent."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class IssueCreated(Event):
    """Event class that triggers when a new issue is created."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class IssueClosed(Event):
    """Event class that triggers when an issue is closed."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class IssueEdited(Event):
    """Event class that triggers when an issue is edited."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class IssueLabeled(Event):
    """Event class that triggers when an issue is labeled."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class GenericIssueEvent(Event):
    """Event class that triggers when any other issue action happen."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class MRCreated(Event):
    """Event class that triggers when a MR is created."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class MRMerged(Event):
    """Event class that triggers when a MR is merged."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class MRClosed(Event):
    """Event class that triggers when a MR is closed."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class MRLabelUpdated(Event):
    """Event class that triggers when a MR label is updated."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class MRApproved(Event):
    """Event class that triggers when a MR is approved."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url


class GenericMREvent(Event):
    """Event class that triggers when a Generic MR Event happens."""

    def __init__(
        self,
        project: str,
        user: str,
        title: Optional[str],
        description: Optional[str],
        labels: list,
        url: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project = project
        self.user = user
        self.title = title
        self.description = description
        self.labels = labels
        self.url = url
