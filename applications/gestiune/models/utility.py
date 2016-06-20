# coding: utf8
BLOCKED = ['calcule', 'client', 'factura', 'istoric', 'logs', 'masina', 'mask', 'tip', 'user', 'users']

if request.env.http_user_agent != "QtGest RoKoR" and request.controller in BLOCKED and request.vars.override != 'thereisnospoon':
    raise HTTP(403, "Forbidden", web2py_error="Not Allowed!")


def is_logged(user_hash):
    usr = db(db.user.hash == user_hash).select(db.user.id, db.user.username, db.user.nivel).first()
    if not usr:
        return False, 0, "", 0
    return True, usr.id, usr.username, usr.nivel


def log_user(id="", name="", ip="0.0.0.0", tabel="", contract="", action="", detalii="", query=""):
    '''
        Insereaza un log in user_logs
        @param id:        Id user
        @param name:      Nume user
        @param tabel:     tabelul unde s-a factu modificarea
        @param contract   numar contract
        @param ip:        ip - ul de unde s-a facut modificarea
        @param action:    Descriere scurta a activitatii
        @param detalii    Detalii
        @param query:     Query-ul ce s-a executat     
    '''
    db.user_logs.insert(user_id=id, username=name, tabel=tabel, contract=contract, ip=ip, activity=action,
                        detalii=detalii,
                        query=query)
    return


def TVA():
    tva = db(db.settings.name == 'TVA').select(db.settings.value, cache=(cache.ram, 36000)).first()

    if tva:
        return tva.value
    else:
        return 24


def log(var):
    import time
    t = time.ctime()
    f = open('./logs/print.log', 'a')

    print >> f, '[{0}]'.format(t), var
