from typing import Callable, List

from py_flat_orm.domain.definition.orm_domain import OrmDomain
from py_flat_orm.domain.definition.orm_validate import OrmValidate
from py_flat_orm.domain.validation.orm_constraint import OrmConstraint
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector


class OrmConditionalValidate:
    def __init__(self, condition_is_met_fn: Callable[[OrmDomain], bool]):
        self.condition_is_met_fn = condition_is_met_fn

    def then(self, collector: OrmErrorCollector, field: str, constraints: List[OrmConstraint]) -> OrmErrorCollector:
        if not self.condition_is_met_fn(collector.domain):
            return collector
        return OrmValidate.with_rule(collector, field, constraints)
