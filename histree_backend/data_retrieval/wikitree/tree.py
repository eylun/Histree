from abc import abstractmethod
from json import JSONDecodeError
from typing import Dict, List, Tuple
from qwikidata.sparql import return_sparql_query_results
from data_retrieval.query.builder import SPARQLBuilder
from histree_backend.data_retrieval.query.parser import WikiResult
from .flower import WikiFlower, WikiPetal, WikiStem


class WikiSeed:
    def __init__(self, up_stem: WikiStem, down_stem: WikiStem, petals: List[WikiPetal]):
        self.petal_map = {petal.label: petal for petal in petals}
        self.up_stem, self.down_stem = up_stem, down_stem

        _headers = dict(petal.to_dict_pair() for petal in petals)
        self.up_stem.set_query_template(_headers)
        self.down_stem.set_query_template(_headers)

        _TEMPLATE_STR = "%s"
        self.info_query_template = (
            SPARQLBuilder(_headers).bounded_to("?item", f"wd:{_TEMPLATE_STR}").build()
        )

    def branch_up(self, id: str, tree: "WikiTree") -> List[WikiFlower]:
        # Query for parents
        result = tree.api.query(self.up_stem.get_query(id))
        parents = WikiResult(result).parse(self.petal_map)

        # Store parents in tree
        for parent in parents:
            tree.flowers[parent.id] = parent

            if parent.id not in tree.branches:
                tree.branches[parent.id] = set()
            tree.branches[parent.id].add(id)

        return parents

    def branch_down(self, id: str, tree: "WikiTree") -> List[WikiFlower]:
        result = tree.api.query(self.down_stem.get_query(id))
        children = WikiResult(result).parse(self.petal_map)

        if children and id not in tree.branches:
            tree.branches[id] = set()

        for child in children:
            tree.flowers[child.id] = child
            tree.branches[id].add(child.id)

        return children

    def sprout(self, id: str, tree: "WikiTree") -> WikiFlower:
        result = tree.api.query(self.info_query_template % id)
        flowers = WikiResult(result).parse(self.petal_map)

        if not flowers:
            return None

        flower = flowers[0]
        tree.flowers[flower.id] = flower

        return flower


class WikiAPI:
    @abstractmethod
    def query(self, query_string: str) -> Dict[str, any]:
        pass


class WikidataAPI(WikiAPI):
    _instance = None

    def query(self, query_string: str) -> Dict[str, any]:
        try:
            response = return_sparql_query_results(query_string)
        except JSONDecodeError:
            response = dict()
        return response

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class WikiTree:
    def __init__(self, seed: WikiSeed, api: WikiAPI = WikidataAPI.instance()):
        self.seed = seed
        self.flowers = dict()
        self.branches = dict()
        self.api = api

    def grow(
        self,
        id: str,
        branch_up: bool = True,
        branch_down: bool = True,
    ) -> Tuple[List[WikiFlower], List[WikiFlower]]:
        if (
            id in self.flowers
            and (not branch_up or self.flowers[id].branched_up)
            and (not branch_down or self.flowers[id].branched_down)
        ):
            return None, None

        if id not in self.flowers:
            self.seed.sprout(id, self)
        flower = self.flowers[id]

        # Branch off from the flower to find immediate nearby flowers
        flowers_above, flowers_below = None, None
        if branch_up and not flower.branched_up:
            flowers_above = self.seed.branch_up(id, self)
            flower.branched_up = True
        if branch_down and not flower.branched_down:
            flowers_below = self.seed.branch_down(id, self)
            flower.branched_down = True
        return flowers_above, flowers_below

    def grow_levels(
        self, id: str, branch_up_levels: int, branch_down_levels: int
    ) -> None:
        above, below = self.grow(
            id,
            branch_up_levels > 0,
            branch_down_levels > 0,
        )
        if above:
            for flower in above:
                self.grow_levels(flower.id, branch_up_levels - 1, 0)
        if below:
            for flower in below:
                # Grow upwards once to find other parent.
                self.grow_levels(flower.id, 1, branch_down_levels - 1)

    def to_json(self) -> Dict[str, any]:
        return {
            "flowers": [flower.to_json() for flower in self.flowers.values()],
            "branches": {id: list(adj_set) for (id, adj_set) in self.branches.items()},
        }
