# coding: utf8
# try something like
def index():
    return dict(message="hello from search.py")


def get_results():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!");
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not (ok):
            return dict(status=401, error="Sesiunea a expirat!")

    if not request.post_vars.has_contract:
        contract = False
    else:
        contract = True

    if contract:
        # log('>>> contract <<<')
        if not (request.post_vars.contract):
            return dict(status=500, error="Campul Contract este gol!")

        contracte = db(db.contracte.contract.like(request.post_vars.contract)).select(db.contracte.contract,
                                                                                      db.contracte.auto,
                                                                                      db.contracte.id)

    else:
        queries = []

        if request.post_vars.contract:
            queries.append(db.contracte.contract.like(request.post_vars.contract))

        if request.post_vars.cod:
            queries.append(db.linii.cod.like(request.post_vars.cod))

        if request.post_vars.denumire:
            queries.append(db.linii.denumire.like(request.post_vars.denumire))

        if request.post_vars.furnizor:
            queries.append(db.linii.furnizor.like(request.post_vars.furnizor))

        if not len(queries):
            return dict(status=500, error="Nici un filtru specificat!")

        query = reduce(lambda a, b: (a & b), queries)

        contracte = db(query)(db.contracte.id == db.linii.contract_id).select(db.contracte.id, db.contracte.contract,
                                                                              db.contracte.auto,
                                                                              db.linii.cod, db.linii.denumire,
                                                                              db.linii.cantitate, db.linii.furnizor)

    return dict(status=200, error="", contracte=contracte, contract=contract)


def get_detalii():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    furnizori = db().select(db.furnizori.denumire, cache=(cache.ram, 36000), orderby=db.furnizori.denumire).as_list()

    return dict(status=200, error="", furnizori=furnizori)
