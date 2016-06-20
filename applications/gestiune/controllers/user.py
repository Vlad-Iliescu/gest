# coding: utf8
# try something like
def index():
    a = request
    return dict(message=a)


def logare():
    if not request.post_vars.username:
        return dict(status=False, error="Username gol!")
    if not request.post_vars.password:
        return dict(status=False, error="Parola empty!")
    usr = db(
        (db.user.username == request.post_vars.username) & (db.user.password == request.post_vars.password)
    ).select(db.user.id, db.user.nivel, db.user.nume).first()
    if not usr:
        return dict(status=False, error="Userul sau parola nu corespunde!")

    login_hash = hashlib.md5(str(request.now)).hexdigest()
    usr.update_record(hash=login_hash)
    return dict(status=True, nivel=usr.nivel, nume=usr.nume, login_hash=login_hash, error="")


def get_consilieri():
    if not request.post_vars.user_hash:
        return dict(status=500, error="Hash nu exista!")
    else:
        ok, user_id, username, nivel = is_logged(request.post_vars.user_hash)
        if not ok:
            return dict(status=401, error="Sesiunea a expirat!")

    consilieri = db(db.user.nivel.belongs([2, 5])).select(
        db.user.id, db.user.nume, cache=(cache.ram, 36000), orderby=~db.user.nivel).as_list()

    return dict(status=200, error="", consilieri=consilieri, sql=db(db.user.nivel.belongs([2, 5]))._select())
