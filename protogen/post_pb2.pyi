from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Post(_message.Message):
    __slots__ = ("id", "title", "lead", "html_content", "authors_emails", "is_published", "issue_id", "published_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    LEAD_FIELD_NUMBER: _ClassVar[int]
    HTML_CONTENT_FIELD_NUMBER: _ClassVar[int]
    AUTHORS_EMAILS_FIELD_NUMBER: _ClassVar[int]
    IS_PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    ISSUE_ID_FIELD_NUMBER: _ClassVar[int]
    PUBLISHED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    lead: str
    html_content: str
    authors_emails: _containers.RepeatedScalarFieldContainer[str]
    is_published: bool
    issue_id: int
    published_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., lead: _Optional[str] = ..., html_content: _Optional[str] = ..., authors_emails: _Optional[_Iterable[str]] = ..., is_published: bool = ..., issue_id: _Optional[int] = ..., published_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
