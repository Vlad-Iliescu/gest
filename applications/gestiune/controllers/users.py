# coding: utf8
# try something like

def get_users():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not (ok):
            return dict(status=401, error="Sesiunea a expirat!")

    users = db(db.user.nivel < 5).select(db.user.id, db.user.username, db.user.nivel, db.user.nume,
                                         db.user.email).as_list()

    return dict(status=200, error="", users=users)


def delete_user():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.user_id:
        return dict(status=500, error="Id User nu exista")
    else:
        _user = db(db.user.id == request.post_vars.user_id).select().first()
        if not _user:
            return dict(status=500, error="User cu ID-ul '{0}' nu exista".format(request.post_vars.user_id))

    db(db.user.id == request.post_vars.user_id).delete()

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='user',
        contract='{0}'.format(request.post_vars.user_id),
        ip=request.env.remote_addr,
        action='Stergere User [{0}]'.format(_user.username),
        detalii='{0}'.format(
            dict(id=_user.id, username=_user.username, nivel=_user.nivel, nume=_user.nume, email=_user.email)),
        query=db(db.user.id == request.post_vars.user_id)._delete()
    )
    ###################################################

    return dict(status=200, error="")


def add_user():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!");
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.username:
        return dict(status=500, error="Username nu exista")

    if not request.post_vars.password:
        return dict(status=500, error="Password nu exista")

    if not request.post_vars.nivel:
        return dict(status=500, error="Nivel nu exista")

    if not request.post_vars.nume:
        nume = ""
    else:
        nume = request.post_vars.nume.title()

    if not request.post_vars.email:
        email = ""
    else:
        email = request.post_vars.email

    user_check = db(db.user.username == request.post_vars.username).select(db.user.id).first()

    if user_check:
        return dict(status=409, error="Userul {0} exista deja in baza de date!".format(request.post_vars.username))

    user_id = db.user.insert(username=request.post_vars.username, password=request.post_vars.password,
                             nivel=request.post_vars.nivel,
                             nume=nume, email=email)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='user',
        contract='{0}'.format(user_id),
        ip=request.env.remote_addr,
        action='Adaugare User [{0}]'.format(request.post_vars.username),
        detalii='{0}'.format(
            dict(id=user_id, username=request.post_vars.username, nivel=request.post_vars.nivel, nume=nume,
                 email=email)),
        query=db.user._insert(username=request.post_vars.username, password=request.post_vars.password,
                              nivel=request.post_vars.nivel,
                              nume=nume, email=email)
    )
    ###################################################

    return dict(status=200, error="")


def edit_user():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.username:
        return dict(status=500, error="Username nu exista")

    if not request.post_vars.nivel:
        return dict(status=500, error="Nivel nu exista")

    if not request.post_vars.user_id:
        return dict(status=500, error="Id User nu exista")
    else:
        _user = db(db.user.id == request.post_vars.user_id).select().first()

    if not request.post_vars.nume:
        nume = ""
    else:
        nume = request.post_vars.nume.title()

    if not (request.post_vars.email):
        email = ""
    else:
        email = request.post_vars.email

    user_check = db(
        (db.user.username == request.post_vars.username) & (db.user.id != request.post_vars.user_id)).select(
        db.user.id).first()

    if user_check:
        return dict(status=500, error="Userul {0} exista deja in baza de date!".format(request.post_vars.username))

    if not request.post_vars.password:
        db(db.user.id == request.post_vars.user_id).update(username=request.post_vars.username,
                                                           nivel=request.post_vars.nivel,
                                                           nume=nume, email=email)

        return dict(status=200, error="")

    db(db.user.id == request.post_vars.user_id).update(username=request.post_vars.username,
                                                       password=request.post_vars.password,
                                                       nivel=request.post_vars.nivel, nume=nume, email=email)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='user',
        contract='{0}'.format(request.post_vars.user_id),
        ip=request.env.remote_addr,
        action='Editare User [{0}]'.format(_user.username),
        detalii='{0}'.format(
            dict(id=request.post_vars.user_id, username=request.post_vars.username, nivel=request.post_vars.nivel,
                 nume=nume, email=email)),
        query=db(db.user.id == request.post_vars.user_id)._update(username=request.post_vars.username,
                                                                  password=request.post_vars.password,
                                                                  nivel=request.post_vars.nivel, nume=nume, email=email)
    )
    ###################################################

    return dict(status=200, error="")
