import json
from dataclasses import dataclass


@dataclass
class Offer:
    url: str
    name: str
    district: str
    description: str

    rent: int
    utilities: int
    rooms: int

    area: float

    @property
    def total_rent(self):
        return self.rent + self.utilities

    @property
    def total_rent_for_m2(self):
        return self.total_rent / self.area

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def __str__(self):
        return self.toJSON()

    def __hash__(self):
        return hash(self.url)
