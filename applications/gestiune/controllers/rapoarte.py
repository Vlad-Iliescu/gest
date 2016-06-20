# coding: utf8
# try something like

def index():
    if request.vars.contract:
        contract = request.vars.contract
    else:
        contract = None

    if contract:
        _users = db().select(db.user.ALL, cache=(cache.ram, 36000))
        users = dict()
        for u in _users:
            users[u.id] = u.nume

        q = ((db.user_logs.tabel.lower() == 'contracte') | (db.user_logs.tabel.lower() == 'linii')) & (
        db.user_logs.contract.lower().like(contract))

        contracte = db(q).select(db.user_logs.ALL, orderby=db.user_logs.date_added)

        form = crud.select(db.user_logs, q)

        return dict(contracte=contracte, users=users, query=db._lastsql, form=form)
    else:
        return dict()


def get_rapoarte():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if nivel > 3:
        rapoarte = db().select(db.rapoarte.ALL, orderby=db.rapoarte.denumire)
    else:
        rapoarte = db((db.rapoarte.access == nivel) | (db.rapoarte.access == 0)).select(db.rapoarte.ALL,
                                                                                        orderby=db.rapoarte.denumire)

    return dict(status=200, error="", rapoarte=rapoarte)


def get_data_raport():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    users = db(db.user.nivel.belongs([1, 2, 3, 4])).select(db.user.id, db.user.nume, db.user.nivel,
                                                           orderby=db.user.nume).as_list()
    consilieri = db(db.user.nivel.belongs([2, 5])).select(db.user.id, db.user.nume, orderby=db.user.nume).as_list()
    asigurator = db(db.asigurator.id > 0).select(db.asigurator.denumire, orderby=db.asigurator.denumire).as_list()
    furnizori = db(db.furnizori.id > 0).select(db.furnizori.denumire, orderby=db.furnizori.denumire).as_list()
    return dict(status=200, error="", users=users, consilieri=consilieri, asigurator=asigurator, furnizori=furnizori)


def add_raport():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.nume:
        return dict(status=500, error="Nume nu exista")
    else:
        _rap = db(db.rapoarte.denumire.lower() == request.post_vars.nume.lower()).select(db.rapoarte.denumire).first()
        if (_rap):
            return dict(status=401, error="Numele exista deja!")

    import json

    if request.post_vars.data:
        linii = json.loads(request.post_vars.data)
    else:
        return dict(status=500, error="Date inexistente!")

    if request.post_vars.tot_contractul and str(request.post_vars.tot_contractul).isdigit() and int(
            request.post_vars.tot_contractul) == 1:
        tot_contractul = True
    else:
        tot_contractul = False

    raport_id = db.rapoarte.insert(denumire=request.post_vars.nume, access=0, tot_contractul=tot_contractul)

    for colum in linii.get("colums", []):
        db.columns.insert(raport_id=raport_id, denumire=colum.get("alias", None), coloana=colum.get("column", None))

    for act in linii.get("active", []):
        if ('widget' not in act) or ('sql_where' not in act):
            continue
        db.active_widgets.insert(raport_id=raport_id, widget=act.get("widget", None),
                                 gui_values=act.get("gui_values", None),
                                 sql_where=act.get("sql_where", None))

    for di in linii.get("disabled", []):
        if 'widget' not in di:
            continue
        db.disabled_widgets.insert(raport_id=raport_id, widget=di.get('widget', None))

    for hi in linii.get("hidden_colums", []):
        if 'column' not in hi:
            continue
        db.hidden_columns.insert(raport_id=raport_id, coloana=hi.get("column", None))

    return dict(status=200, error="", id=raport_id)


