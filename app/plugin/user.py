from db import DB


class User:
    _db = DB("Users")

    def __init__(self, user_id, name):
        self.user_id: int = user_id
        self._name: str = name
        self._age: int = None
        self._gender: str = None
        self._faculty: str = None
        self._group: str = None
        self._type: str = None

        self._save()

    def __init__(self, user_id):
        self.user_id: int = user_id
        self._load()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.update_data()

        return self._name

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = value
        self.update_data()

        return self._age

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, value):
        self._gender = value
        self.update_data()

        return self._gender

    @property
    def faculty(self):
        return self._faculty

    @faculty.setter
    def faculty(self, value):
        self._faculty = value
        self.update_data()

        return self._faculty

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._group = value
        self.update_data()

        return self._group

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value
        self.update_data()

        return self._type

    def _into_json(self):
        return {
            "_id": self.user_id,
            "name": self._name,
            "age": self._age,
            "gender": self._gender,
            "faculty": self._faculty,
            "group": self._group,
            "type": self._type,
        }

    def update_data(self):
        self._db.update({"_id": self.user_id}, self._into_json())

    def _save(self):
        if not self._db.exist({"_id": self.user_id}):
            self._db.insert(self._into_json())
        else:
            self.update_data()

    def _load(self):
        if not self._db.exist({"_id": self.user_id}):
            return

        data = self._db.find_one({"_id": self.user_id})
        self._name = data["name"]
        self._age = data["age"]
        self._gender = data["gender"]
        self._faculty = data["faculty"]
        self._group = data["group"]
        self._type = data["type"]

    def __str__(self):
        text = [f"{var}: {vars(self)[var]}" for var in vars(self) if var]
        text = "\n".join(text)

        return text
