import json

from openlineage.prefect.executor import track_lineage
from openlineage.prefect.test_utils import RESOURCES
from prefect import  flow, task,task_runners
from prefect.task_runners import SequentialTaskRunner,ConcurrentTaskRunner

task_runners.SequentialTaskRunner = track_lineage(SequentialTaskRunner)
task_runners.ConcurrentTaskRunner = track_lineage(ConcurrentTaskRunner)


@task()
def get(n):
    """
    Get a json file
    """
    filename = f"{RESOURCES}/{n}.json"
    return json.loads(open(filename).read())


@task()
def inc(g, y=1):
    return g + y


@task()
def multiply(i):
    """
    Multiple the value
    """
    return i * 2


@task()
def non_data_task(m):
    return


@task()
def error_task():
    raise ValueError("custom-error-message")


@flow()
def simple_flow(p: str):
    g = get(p)
    i = inc(g)
    m = multiply(i)
    non_data_task(m)


@flow()
def error_flow():
    return error_task()
