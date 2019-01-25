from copy import deepcopy

from pydent.base import ModelRegistry
from pydent.browser import Browser

from dirtio.utils import cache_plans

import networkx as nx

def _get_browser(browser=None, session=None):
    if browser is None:
        if session is None:
            return Exception("Cannot resolve query. Must provide with 'session' or 'browser' arguments")
        return Browser(session)
    return browser

def resolve_query(query, include=None, browser=None, session=None, query_only=False):
    """
    Resolves a Dirt.io query object

    :param query:
    :type query: dict
    :param include:
    :type include: dict
    :param browser:
    :type browser: Browser
    :param session:
    :type session: AqSession
    :param query_only: If True, returns the final query only
    :type query_only: bool
    :return:
    :rtype:
    """
    browser = _get_browser(browser, session)

    if include is None:
        include = dict()
    if isinstance(query, list):
        return [resolve_query(q, browser=browser) for q in query]
    q = deepcopy(query)

    typename = q.pop("__typename", None)
    if typename is None:
        raise TypeError("Could not find __typename for {}".format(q))
    attributes = q

    model = ModelRegistry.get_model(typename)
    relationships = model.get_relationships()

    filtered_query = {}

    for k, v in attributes.items():
        if isinstance(v, dict):
            nested_model = resolve_query(v, browser=browser)
            if not nested_model:
                return list()
            elif len(nested_model) > 1:
                raise TypeError("More than one nested model found.")
            nested_model = nested_model[0]
            if k in relationships:
                relation = relationships.get(k)
                assert relation.nested == v['__typename']
                assert not relation.many
                include[relation.data_key] = dict()


                filtered_query[relation.ref] = getattr(nested_model, relation.attr)
        else:
            filtered_query[k] = v
    if query_only:
        return filtered_query
    if filtered_query:
        models = browser.where(filtered_query, model_class=typename)
        return models
    return list()


def resolve_model(model, query, session=None, browser=None, with_reason=False):
    filtered_query = resolve_query(query, session=session, browser=browser, query_only=True)
    # filtered_query = query
    model_type = ModelRegistry.get_model(query['__typename'])
    passes = {"passes": True, "reasons": []}
    if not issubclass(type(model), model_type):
        passes['passes'] = False
        passes['reasons'].append("'{}' is not the __typename '{}'"
                                 " specified in the query".format(type(model), query['__typename']))
    for k, v in filtered_query.items():
        if hasattr(model, k) and v != getattr(model, k):
            passes['passes'] = False
            passes['reasons'].append("model.{}={}, but was supposed to be {}".format(k, getattr(model, k), v))
    if with_reason:
        return passes
    else:
        return passes['passes']


def filter_models(models, query, browser=None, session=None):
    browser = _get_browser(browser, session)
    return [m for m in models if resolve_model(m, query, session=session, browser=browser)]


def resolve_event(session, plan_ids, event_name, event_query):
    event_query = deepcopy(event_query)

    plans = cache_plans(session, plan_ids)
    _browser = plans[0]._browser

    start_query = event_query.pop("__START")
    end_query = event_query.pop("__END")

    resolve_query(event_query["__START"], browser=_browser)
    resolve_query(event_query["__END"], browser=_browser)

    # search for subgraph
    for plan in plans:
        G = plan.layout.G
        for nid in G.nodes:
            node = G.nodes[nid]
            op = node['operation']


def _from_g(g, nid, k):
    return g.nodes[nid][k]

def resolve_subgraph(opgraph, start_query, end_query, browser, depth=None):
    # search for subgraph
    G = opgraph
    connections = {}

    allops = [_from_g(G, nid, 'operation') for nid in opgraph.nodes]
    browser.recursive_retrieve(allops, start_query, strict=False)
    browser.recursive_retrieve(allops, end_query, strict=False)

    # filtered_start_query = resolve_query(start_query, session=None, browser=browser, query_only=True)
    # filtered_end_query = resolve_query(end_query, session=None, browser=browser, query_only=True)

    starts = filter_models(allops, start_query, browser=browser)
    ends = filter_models(allops, end_query, browser=browser)

    for op in starts:
        nid = op.id
        connections[nid] = []
        for _, next_nids in nx.bfs_successors(G, nid, depth_limit=depth):
            next_nids = set(next_nids).intersection(set(e.id for e in ends))
            ops = [_from_g(G, _nid, 'operation') for _nid in next_nids]
            connections[nid] += [_op.id for _op in ops]
    return connections


