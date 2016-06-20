# coding: utf8
# try something like

def get_logs():
    '''
    >>> 1
    1
    '''
    if not request.post_vars.user_hash:
        return dict(status=False, error="Hash nu exista!");
    else:
        ok, user_id, username = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=False, error="Sesiunea a expirat!")
    if not request.post_vars.user_id:
        return dict(status=False, error="Id User nu exista!")

    logs = db(db.user_logs.user_id == request.post_vars.user_id).select(db.user_logs.id, db.user_logs.ip,
                                                                        db.user_logs.date_added, db.user_logs.activity,
                                                                        orderby=~db.user_logs.date_added).as_list()
    rows = db(db.user_logs.user_id == request.post_vars.user_id).select(db.user_logs.id.count())[0]._extra(
        db.user_logs.id.count())
    return dict(status=True, error="", rows=rows, logs=logs)
