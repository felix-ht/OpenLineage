import attr
import prefect
from openlineage.client.facet import BaseFacet
from openlineage.prefect.util import task_qualified_name
from prefect._version import get_versions
from prefect.tasks import Task
from prefect.context import get_run_context

@attr.s
class PrefectRunFacet(BaseFacet):
    task: str = attr.ib()
    prefect_version: str = attr.ib()
    prefect_commit: str = attr.ib()
    prefect_backend: str = attr.ib()
    openlineage_prefect_version: str = attr.ib()

    @classmethod
    def from_task(cls, task: Task):
        from openlineage.prefect.adapter import OPENLINEAGE_PREFECT_VERSION

        version = get_versions()
        return cls(
            task=task_qualified_name(task),
            prefect_version=version["version"],
            prefect_commit=version["full-revisionid"],
            prefect_backend="todo",
            openlineage_prefect_version=OPENLINEAGE_PREFECT_VERSION,
        )
