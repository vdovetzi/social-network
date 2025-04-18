# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: service/proto/service.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'service/proto/service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bservice/proto/service.proto\x12\x05posts\x1a\x1fgoogle/protobuf/timestamp.proto\"\xcc\x01\n\x04Post\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x12\n\ncreator_id\x18\x04 \x01(\t\x12.\n\ncreated_at\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12.\n\nupdated_at\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x12\n\nis_private\x18\x07 \x01(\x08\x12\x0c\n\x04tags\x18\x08 \x03(\t\"m\n\x11\x43reatePostRequest\x12\r\n\x05title\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12\x12\n\ncreator_id\x18\x03 \x01(\t\x12\x12\n\nis_private\x18\x04 \x01(\x08\x12\x0c\n\x04tags\x18\x05 \x03(\t\"-\n\x0eGetPostRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\"y\n\x11UpdatePostRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x12\n\nupdater_id\x18\x04 \x01(\t\x12\x12\n\nis_private\x18\x05 \x01(\x08\x12\x0c\n\x04tags\x18\x06 \x03(\t\"3\n\x11\x44\x65letePostRequest\x12\n\n\x02id\x18\x01 \x01(\t\x12\x12\n\ndeleter_id\x18\x02 \x01(\t\"%\n\x12\x44\x65letePostResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\"C\n\x10ListPostsRequest\x12\x0c\n\x04page\x18\x01 \x01(\x05\x12\x10\n\x08per_page\x18\x02 \x01(\x05\x12\x0f\n\x07user_id\x18\x03 \x01(\t\"^\n\x11ListPostsResponse\x12\x1a\n\x05posts\x18\x01 \x03(\x0b\x32\x0b.posts.Post\x12\r\n\x05total\x18\x02 \x01(\x05\x12\x0c\n\x04page\x18\x03 \x01(\x05\x12\x10\n\x08per_page\x18\x04 \x01(\x05\")\n\x0cPostResponse\x12\x19\n\x04post\x18\x01 \x01(\x0b\x32\x0b.posts.Post2\xc1\x02\n\x0bPostService\x12;\n\nCreatePost\x12\x18.posts.CreatePostRequest\x1a\x13.posts.PostResponse\x12\x35\n\x07GetPost\x12\x15.posts.GetPostRequest\x1a\x13.posts.PostResponse\x12;\n\nUpdatePost\x12\x18.posts.UpdatePostRequest\x1a\x13.posts.PostResponse\x12\x41\n\nDeletePost\x12\x18.posts.DeletePostRequest\x1a\x19.posts.DeletePostResponse\x12>\n\tListPosts\x12\x17.posts.ListPostsRequest\x1a\x18.posts.ListPostsResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service.proto.service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_POST']._serialized_start=72
  _globals['_POST']._serialized_end=276
  _globals['_CREATEPOSTREQUEST']._serialized_start=278
  _globals['_CREATEPOSTREQUEST']._serialized_end=387
  _globals['_GETPOSTREQUEST']._serialized_start=389
  _globals['_GETPOSTREQUEST']._serialized_end=434
  _globals['_UPDATEPOSTREQUEST']._serialized_start=436
  _globals['_UPDATEPOSTREQUEST']._serialized_end=557
  _globals['_DELETEPOSTREQUEST']._serialized_start=559
  _globals['_DELETEPOSTREQUEST']._serialized_end=610
  _globals['_DELETEPOSTRESPONSE']._serialized_start=612
  _globals['_DELETEPOSTRESPONSE']._serialized_end=649
  _globals['_LISTPOSTSREQUEST']._serialized_start=651
  _globals['_LISTPOSTSREQUEST']._serialized_end=718
  _globals['_LISTPOSTSRESPONSE']._serialized_start=720
  _globals['_LISTPOSTSRESPONSE']._serialized_end=814
  _globals['_POSTRESPONSE']._serialized_start=816
  _globals['_POSTRESPONSE']._serialized_end=857
  _globals['_POSTSERVICE']._serialized_start=860
  _globals['_POSTSERVICE']._serialized_end=1181
# @@protoc_insertion_point(module_scope)