def edit_raport():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.raport_id:
        return dict(status=500, error="Raport ID nu exista!")
    else:
        _raport = db(db.rapoarte.id == request.post_vars.raport_id).select(db.rapoarte.denumire, db.rapoarte.access,
                                                                           db.rapoarte.tot_contractul).first()

    if not (_raport):
        return dict(status=500, error="Raportul nu exista")

    colums = db(db.columns.raport_id == request.post_vars.raport_id).select(db.columns.denumire,
                                                                            db.columns.coloana).as_list()
    active = db(db.active_widgets.raport_id == request.post_vars.raport_id).select(db.active_widgets.widget,
                                                                                   db.active_widgets.gui_values).as_list()
    disabled = db(db.disabled_widgets.raport_id == request.post_vars.raport_id).select(
        db.disabled_widgets.widget).as_list()
    hidden = db(db.hidden_columns.raport_id == request.post_vars.raport_id).select(db.hidden_columns.coloana).as_list()

    return dict(status=200, error="", colums=colums, active=active, disabled=disabled, hidden=hidden,
                denumire=_raport.denumire,
                tot_contractul=_raport.tot_contractul)


def generate_raport():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not (request.post_vars.raport_id):
        return dict(status=500, error="Raport_id nu exista")
    else:
        _raport = db(db.rapoarte.id == request.post_vars.raport_id).select(db.rapoarte.denumire, db.rapoarte.access,
                                                                           db.rapoarte.tot_contractul).first()

    if not _raport:
        return dict(status=500, error="Raportul nu exista")

    _colums = db(db.columns.raport_id == request.post_vars.raport_id).select(db.columns.denumire, db.columns.coloana)
    _active = db(db.active_widgets.raport_id == request.post_vars.raport_id).select(db.active_widgets.sql_where)

    colums = []
    for col in _colums:
        colums.append('{0} AS `{1}`'.format(col.coloana, col.denumire) if col.denumire else '{0}'.format(col.denumire))

    headers = []
    for i in colums:
        headers.append(i.split('AS')[1].strip(' `') if len(i.split('AS')) == 2 else i.split('.')[1])

    where = [x.sql_where for x in _active if x.sql_where]

    _users = db().select(db.user.ALL, cache=(cache.ram, 36000))
    users = dict()
    for u in _users:
        users[u.id] = u.nume

    if not _raport.tot_contractul:
        if len(where):
            query = "SELECT {0} FROM contracte JOIN linii on contracte.id = linii.contract_id WHERE {1};".format(
                ', '.join(colums) if len(colums) else '*', ' AND '.join(where))
        else:
            query = "SELECT {0} FROM contracte JOIN linii on contracte.id = linii.contract_id;".format(
                ', '.join(colums) if len(colums) else '*')
    else:
        if len(where):
            query = "SELECT {0} FROM contracte JOIN linii ON contracte.id = linii.contract_id WHERE contracte.id IN ( SELECT contracte.id  FROM contracte JOIN linii on contracte.id = linii.contract_id WHERE {1} );".format(
                ', '.join(colums) if len(colums) else '*', ' AND '.join(where))
        else:
            query = "SELECT {0} FROM contracte JOIN linii on contracte.id = linii.contract_id;".format(
                ', '.join(colums) if len(colums) else '*')

    try:
        raport = db.executesql(query, as_dict=True)
    except:
        raport = []

    # log(query)
    # log(headers)

    if "Pret Achizitie" in headers:
        idx = headers.index('Pret Achizitie')
        headers.insert(idx + 1, 'Pret Achizitie TVA')

    if "Pret Vanzare" in headers:
        idx = headers.index('Pret Vanzare')
        headers.insert(idx + 1, 'Pret Vinzare TVA')

    if "Pret Vanzare" in headers and "Cantitate" in headers:
        idx = headers.index('Pret Vinzare TVA')
        headers.insert(idx + 1, 'Total')

    if "Data Completare" in headers and "Termen" in headers:
        idx = headers.index('Termen')
        headers.insert(idx + 1, 'Sosire')

    for r in raport:
        if 'Comanda' in r:
            r['Comanda'] = 'Comanda' if r['Comanda'] == 'T' else 'Oferta'

        if 'Consilier Contract' in r:
            r['Consilier Contract'] = users[r['Consilier Contract']]

        if 'Consilier Lucrat' in r:
            r['Consilier Lucrat'] = users[r['Consilier Lucrat']] if r['Consilier Lucrat'] else ''

        if 'Contactat' in r:
            r['Contactat'] = 'Da' if r['Contactat'] == 'T' else 'Nu'

        if 'Data Adaugare Contract' in r:
            r['Data Adaugare Contract'] = r['Data Adaugare Contract'].strftime('%d/%m/%Y %H:%M')

        if 'Data Adaugare Linie' in r:
            r['Data Adaugare Linie'] = r['Data Adaugare Linie'].strftime('%d/%m/%Y %H:%M')

        if "Data Completare" in r and "Termen" in r:
            termen = r["Termen"] if str(r["Termen"]).isdigit() else 0
            data = r["Data Completare"] if r["Data Completare"] else None
            if data and str(termen).isdigit():
                from datetime import timedelta
                while termen:
                    data = data + timedelta(days=1)
                    if data.weekday() == 6 or data.weekday() == 5:
                        data = data + timedelta(days=1)
                    else:
                        termen -= 1

                r["Sosire"] = data.strftime('%d/%m/%Y')
            else:
                r["Sosire"] = ''

        if 'Data Completare' in r:
            r['Data Completare'] = r['Data Completare'].strftime('%d/%m/%Y %H:%M') if r['Data Completare'] else ''

        if 'Data Receptie' in r:
            r['Data Receptie'] = r['Data Receptie'].strftime('%d/%m/%Y %H:%M') if r['Data Receptie'] else ''

        if 'Finalizat' in r:
            r['Finalizat'] = 'Da' if r['Finalizat'] == 'T' else 'Nu'

        if "Pret Achizitie" in r:
            r['Pret Achizitie TVA'] = '{0:.2f}'.format(r['Pret Achizitie'] * (1 + TVA() / 100.)) if r[
                'Pret Achizitie'] else ''

        if "Pret Vanzare" in r:
            r['Pret Vinzare TVA'] = '{0:.2f}'.format(r['Pret Vanzare'] * (1 + TVA() / 100.)) if r[
                'Pret Vanzare'] else ''

        if "Pret Vanzare" in r and "Cantitate" in r:
            r['Total'] = '{0:.2f}'.format((r['Pret Vanzare'] * r['Cantitate']) * (1 + TVA() / 100.)) if r[
                                                                                                            'Pret Vanzare'] and \
                                                                                                        r[
                                                                                                            'Cantitate'] else ''

        if "Programare" in r:
            r['Programare'] = r['Programare'].strftime('%d/%m/%Y %H:%M') if r['Programare'] else ''

        if 'Sters' in r:
            r['Sters'] = 'Da' if r['Sters'] == 'T' else 'Nu'

        if 'User Adaugare Contract' in r:
            r['User Adaugare Contract'] = users[r['User Adaugare Contract']] if r['User Adaugare Contract'] else ''

        if 'User Adaugare Linie' in r:
            r['User Adaugare Linie'] = users[r['User Adaugare Linie']] if r['User Adaugare Linie'] else ''

        if 'User Receptie' in r:
            r['User Receptie'] = users[r['User Receptie']] if r['User Receptie'] else ''

    return dict(status=200, error="", cols=headers, raport=raport, denumire=_raport.denumire)


