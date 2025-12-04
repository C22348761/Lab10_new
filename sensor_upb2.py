'''
from uprotobuf import *


@registerMessage
class TimeMessage(Message):
    _proto_fields=[
        dict(name='epoch', type=WireType.Varint, subType=VarintSubType.UInt64, fieldType=FieldType.Required, id=1),
    ]

@registerMessage
class SensorreadingMessage(Message):
    _proto_fields=[
        dict(name='temperature', type=WireType.Bit32, subType=FixedSubType.Float, fieldType=FieldType.Required, id=1),
        dict(name='publisher_id', type=WireType.Length, subType=LengthSubType.String, fieldType=FieldType.Required, id=2),
        dict(name='timestamp', type=WireType.Length, subType=LengthSubType.Message, fieldType=FieldType.Required, id=3, mType='.sensor.Time'),
    ]
'''
from uprotobuf import *


@registerMessage
class TimeMessage(Message):
    _proto_fields=[
        dict(name='epoch', type=WireType.Varint, subType=VarintSubType.UInt64, fieldType=FieldType.Required, id=1),
    ]

@registerMessage
class SensorreadingMessage(Message):
    _proto_fields=[
        dict(name='temperature', type=WireType.Bit32, subType=FixedSubType.Float, fieldType=FieldType.Required, id=1),
        dict(name='publisher_id', type=WireType.Length, subType=LengthSubType.String, fieldType=FieldType.Required, id=2),
        dict(name='timestamp', type=WireType.Varint, subType=VarintSubType.UInt64, fieldType=FieldType.Required, id=3),
    ]