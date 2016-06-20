# coding: utf8

def index():
    return dict(message="hello from contracte.py")


def add_contract():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!");
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    fields = dict(user_id=user_id, date_added=request.now)

    if not request.post_vars.contract:
        return dict(status=500, error="Contract nu exista")
    else:
        _cont = db(db.contracte.contract == request.post_vars.contract).select(db.contracte.id).first()
        if _cont:
            return dict(status=409, error="Contractul {0} exista in baza".format(request.post_vars.contract),
                        contract_id=_cont.id)
        fields["contract"] = request.post_vars.contract

    if not request.post_vars.auto:
        return dict(status=500, error="Auto nu exista!")
    else:
        fields["auto"] = request.post_vars.auto

    if request.post_vars.numar_auto:
        fields["numar_auto"] = request.post_vars.numar_auto

    if not request.post_vars.contactat:
        return dict(status=500, error="Contactat nu exista!")
    else:
        if str(request.post_vars.contactat) == str(1):
            fields["contactat"] = True
        else:
            fields["contactat"] = False

    if not request.post_vars.consilier_id:
        return dict(status=500, error="Consilier_id nu exista!")
    else:
        fields["consilier_id"] = request.post_vars.consilier_id

    if request.post_vars.programare:
        fields["programare"] = datetime.datetime.strptime(request.post_vars.programare, '%d.%m.%Y %H:%M:%S')

    if request.post_vars.observatii:
        fields["observatii"] = request.post_vars.observatii

    contract_id = db.contracte.insert(**fields)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='contracte',
        contract='{0}'.format(request.post_vars.contract),
        ip=request.env.remote_addr,
        action='Adaugare Contract [{0}]'.format(request.post_vars.contract),
        detalii='{0}'.format(fields),
        query=db.contracte._insert(**fields)
    )
    ##################################################

    return dict(status=200, error="", contract_id=contract_id)


def get_contracte_finalizate():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    tva = TVA()

    contracte = db.executesql("""
        SELECT 
          contracte.id,
          contracte.contract,
          contracte.auto,
          contracte.numar_auto,
          contracte.date_added,
          contracte.user_id,
          contracte.consilier_id,
          contracte.programare,
          contracte.contactat,
          contracte.observatii,
          contracte.stare,
          contracte.motiv,
          COALESCE(SUM(ROUND((linii.pret_vanzare * (1 + {0:.2f})) * linii.cantitate,2)),0.00) AS total ,
          IF(SUM(IF(linii.stare = 4, 1,0)) = SUM(IF(linii.comanda = 'T',1,0)) AND SUM(IF(linii.comanda = 'T',1,0)) <> 0, 'T','F') AS rezolvat
        FROM
          contracte 
          LEFT JOIN linii 
            ON (contracte.id = linii.contract_id) 
        WHERE (contracte.finalizat = 'T') 
        GROUP BY contracte.id,
          contracte.contract,
          contracte.auto,
          contracte.numar_auto,
          contracte.date_added,
          contracte.user_id,
          contracte.consilier_id,
          contracte.programare,
          contracte.contactat,
          contracte.observatii,
          contracte.stare 
        ORDER BY contracte.date_added;""".format(tva / 100.0), as_dict=True)

    users = db().select(db.user.id, db.user.nume).as_list()

    return dict(status=200, error="", contracte=contracte, users=users, TVA=tva)


def get_contracte():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    tva = TVA()

    contracte = db.executesql("""
        SELECT 
          contracte.id,
          contracte.contract,
          contracte.auto,
          contracte.numar_auto,
          contracte.date_added,
          contracte.user_id,
          contracte.consilier_id,
          contracte.programare,
          contracte.contactat,
          contracte.observatii,
          contracte.stare,
          COALESCE(SUM(ROUND((linii.pret_vanzare * (1 + {0:.2f})) * linii.cantitate,2)),0.00) AS total ,
          IF(SUM(IF(linii.stare = 4, 1,0)) = SUM(IF(linii.comanda = 'T',1,0)) AND SUM(IF(linii.comanda = 'T',1,0)) <> 0, 'T','F') AS rezolvat
        FROM
          contracte 
          LEFT JOIN linii 
            ON (contracte.id = linii.contract_id) 
        WHERE (contracte.finalizat = 'F') 
        GROUP BY contracte.id,
          contracte.contract,
          contracte.auto,
          contracte.numar_auto,
          contracte.date_added,
          contracte.user_id,
          contracte.consilier_id,
          contracte.programare,
          contracte.contactat,
          contracte.observatii,
          contracte.stare 
        ORDER BY contracte.date_added;""".format(tva / 100.0), as_dict=True)

    users = db().select(db.user.id, db.user.nume).as_list()

    return dict(status=200, error="", contracte=contracte, users=users, TVA=tva)


