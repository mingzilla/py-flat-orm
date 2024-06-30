from typing import List, Callable, Any

from py_flat_orm.domain.validation.orm_constraint import OrmConstraint  # type: ignore
from py_flat_orm.domain.validation.orm_error_collector import OrmErrorCollector  # type: ignore
from py_flat_orm.domain.validation.orm_field_error import OrmFieldError  # type: ignore
from py_flat_orm.util.base_util.in_fn import InFn  # type: ignore
from .orm_domain import OrmDomain  # type: ignore


class OrmValidate:
    @staticmethod
    def with_rule(collector: OrmErrorCollector, field: str, constraints: List[OrmConstraint]) -> OrmErrorCollector:
        value = getattr(collector.domain, field, None)
        for constraint in constraints:
            OrmValidate.collect_error(collector, constraint, field, value)
        return collector

    @staticmethod
    def collect_error(collector: OrmErrorCollector, constraint: OrmConstraint, field: str, value: Any) -> OrmErrorCollector:
        if OrmConstraint.is_valid(constraint, value):
            return collector
        field_error = OrmFieldError.create(constraint, field, value)
        collector.add_error(field_error)
        return collector

    @staticmethod
    def if_having(field: str) -> 'OrmConditionalValidate':
        def condition_is_met_fn(domain: OrmDomain) -> bool:
            value = InFn.prop_as_string(field, domain)
            return InFn.is_not_blank(value)

        return OrmConditionalValidate(condition_is_met_fn)

    @staticmethod
    def if_not_having(field: str) -> 'OrmConditionalValidate':
        def condition_is_met_fn(domain: OrmDomain) -> bool:
            value = InFn.prop_as_string(field, domain)
            return InFn.is_blank(value)

        return OrmConditionalValidate(condition_is_met_fn)

    @staticmethod
    def if_satisfies(condition_is_met_fn: Callable[[OrmDomain], bool]) -> 'OrmConditionalValidate':
        return OrmConditionalValidate(condition_is_met_fn)


class OrmConditionalValidate:
    def __init__(self, condition_is_met_fn: Callable[[OrmDomain], bool]):
        self.condition_is_met_fn = condition_is_met_fn

    def then(self, collector: OrmErrorCollector, field: str, constraints: List[OrmConstraint]) -> OrmErrorCollector:
        try:
            is_met = self.condition_is_met_fn(collector.domain)
        except TypeError: # occurs when comparing None and int
            is_met = False

        if not is_met:
            return collector
        return OrmValidate.with_rule(collector, field, constraints)
