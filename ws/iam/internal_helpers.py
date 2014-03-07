from flask import request, abort


def ensure_allowed(action, resource):
    """Ensure a permission (or abort with 403) using the WS context stored in the request."""
    if hasattr(request, 'ws_session'):
        user_id = request.ws_session.user_id
        session_id = request.ws_session.session_id

        json, status_code = check_permission_action_internal(session_id, action, resource, user_id)

        if status_code != 200:
            abort(403)

        if not json.get('allowed', False):
            abort(403)


from app import check_permission_action_internal