def get_contract():
    """
    >>> request.post_vars.user_hash = '11cb288188af4db6ea9007729c852294'
    >>> request.post_vars.contract_id = 1
    >>> get_contract()
    """
    # log(request.vars)

    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.contract_id:
        return dict(status=500, error="Contractul nu exista!")

    furnizori = db().select(db.furnizori.denumire, cache=(cache.ram, 36000), orderby=db.furnizori.denumire).as_list()
    asiguratori = db().select(db.asigurator.denumire, db.asigurator.tip, cache=(cache.ram, 36000),
                              orderby=db.asigurator.denumire).as_list()
    consilieri = db(db.user.nivel.belongs([2, 5])).select(db.user.id, db.user.nume, cache=(cache.ram, 36000),
                                                          orderby=~db.user.nivel).as_list()

    contract = db(db.contracte.id == request.post_vars.contract_id).select().as_list()
    if not (len(contract)):
        return dict(status=500, error="Contractul nu exista!")

    linii = db(db.linii.contract_id == request.post_vars.contract_id)(db.linii.sters == False).select().as_list()

    users = dict()
    _users = db().select(db.user.id, db.user.nume, cache=(cache.ram, 36000))
    for i in _users:
        users[i.id] = i.nume

    user_id = contract[0].get('user_id', None)

    if user_id:
        user = users.get(user_id, 'Necunoscut')
    else:
        user = 'Necunoscut'

    return dict(status=200, error="", furnizori=furnizori, asiguratori=asiguratori, user=user,
                contract=contract[0], linii=linii, consilieri=consilieri, TVA=TVA(), data=request.now,
                users=_users.as_list())


