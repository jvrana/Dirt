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
