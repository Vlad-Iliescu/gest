# coding: utf8# try something like
def index():
    return dict(message="hello from todo.py")


def popup():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    if nivel > 3:
        return dict(status=200, error="", pop=[], count=0)

    if nivel == 1:
        stare = [1, 3, 4]
    elif nivel == 2:
        stare = [0, 2]
    elif nivel == 3:
        stare = [3]
    else:
        stare = [4]

    query = (db.linii.contract_id == db.contracte.id) & (db.linii.stare.belongs(stare))

    if nivel == 1:
        query = (query) & (db.linii.ascuns == False) & (db.contracte.user_id == user_id)
    elif nivel == 2:
        query = (query) & (db.contracte.consilier_id.belongs([14, user_id]))

    popup = db(query)(db.contracte.finalizat == False)(db.linii.sters == False).select(
        db.contracte.id, db.contracte.contract, db.contracte.auto, db.linii.comanda, db.linii.cantitate,
        db.linii.cantitate_in, db.linii.stare).as_list()

    # log(popup)
    # if user_id in [1,15]:
    #    log(db._lastsql)          
    # pop = [dict(id = c['id'], contract = c['contract'], oferte = int(c['oferte']), comenzi = int(c['comenzi']), \
    #    receptionate = int(c['receptionate']) ) for c in popup if int(c['comenzi']) + int(c['oferte']) + int(c['receptionate'])] \
    #     if len(popup) else []

    a = dict()

    for p in popup:
        if not a.get(p['contracte']['id'], False):
            a[p['contracte']['id']] = dict(contract=p['contracte']['contract'], auto=p['contracte']['auto'], linii={})

        if p['linii']['comanda']:
            if p['linii']['cantitate'] == p['linii']['cantitate_in']:
                a[p['contracte']['id']]['linii']['receptionate'] = a[p['contracte']['id']]['linii'].get('receptionate',
                                                                                                        0) + 1
            else:
                a[p['contracte']['id']]['linii']['comenzi'] = a[p['contracte']['id']]['linii'].get('comenzi', 0) + 1
        else:
            if p['linii']['stare'] < 2:
                a[p['contracte']['id']]['linii']['oferte'] = a[p['contracte']['id']]['linii'].get('oferte', 0) + 1

    pop = []
    for i in a:
        if len(a[i]['linii']):
            pop.append(dict(id=i, contract=a[i]['contract'], auto=a[i]['auto'], oferte=a[i]['linii'].get('oferte', 0), \
                            comenzi=a[i]['linii'].get('comenzi', 0), receptionate=a[i]['linii'].get('receptionate', 0)))

    # log(db._lastsql)
    # log(pop)
    # log(len(pop))

    count = len(pop)  # sum((x['oferte'] + x['comenzi']) for x in pop)

    return dict(status=200, error="", pop=pop, count=count)
