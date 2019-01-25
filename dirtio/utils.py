from pydent.browser import Browser
from pydent.planner import Planner


def cache_plans(session, plan_ids):
    browser = Browser(session)
    plans = browser.where({"id": plan_ids}, model_class="Plan")
    planner_instances = []
    Planner.cache_plans(browser, plans)
    for plan in plans:
        planner = Planner.__new__(Planner)
        planner.session = plan.session
        planner._browser = browser
        planner.plan = plan
        planner_instances.append(planner)

    return planner_instances


def dictionary_contains(d1, d2):
    # check that every key:value in d2 is in d1

    for k2, v2 in d2.items():
        if k2 not in d1:
            return False
        elif not issubclass(type(d1[k2]), type(v2)):
            return False
        elif not isinstance(v2, dict) and d1[k2] != v2:
            return False
    for k2, v2 in d2.items():
        if isinstance(v2, dict):
            n1 = d1[k2]
            n2 = v2
            r = dictionary_contains(n1, n2)
            if not r:
                return False
    return True
