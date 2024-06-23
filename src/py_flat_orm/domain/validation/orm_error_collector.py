from typing import List, Dict, Any


class OrmErrorCollector:
    def __init__(self, domain: 'OrmDomain'):
        self.domain = domain
        self.fields: Dict[str, OrmFieldErrors] = {}

    @staticmethod
    def create(domain: 'OrmDomain') -> 'OrmErrorCollector':
        return OrmErrorCollector(domain)

    def add_error(self, field_error: OrmFieldError) -> None:
        field = field_error.field
        if field not in self.fields:
            self.fields[field] = OrmFieldErrors.create(field)
        self.fields[field].add_error(field_error)

    def has_errors(self) -> bool:
        return any(field_errors.has_errors() for field_errors in self.fields.values())

    @staticmethod
    def have_errors(collectors: List[List['OrmErrorCollector']]) -> bool:
        flattened_collectors = [collector for sublist in collectors for collector in sublist]
        return any(collector.has_errors() for collector in flattened_collectors if collector)

    @staticmethod
    def to_error_maps(collectors: List['OrmErrorCollector']) -> List[Dict[str, List[Dict]]]:
        item_with_errors = [collector for collector in collectors if collector and collector.has_errors()]
        return [collector.to_map() for collector in item_with_errors]

    def to_map(self) -> Dict[str, List[Dict[str, Any]]]:
        return {field: [error.to_dict() for error in field_errors.errors] for field, field_errors in self.fields.items()}

# Example implementation of the OrmDomain class.
class OrmDomain:
    pass
