import pytest
from dirtio import resolve_query, resolve_model, cache_plans, resolve_event, resolve_subgraph

class TestResolveQuery(object):

    def test_basic_nested(self, browser):
        query = {
            "__typename": "Operation",
            "operation_type": {
                "__typename": "OperationType",
                "name": "Check Yeast Plate",
                "deployed": True,
            },
            "status": "waiting"
        }

        models = resolve_query(query, browser=browser)
        for m in models:
            assert m.operation_type.name == 'Check Yeast Plate'
        assert len(models) > 1


class TestResolveModel(object):
    check_plate = {
        "__typename": "Operation",
        "operation_type": {
            "__typename": "OperationType",
            "name": "Check Yeast Plate",
            "deployed": True,
        },
        "status": "waiting"
    }

    fragment_analyzing = {
        "__typename": "Operation",
        "operation_type": {
            "__typename": "OperationType",
            "name": "Fragment Analyzing",
            "deployed": True,
        }
    }

    def test_basic(self, browser):
        ops1 = resolve_query(self.check_plate, browser=browser)
        ops2 = resolve_query(self.fragment_analyzing, browser=browser)

        assert resolve_model(ops1[0], self.check_plate, browser=browser)
        assert not resolve_model(ops2[0], self.check_plate, browser=browser)

        assert resolve_model(ops2[0], self.fragment_analyzing, browser=browser)
        assert not resolve_model(ops1[0], self.fragment_analyzing, browser=browser)

        print(resolve_model(ops1[0], self.fragment_analyzing, browser=browser, with_reason=True))


class TestEvent(object):

    check_plate = {
        "__typename": "Operation",
        "operation_type": {
            "__typename": "OperationType",
            "name": "Check Yeast Plate",
            "deployed": True,
        },
        "status": "waiting"
    }

    fragment_analyzing = {
        "__typename": "Operation",
        "operation_type": {
            "__typename": "OperationType",
            "name": "Fragment Analyzing",
            "deployed": True,
        }
    }

    def test_basic(self, session):
        session.set_verbose(True)
        plans = cache_plans(session, [30380])
        browser = plans[0]._browser
        start = self.check_plate
        end = self.fragment_analyzing
        G = plans[0].layout.G

        browser.set_verbose(True)
        results = resolve_subgraph(G, start, end, browser)
        print(results)