def editeaza_raport():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.raport_id:
        return dict(status=500, error="Raport_id nu exista")
    else:
        _raport = db(db.rapoarte.id == request.post_vars.raport_id).select(db.rapoarte.denumire, db.rapoarte.access,
                                                                           db.rapoarte.tot_contractul,
                                                                           db.rapoarte.id).first()

    if not _raport:
        return dict(status=500, error="Raportul nu exista")

    if not request.post_vars.nume:
        return dict(status=500, error="Nume nu exista")
    else:
        # log(request.post_vars.nume)
        _rap = db(db.rapoarte.denumire.lower() == request.post_vars.nume.lower())(db.rapoarte.id != _raport.id).select(
            db.rapoarte.denumire).first()
        # log(db._lastsql)
        if _rap:
            return dict(status=401, error="Numele exista deja!")

    import json

    if request.post_vars.data:
        linii = json.loads(request.post_vars.data)
    else:
        return dict(status=500, error="Date inexistente!")

    # COLUMNS    
    db(db.columns.raport_id == _raport.id).delete()

    for colum in linii.get("colums", []):
        db.columns.insert(raport_id=_raport.id, denumire=colum.get("alias", None), coloana=colum.get("column", None))

    # ACTIVE WIDGETS
    db(db.active_widgets.raport_id == _raport.id).delete()

    for act in linii.get("active", []):
        if ('widget' not in act) or ('sql_where' not in act):
            continue
        db.active_widgets.insert(raport_id=_raport.id, widget=act.get("widget", None),
                                 gui_values=act.get("gui_values", None),
                                 sql_where=act.get("sql_where", None))

    # DISABLED
    db(db.disabled_widgets.raport_id == _raport.id).delete()

    for di in linii.get("disabled", []):
        if 'widget' not in di:
            continue
        db.disabled_widgets.insert(raport_id=_raport.id, widget=di.get('widget', None))

    # HIDDEN
    db(db.hidden_columns.raport_id == _raport.id).delete()

    for hi in linii.get("hidden_colums", []):
        if 'column' not in hi:
            continue
        db.hidden_columns.insert(raport_id=_raport.id, coloana=hi.get("column", None))

    if request.post_vars.tot_contractul and str(request.post_vars.tot_contractul).isdigit() and int(
            request.post_vars.tot_contractul) == 1:
        tot_contractul = True
    else:
        tot_contractul = False

    db(db.rapoarte.id == _raport.id).update(denumire=request.post_vars.nume, tot_contractul=tot_contractul)

    return dict(status=200, error="")


