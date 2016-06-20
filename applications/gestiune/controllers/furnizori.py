# coding: utf8
# try something like
def index():
    return dict(message="hello from furnizori.py")


def get_furnizori():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!");
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    furnizori = db(db.furnizori.id > 0).select(db.furnizori.ALL, orderby=db.furnizori.denumire).as_list()

    return dict(status=200, error="", furnizori=furnizori)


def sterge_furnizor():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.furnizor_id:
        return dict(status=500, error="furnizor_id nu exista!")
    else:
        _furn = db(db.furnizori.id == request.post_vars.furnizor_id).select().first()
        if not _furn:
            return dict(status=500, error="Furnizorul cu ID-ul '{0}' nu exista!".format(request.post_vars.furnizor_id))

    db(db.furnizori.id == request.post_vars.furnizor_id).delete()

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='furnizori',
        contract='{0}'.format(_furn.id),
        ip=request.env.remote_addr,
        action='Stergere Furnizor [{0}]'.format(_furn.denumire),
        detalii='{0}'.format(dict(id=_furn.id, denumire=_furn.denumire)),
        query=db(db.furnizori.id == request.post_vars.furnizor_id)._delete()
    )
    ###################################################

    return dict(status=200, error="")


def add_furnizor():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.furnizor:
        return dict(status=500, error="Funizor nu exista!")
    else:
        _furnizor = db(db.furnizori.denumire.lower() == request.post_vars.furnizor.lower()).select().first()
        if _furnizor:
            return dict(status=409, error="Furnizorul '{0}' exista deja!".format(request.post_vars.furnizor))

    furnizor_id = db.furnizori.insert(denumire=request.post_vars.furnizor)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='furnizori',
        contract='{0}'.format(furnizor_id),
        ip=request.env.remote_addr,
        action='Adaugare Furnizor [{0}]'.format(request.post_vars.furnizor),
        detalii='{0}'.format(dict(id=furnizor_id, denumire=request.post_vars.furnizor)),
        query=db.furnizori._insert(denumire=request.post_vars.furnizor)
    )
    ###################################################       

    return dict(status=200, error="")


def edit_furnizor():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.furnizor_id:
        return dict(status=500, error="Furnizor_id nu exista!")
    else:
        _furn = db(db.furnizori.id == request.post_vars.furnizor_id).count()
        if not _furn:
            return dict(status=500, error="Furnizorul cu ID-ul '{0}' nu exista!".format(request.post_vars.furnizor_id))

    if not request.post_vars.furnizor:
        return dict(status=500, error="Funizor nu exista!")
    else:
        _furnizor = db(db.furnizori.denumire.lower() == request.post_vars.furnizor.lower()).count()
        if _furnizor:
            return dict(status=409, error="Furnizorul '{0}' exista deja!".format(request.post_vars.furnizor))

    db(db.furnizori.id == request.post_vars.furnizor_id).update(denumire=request.post_vars.furnizor)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='furnizori',
        contract='{0}'.format(request.post_vars.furnizor_id),
        ip=request.env.remote_addr,
        action='Editare Furnizor [{0}]'.format(request.post_vars.furnizor),
        detalii='{0}'.format(dict(id=request.post_vars.furnizor_id, denumire=request.post_vars.furnizor)),
        query=db(db.furnizori.id == request.post_vars.furnizor_id)._update(denumire=request.post_vars.furnizor)
    )
    ###################################################    

    return dict(status=200, error="")
