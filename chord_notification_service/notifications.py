def notification_dict(notification) -> dict:
    return {
        "id": notification[0],
        "title": notification[1],
        "description": notification[2],
        "notification_type": notification[3],
        "action_target": notification[4],
        "read": bool(notification[5]),
        "timestamp": notification[6]
    }
