from typing import Any, Dict, TypeVar

from .in_fn import InFn

T = TypeVar('T')


class DomainUtil:

    @staticmethod
    def merge_fields(obj: T, new_props: Dict[str, Any]) -> T:
        """
        Basic type includes: int, Integer, boolean, Boolean, String, Date
        String is trimToEmpty. Domain objects are supposed to be saved to db, A value should not just have empty space or space around.
        However, this doesn't do trimToNull for compatibility purposes. When working on existing bad code, trimToEmpty wouldn't make it hard for those devs.
        """
        new_props = new_props or {}
        relevant_props = {}

        for k, v in new_props.items():
            if hasattr(obj, k):
                relevant_props[k] = v

        for k, v in relevant_props.items():
            obj = InFn.set_primitive_field(obj, k, InFn.trim_to_empty_if_is_string(v))

        return obj

    @staticmethod
    def merge_request_data(obj: T, resolved_props: Dict[str, Any], unmodified_client_submitted_props: Dict[str, Any]) -> T:
        """
        Merge data submitted from the client side to the server side, which allows submitting only a single field to update one field using the API, without having to submit every single field.

        Used by Domain.mergeData(), so that setting data is consistently handled.
        This develops a consistent procedure, so that devs don't need to always consider if they need to use
        - e.g.`this.myField = myField` - set the value without fallback
        - or`this.myField = myField ?: this.myField` - picks up the db value if value supplied is null

        Scenarios:
        - if user intentionally sets value x, and resolved as x, use x
        - if user intentionally sets value x, and resolved as y, use y
        - if user intentionally sets value null, and resolved as y, use y
        - if user intentionally sets value null, and resolved as null, use null
        - if user does not submit field (no intent to change), and resolved as null (because a variable is created to process the logic), use db value
          - mostly occurs when using the API to update without supplying every single field
        """
        new_props = {}

        for k, v in resolved_props.items():
            client_sends_key = k in unmodified_client_submitted_props
            client_sets_null = unmodified_client_submitted_props.get(k) is None
            server_sets_value = v is not None
            has_field_and_set_to_null = client_sends_key and client_sets_null

            if server_sets_value:
                new_props[k] = v
            elif has_field_and_set_to_null:
                new_props[k] = None
            else:
                db_value = getattr(obj, k)
                new_props[k] = db_value

        return DomainUtil.merge_fields(obj, new_props)