def edit_contract():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.contract_id:
        return dict(status=500, error="Contractul nu exista!")

    fields = dict()

    if request.post_vars.contract:
        fields['contract'] = request.post_vars.contract

    if request.post_vars.auto:
        fields['auto'] = request.post_vars.auto

    if request.post_vars.numar_auto:
        fields['numar_auto'] = request.post_vars.numar_auto

    if request.post_vars.contactat:
        if request.post_vars.contactat == 1:
            fields['contactat'] = True
        else:
            fields['contactat'] = False

    if request.post_vars.programare:
        fields["programare"] = datetime.datetime.strptime(request.post_vars.programare, '%d.%m.%Y %H:%M:%S')

    import json

    if request.post_vars.linii:
        # log(request.post_vars.linii)
        linii = json.loads(request.post_vars.linii)
        if not (linii) or not (len(linii.get('insert', [])) + len(linii.get('update', []))):
            return dict(status=500, error="Contractul nu poate fi gol!")
    else:
        return dict(status=500, error="Contractul nu poate fi gol!")

    db(db.contracte.id == request.post_vars.contract_id).update(**fields)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='contracte',
        contract='{0}'.format(request.post_vars.contract),
        ip=request.env.remote_addr,
        action='Editare Contract [{0}]'.format(request.post_vars.contract),
        detalii='{0}'.format(fields),
        query=db(db.contracte.id == request.post_vars.contract_id)._update(**fields)
    )
    ##################################################

    query = ''
    detalii = dict(insert=[], update=[], delete=[])

    if len(linii.get('insert', [])):
        for linie in linii.get('insert', []):
            linie['user_id'] = user_id
            linie['contract_id'] = request.post_vars.contract_id
            linie['date_added'] = request.now

            if linie.get('asigurator', False) and linie['asigurator'] == '--Fara--':
                linie['asigurator'] == None

            if 'linie_id' in linie:
                del linie['linie_id']

            if 'old_comanda' in linie:
                del linie['old_comanda']

            if 'data_edit' in linie:
                linie['data_edit'] = datetime.datetime.strptime(linie['data_edit'], '%d.%m.%Y %H:%M:%S')

            stare = linie.get('stare', 0)

            if nivel == 1:
                if stare == 3:
                    linie['ascuns'] = True

            if nivel == 2:
                if stare == 0:
                    if linie.get('comanda', False):
                        linie['stare'] = 3
                    else:
                        linie['stare'] = 2
                    linie['consilier_id'] = user_id
                    if linie.get('comanda', False):
                        linie['user_cerere'] = user_id
                        linie['user_comanda'] = user_id
            elif nivel > 3:
                linie['stare'] = 4
                linie['consilier_id'] = user_id
                linie['user_cerere'] = user_id
                linie['user_comanda'] = user_id
                linie['user_receptie'] = user_id

            db.linii.insert(**linie)

            query += db.linii._insert(**linie)
            detalii['insert'].append(linie)

    if len(linii.get('update', [])):
        for linie in linii.get('update', []):
            linie_id = linie.get('linie_id', 0)

            if 'linie_id' in linie:
                del linie['linie_id']

            if 'data_edit' in linie:
                linie['data_edit'] = datetime.datetime.strptime(linie['data_edit'], '%d.%m.%Y %H:%M:%S')

            if 'old_comanda' in linie and 'comanda' in linie:
                if (not linie['old_comanda']) and linie['comanda']:
                    linie['data_edit'] = request.now
                    linie['user_cerere'] = user_id

                del linie['old_comanda']

            if linie.get('asigurator', False) and linie['asigurator'] == '--Fara--':
                linie['asigurator'] = None

            stare = linie.get('stare', 0)

            if stare == 0:
                if nivel == 2:
                    linie['stare'] = 1
                    linie['consilier_id'] = user_id
            elif stare == 1:
                if nivel == 1:
                    linie['stare'] = 2
                    if (linie.get('comanda', False)):
                        linie['user_cerere'] = user_id
            elif stare == 2:
                if (linie.get('comanda', False)):
                    if nivel == 2:
                        linie['stare'] = 3
                        linie['user_comanda'] = user_id

            elif stare == 3:
                if nivel == 3:
                    cant = db(db.linii.id == linie_id).select(db.linii.cantitate).first().cantitate
                    cant_in = linie.get('cantitate_in', False)
                    if cant and cant_in and (str(cant) == str(cant_in)):
                        linie['stare'] = 4
                        linie['user_receptie'] = user_id
                        linie['ascuns'] = False
                elif nivel == 1:
                    linie['ascuns'] = True
            elif stare == 4:
                if nivel == 1:
                    linie['ascuns'] = True

            db(db.linii.id == linie_id).update(**linie)

            query += db(db.linii.id == linie_id)._update(**linie)
            detalii['update'].append(linie)

    if len(linii.get('delete', [])):
        db(db.linii.id.belongs(linii.get('delete', []))).update(sters=True)

        query += db(db.linii.id.belongs(linii.get('delete', [])))._update(sters=True)
        detalii['delete'] = linii.get('delete', [])

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='linii',
        contract='{0}'.format(request.post_vars.contract),
        ip=request.env.remote_addr,
        action='Editare Contract [{0}]'.format(request.post_vars.contract),
        detalii='{0}'.format(detalii),
        query=query
    )
    ##################################################

    return dict(status=200, error="")


def finalizare():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.contract_id:
        return dict(status=500, error="Contract_Id nu exista!")
    else:
        _contract = db(db.contracte.id == request.post_vars.contract_id).select().first()
        if not _contract:
            return dict(status=500, error="Contractul cu ID-ul '{0}' nu exista!".format(request.post_vars.contract_id))

    if not request.post_vars.motiv:
        return dict(status=500, error="Motiv nu exista!")

    db(db.contracte.id == request.post_vars.contract_id).update(finalizat=True, motiv=request.post_vars.motiv,
                                                                user_finalizare=user_id)
    # db(db.linii.contract_id == request.post_vars.contract_id).update(sters = True)

    ###################### LOG #######################
    log_user(
        id=user_id,
        name=username,
        tabel='contracte',
        contract='{0}'.format(_contract.contract),
        ip=request.env.remote_addr,
        action='Finalizare Contract [{0}]'.format(_contract.contract),
        detalii='{0}'.format(dict(id=request.post_vars.contract_id, contract=_contract.contract, auto=_contract.auto,
                                  date_added=_contract.date_added,
                                  user_id=_contract.user_id, programare=_contract.programare,
                                  contactat=_contract.contactat, observatii=_contract.observatii,
                                  finalizat=True, consilier_id=_contract.consilier_id, motiv=request.post_vars.motiv,
                                  user_finalizare=user_id,
                                  numar_auto=_contract.numar_auto)),
        query=db(db.contracte.id == request.post_vars.contract_id)._update(finalizat=True,
                                                                           motiv=request.post_vars.motiv,
                                                                           user_finalizare=user_id)
    )
    ##################################################

    return dict(status=200, error="")
