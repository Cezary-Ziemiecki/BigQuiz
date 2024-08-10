import abc
import collections.abc as collections
from bson.objectid import ObjectId
from pymongo.errors import InvalidName
from pymongo.database import Database


class UnchangedProperty(abc.ABC):
    def __init__(self, default=None) -> None:
        self.instances = {}
        self._default = default

    def __get__(self, instance, parent):
        if instance is None:
            return self
        try:
            return self.instances[instance]
        except KeyError:
            return self._default
        except Exception as e:
            print(e)

    def __set__(self, instance, value):
        if instance in self.instances:
            raise AttributeError("can't set attribute")
        else:
            try:
                value = self.validate(value)
            except Exception as e:
                print(e)
            else:
                self.instances[instance] = value

    @abc.abstractmethod
    def validate(self, value):
        """"""


class UnchangedTypedPropert(UnchangedProperty):

    def __init__(self, cls, default=None) -> None:
        super().__init__(default)
        self._cls = cls

    def validate(self, value):
        if isinstance(value, self._cls):
            return value
        else:
            raise TypeError


class IterableStorage(abc.ABC):

    def __init__(self):
        self.storage = []

    def __setitem__(self, key, value):
        try:
            value = self.validate(value)
        except Exception as e:
            print(e)
        else:
            self.storage[key] = value

    def __iter__(self):
        return iter(self.storage)

    def __getitem__(self, index):
        return self.storage[index]

    def append(self, value):
        try:
            value = self.validate(value)
        except Exception as e:
            print(e)
        else:
            self.storage.append(value)

    @abc.abstractmethod
    def validate(self, value):
        """"""


class MongoId():
    def __init__(self):
        super().__init__()

    def set_collection(self, collection):
        self.collection = collection

    def validate(self, value):
        if type(value) == ObjectId:
            result = self.collection.find({'_id': value})
        elif type(value) in [str, int]:
            object_id = ['0']*(24-len(str(value)))+list(str(value))
            value = ObjectId(''.join(object_id))
            result = self.collection.find(
                {'_id': ObjectId(''.join(object_id))})
        else:
            raise ValueError('value must be in type ObjectId, str or int')
        if len(list(result)):
            if not isinstance(self, collections.Iterable) or value not in list(self):
                return value
            raise ValueError(f'Value {value} is in collection')
        raise InvalidName(f'There was no record with id: {value}')


class MongoIdList(MongoId, IterableStorage):
    """"""
