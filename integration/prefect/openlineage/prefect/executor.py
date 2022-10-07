from functools import partial
from typing import Any, Awaitable, Callable, Dict, Optional

from uuid import UUID


from openlineage.prefect.adapter import OpenLineageAdapter
from prefect.futures import PrefectFuture
from prefect.orion.schemas.core import TaskRun
from prefect.orion.schemas.states import State, StateType
from prefect.task_runners import BaseTaskRunner, R

#  task=task,
# task_run=task_run,
# parameters=parameters,
# wait_for=wait_for,
# result_filesystem=flow_run_context.result_filesystem,
# settings=prefect.context.SettingsContext.get().copy(),

def parse_task_inputs(inputs: Dict):
    def _parse_task_input(x):
        # TODO - need to look up TaskRunResult output DataDocument
        return x

    return {k: _parse_task_input(v) for k, v in inputs.items()}


def on_submit(method, adapter: OpenLineageAdapter):
    async def inner(
        self: BaseTaskRunner,
        key: UUID,
        call: Callable[..., Awaitable[State[R]]],
    ) -> PrefectFuture:
        parital_call: partial = call
        keywords = parital_call.keywords
        task = keywords["task"]
        task_run = keywords["task_run"]
        parameters : Dict[str, Any] = keywords["parameters"]
  
        future = await method(self=self, key=key, call=call)
        
        adapter.start_task(task=task, task_run=task_run, run_kwargs=parameters)
        return future

    return inner


def on_wait(method, adapter: OpenLineageAdapter):
    async def inner(self:BaseTaskRunner,  *args, **kwargs) -> Optional[State]:
        state: Optional[State] = await method(self=self, *args, **kwargs)
        if state:
            if state.type == StateType.COMPLETED:
                adapter.complete_task(state=state)
            elif state.type == StateType.FAILED:
                adapter.fail_task(state=state)
        return state

    return inner


def track_lineage(cls: BaseTaskRunner, open_lineage_url: Optional[str] = None):
    adapter = OpenLineageAdapter()

    cls.submit = on_submit(cls.submit, adapter=adapter)
    cls.wait = on_wait(cls.wait, adapter=adapter)
    return cls
