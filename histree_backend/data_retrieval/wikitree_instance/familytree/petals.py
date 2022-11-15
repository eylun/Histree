from data_retrieval.wikitree.flower import WikiPetal
from data_retrieval.wikitree_instance.familytree.property import PROPERTY_MAP


class GenderPetal(WikiPetal):
    gender_map = {
        "Q6581097": "male",
        "Q6581072": "female",
        "Q48270": "non-binary",
        "Q1097630": "intersex",
        "Q2449503": "transgender male",
        "Q1052281": "transgender female",
        "Q505371": "agender",
    }

    def __init__(self):
        label = "gender"
        super().__init__(PROPERTY_MAP["petals"][label], label, True, False)

    def parse(self, value: str) -> str:
        id = value.split("/")[-1]
        return self.gender_map.get(id, self.undefined)


class DatePetal(WikiPetal):
    def __init__(self, id, label):
        super().__init__(id, label, True, False)

    def parse(self, value: str) -> str:
        if not value:
            return self.undefined
        return value[1:].split("T")[0]


class BirthDatePetal(DatePetal):
    def __init__(self):
        label = "date_of_birth"
        super().__init__(PROPERTY_MAP["petals"][label], label)


class DeathDatePetal(DatePetal):
    def __init__(self):
        label = "date_of_death"
        super().__init__(PROPERTY_MAP["petals"][label], label)


class BirthNamePetal(WikiPetal):
    def __init__(self):
        label = "birth_name"
        super().__init__(PROPERTY_MAP["petals"][label], label, True, True)

    def parse(self, value: str) -> str:
        return value


class ImagePetal(WikiPetal):
    def __init__(self):
        label = "image"
        super().__init__(PROPERTY_MAP["petals"][label], label, True, True)

    def parse(self, value: str) -> str:
        return value
