from db import DB


class Admin:
    _db = DB("admins")

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self._save()

    def __init__(self, user_id):
        self.user_id = user_id
        self._load()

    def _save(self):
        self._db.insert({"user_id": self.user_id, "name": self.name})

    def _load(self):
        data = self._db.find_one({"user_id": self.user_id})
        self.name = data["name"]
