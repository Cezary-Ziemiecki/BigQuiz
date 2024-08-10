import abc
import collections.abc as collections
from bson.objectid import ObjectId
from pymongo.errors import InvalidName
from pymongo.database import Database


class UnchangedProperty(abc.ABC):
    """
    Abstract Descriptor for validated once set property.

    Methods
    validate(value)
        Abstract method for validate new property value
    """

    def __init__(self, default=None) -> None:
        """
        Prepare instances dict for multi owner usage
        ----------
        default :, None
            default preset value
        """
        self.instances = {}
        self._default = default

    def __get__(self, instance, parent):
        """
        Getter method return default value in case of preset state
        Parameters
        ----------
        instance :
        parent :

        Returns
        -------
            instance connected value
        """
        if instance is None:
            return self
        try:
            return self.instances[instance]
        except KeyError:
            return self._default
        except Exception as e:
            print(e)

    def __set__(self, instance, value):
        """
        Setter method settings unset instance value by valid value 

        Parameters
        ----------
        instance :
        value :

        Raises
        ------
        AttributeError
            If the value is previous set
        """
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
        """
        Abstract method for validate new property value
        Parameters
        ----------
        value :
            Validated value
        """


class UnchangedTypedPropert(UnchangedProperty):
    """
    Descriptor for type controled once set property.
    Methods
    ----------
    validate(value)
        Type checking of new property value
    """

    def __init__(self, cls, default=None) -> None:
        """
        Prepare instances dict for multi owner usage
        ----------
        cls : type
            obligating type of value
        default :, None
            default preset value
        """
        super().__init__(default)
        self._cls = cls

    def validate(self, value):
        """
        Type checking of new property value
        Parameters
        ----------
        value :
           Validated value

        Returns
        -------
            value being instance of saved class

        Raises
        ------
        TypeError
            receiving value is not instance of concrete type
        """
        if isinstance(value, self._cls):
            return value
        else:
            raise TypeError


class IterableStorage(abc.ABC):
    """
    Abstract class for validated Iterable storages
    Methods
    ----------
    validate(value)
        Type checking of new property value
    """

    def __init__(self):
        """
        Create storage list for validated values
        """
        self.storage = []

    def __setitem__(self, key, value):
        """
            Validated list item edition
        Parameters
        ----------
        key : int
            index of changing list element
        value : _type_
            new value of list element
        """
        try:
            value = self.validate(value)
        except Exception as e:
            print(e)
        else:
            self.storage[key] = value

    def __iter__(self):
        """
            Create storage iterator
        Returns
        -------
        iterable object
            iterable storage
        """
        return iter(self.storage)

    def __getitem__(self, key):
        """
            Get element from storage
        Parameters
        ----------
        key : int
            index of element

        Returns
        -------
            key'th element from storage
        """
        return self.storage[key]

    def append(self, value):
        """
        Add new validated element to the end of storage
        Parameters
        ----------
        value :
            New validated element
        """
        try:
            value = self.validate(value)
        except Exception as e:
            print(e)
        else:
            self.storage.append(value)

    @abc.abstractmethod
    def validate(self, value):
        """
        Abstract method for validate new property value
        Parameters
        ----------
        value :
            Validated value
        """


class MongoId():
    """
    Mongo Object Id validated element
    Methods
    ----------
    set collection(collection):
        set MongoDB collection name
    validate(value)
        Accept only str, int and ObjectId values
    """

    def set_collection(self, collection):
        """
        set reference to MongoDB collection
        Parameters
        ----------
        collection : pymongo.collection.Collection
            MongoDB collection reference
        """
        self.collection = collection

    def validate(self, value):
        """
            Accept only str, int and ObjectId values
        Parameters
        ----------
        value : 
            Validated value

        Returns
        -------
        bson.objectid.ObjectId
            Id of MongoDB record

        Raises
        ------
        TypeError
            Inserted value is not in proper type of ObjectId, str or int
        ValueError
            Inserted value is in set
        InvalidName
            In collection is not record with that ObjectId
        """
        if type(value) == ObjectId:
            result = self.collection.find({'_id': value})
        elif type(value) in [str, int]:
            object_id = ['0']*(24-len(str(value)))+list(str(value))
            value = ObjectId(''.join(object_id))
            result = self.collection.find(
                {'_id': ObjectId(''.join(object_id))})
        else:
            raise TypeError('value must be in type ObjectId, str or int')
        if len(list(result)):
            if not isinstance(self, collections.Iterable) or value not in list(self):
                return value
            raise ValueError(f'Value {value} is in set')
        raise InvalidName(f'There was no record with id: {value}')


class MongoIdList(MongoId, IterableStorage):
    """
        Iterable storage contained only ObjectId objects
    """