def sterge_raport():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!");
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not (ok):
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.raport_id:
        return dict(status=500, error="Raport_id nu exista")
    else:
        _raport = db(db.rapoarte.id == request.post_vars.raport_id).select(db.rapoarte.denumire, db.rapoarte.access,
                                                                           db.rapoarte.tot_contractul,
                                                                           db.rapoarte.id).first()

    if not _raport:
        return dict(status=500, error="Raportul nu exista")

    db(db.rapoarte.id == _raport.id).delete()

    return dict(status=200, error="")


def generate_raport_from_query():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if request.post_vars.tot_contractul and str(request.post_vars.tot_contractul).isdigit() and int(
            request.post_vars.tot_contractul) == 1:
        tot_contractul = True
    else:
        tot_contractul = False

    import json

    if request.post_vars.data:
        linii = json.loads(request.post_vars.data)
    else:
        return dict(status=500, error="Date inexistente!")

    colums = []
    for col in linii.get('colums', []):
        if not (col.get('column', False)):
            continue
        colums.append('{0} AS `{1}`'.format(col['column'], col['alias']) if col.get('alias', False) else '{0}'.format(
            col['column']))

    headers = []
    for i in colums:
        headers.append(i.split('AS')[1].strip(' `') if len(i.split('AS')) == 2 else i.split('.')[1])

    where = []
    for wh in linii.get('active', []):
        if not (wh.get('sql_where', False)):
            continue
        where.append('{0}'.format(wh['sql_where']))

    _users = db().select(db.user.ALL, cache=(cache.ram, 36000))
    users = dict()
    for u in _users:
        users[u.id] = u.nume

    if not tot_contractul:
        if len(where):
            query = "SELECT {0} FROM contracte JOIN linii on contracte.id = linii.contract_id WHERE {1};".format( \
                ', '.join(colums) if len(colums) else '*', ' AND '.join(where))
        else:
            query = "SELECT {0} FROM contracte JOIN linii on contracte.id = linii.contract_id;".format( \
                ', '.join(colums) if len(colums) else '*')
    else:
        if len(where):
            query = "SELECT {0} FROM contracte JOIN linii ON contracte.id = linii.contract_id WHERE contracte.id IN ( SELECT contracte.id  FROM contracte JOIN linii on contracte.id = linii.contract_id WHERE {1} );".format( \
                ', '.join(colums) if len(colums) else '*', ' AND '.join(where))
        else:
            query = "SELECT {0} FROM contracte JOIN linii on contracte.id = linii.contract_id;".format( \
                ', '.join(colums) if len(colums) else '*')

    try:
        raport = db.executesql(query, as_dict=True)
    except:
        raport = []

    # log(query)

    if "Pret Achizitie" in headers:
        idx = headers.index('Pret Achizitie')
        headers.insert(idx + 1, 'Pret Achizitie TVA')

    if "Pret Vanzare" in headers:
        idx = headers.index('Pret Vanzare')
        headers.insert(idx + 1, 'Pret Vinzare TVA')

    if "Pret Vanzare" in headers and "Cantitate" in headers:
        idx = headers.index('Pret Vinzare TVA')
        headers.insert(idx + 1, 'Total')

    if "Data Completare" in headers and "Termen" in headers:
        idx = headers.index('Termen')
        headers.insert(idx + 1, 'Sosire')

    for r in raport:
        if 'Comanda' in r:
            r['Comanda'] = 'Comanda' if r['Comanda'] == 'T' else 'Oferta'

        if 'Consilier Contract' in r:
            r['Consilier Contract'] = users[r['Consilier Contract']]

        if 'Consilier Lucrat' in r:
            r['Consilier Lucrat'] = users[r['Consilier Lucrat']] if r['Consilier Lucrat'] else ''

        if 'Contactat' in r:
            r['Contactat'] = 'Da' if r['Contactat'] == 'T' else 'Nu'

        if 'Data Adaugare Contract' in r:
            r['Data Adaugare Contract'] = r['Data Adaugare Contract'].strftime('%d/%m/%Y %H:%M')

        if 'Data Adaugare Linie' in r:
            r['Data Adaugare Linie'] = r['Data Adaugare Linie'].strftime('%d/%m/%Y %H:%M')

        if "Data Completare" in r and "Termen" in r:
            termen = r["Termen"] if str(r["Termen"]).isdigit() else 0
            data = r["Data Completare"] if r["Data Completare"] else None
            if data and str(termen).isdigit():
                from datetime import timedelta
                while termen:
                    data = data + timedelta(days=1)
                    if data.weekday() == 6 or data.weekday() == 5:
                        data = data + timedelta(days=1)
                    else:
                        termen -= 1

                r["Sosire"] = data.strftime('%d/%m/%Y')
            else:
                r["Sosire"] = ''

        if 'Data Completare' in r:
            r['Data Completare'] = r['Data Completare'].strftime('%d/%m/%Y %H:%M') if r['Data Completare'] else ''

        if 'Data Receptie' in r:
            r['Data Receptie'] = r['Data Receptie'].strftime('%d/%m/%Y %H:%M') if r['Data Receptie'] else ''

        if 'Finalizat' in r:
            r['Finalizat'] = 'Da' if r['Finalizat'] == 'T' else 'Nu'

        if "Pret Achizitie" in r:
            r['Pret Achizitie TVA'] = '{0:.2f}'.format(r['Pret Achizitie'] * (1 + TVA() / 100.)) if r[
                'Pret Achizitie'] else ''

        if "Pret Vanzare" in r:
            r['Pret Vinzare TVA'] = '{0:.2f}'.format(r['Pret Vanzare'] * (1 + TVA() / 100.)) if r[
                'Pret Vanzare'] else ''

        if "Pret Vanzare" in r and "Cantitate" in r:
            r['Total'] = '{0:.2f}'.format((r['Pret Vanzare'] * r['Cantitate']) * (1 + TVA() / 100.)) if r[
                                                                                                            'Pret Vanzare'] and \
                                                                                                        r[
                                                                                                            'Cantitate'] else ''

        if "Programare" in r:
            r['Programare'] = r['Programare'].strftime('%d/%m/%Y %H:%M') if r['Programare'] else ''

        if 'Sters' in r:
            r['Sters'] = 'Da' if r['Sters'] == 'T' else 'Nu'

        if 'User Adaugare Contract' in r:
            r['User Adaugare Contract'] = users[r['User Adaugare Contract']] if r['User Adaugare Contract'] else ''

        if 'User Adaugare Linie' in r:
            r['User Adaugare Linie'] = users[r['User Adaugare Linie']] if r['User Adaugare Linie'] else ''

        if 'User Receptie' in r:
            r['User Receptie'] = users[r['User Receptie']] if r['User Receptie'] else ''

    return dict(status=200, error="", cols=headers, raport=raport, denumire="Previzualizare")
