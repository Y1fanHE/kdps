'''
Author: He,Yifan
Date: 2022-02-16 20:07:17
LastEditors: He,Yifan
LastEditTime: 2022-02-18 16:44:07
'''


from pgsyn.gp.algorithms.base import SearchAlgorithm
from pgsyn.utils import instantiate_using

from pgsyn.gp.algorithms.umad import UMAD
from pgsyn.gp.algorithms.umadr import UMADR


def get_search_algo(name: str, **kwargs) -> SearchAlgorithm:
    """Return the search algorithm class with the given name."""
    name_to_cls = {
        "UMAD": UMAD,
        "UMADR": UMADR
    }
    _cls = name_to_cls.get(name, None)
    if _cls is None:
        raise ValueError("No search algorithm '{nm}'. Supported names: {lst}.".format(
            nm=name,
            lst=list(name_to_cls.keys())
        ))
    return instantiate_using(_cls, kwargs)


__all__ = ["get_search_algo"]
