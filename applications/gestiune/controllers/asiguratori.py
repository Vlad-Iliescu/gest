# coding: utf8

def get_asiguratori():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    asiguratori = db().select(
        db.asigurator.id, db.asigurator.denumire, db.asigurator.tip, orderby=db.asigurator.denumire).as_list()

    return dict(status=200, error="", asiguratori=asiguratori)


def sterge_asigurator():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.asigurator_id:
        return dict(status=500, error="Asigurator ID nu exista!")
    else:
        _asig = db(db.asigurator.id == request.post_vars.asigurator_id).select().first()
        if not _asig:
            return dict(status=500,
                        error="Asiguratorul cu ID-ul '{0}' nu exista!".format(request.post_vars.asigurator_id))

    db(db.asigurator.id == request.post_vars.asigurator_id).delete()

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='asigurator',
        contract='{0}'.format(_asig.id),
        ip=request.env.remote_addr,
        action='Stergere Asigurator [{0}]'.format(_asig.denumire),
        detalii='{0}'.format(dict(id=_asig.id, denumire=_asig.denumire, tip=_asig.tip)),
        query=db(db.asigurator.id == request.post_vars.asigurator_id)._delete()
    )
    ###################################################

    return dict(status=200, error="")


def add_asigurator():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.asigurator:
        return dict(status=500, error="Asigurator nu exista!")
    else:
        _asig = db(db.asigurator.denumire.lower() == request.post_vars.asigurator.lower()).count()
        if _asig:
            return dict(status=409, error="Asiguratorul '{0}' exista deja!".format(request.post_vars.asigurator))

    if not request.post_vars.tip:
        return dict(status=500, error="Tip nu exista!")

    id_asig = db.asigurator.insert(denumire=request.post_vars.asigurator, tip=request.post_vars.tip)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='asigurator',
        contract='{0}'.format(id_asig),
        ip=request.env.remote_addr,
        action='Adaugare Asigurator [{0}]'.format(request.post_vars.asigurator),
        detalii='{0}'.format(dict(id=id_asig, denumire=request.post_vars.asigurator, tip=request.post_vars.tip)),
        query=db.asigurator._insert(denumire=request.post_vars.asigurator, tip=request.post_vars.tip)
        )
    ###################################################

    return dict(status=200, error="")


def edit_asigurator():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.asigurator_id:
        return dict(status=500, error="Asigurator ID nu exista")
    else:
        _asig = db(db.asigurator.id == request.post_vars.asigurator_id).select().first()
        if not _asig:
            return dict(status=500,
                        error="Asiguratorul cu ID-ul '{0}' nu exista!".format(request.post_vars.asigurator_id))

    if not request.post_vars.asigurator:
        return dict(status=500, error="Asigurator nu exista!")
    else:
        _asigurator = db(db.asigurator.denumire.lower() == request.post_vars.asigurator.lower()).count()
        if _asigurator:
            return dict(status=409, error="Asiguratorul '{0}' exista deja!".format(request.post_vars.asigurator))

    if not request.post_vars.tip:
        return dict(status=500, error="Tip nu exista!")

    db(db.asigurator.id == request.post_vars.asigurator_id).update(denumire=request.post_vars.asigurator,
                                                                   tip=request.post_vars.tip)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='asigurator',
        contract='{0}'.format(_asig.id),
        ip=request.env.remote_addr,
        action='Editare Asigurator [{0}]'.format(_asig.denumire),
        detalii='{0}'.format(dict(id=_asig.id, denumire=request.post_vars.asigurator, tip=request.post_vars.tip)),
        query=db(db.asigurator.id == request.post_vars.asigurator_id)._update(denumire=request.post_vars.asigurator,
                                                                              tip=request.post_vars.tip)
    )
    ###################################################

    return dict(status=200, error="")
