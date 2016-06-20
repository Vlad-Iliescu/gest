# -*- coding: utf-8 -*-

db = DAL('mysql://root:parola@localhost/gestiune')

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*']  # if request.is_local else []

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Mail, Auth, Crud, Service, PluginManager, prettydate
from gluon.serializers import json
from gluon.tools import *
from StringIO import StringIO
import os
import md5
import hashlib
import datetime

mail = Mail()  # mailer
auth = Auth(db)  # authentication/authorization
crud = Crud(db)  # for CRUD helpers using auth
service = Service()  # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()  # for configuring plugins

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'  # your email
mail.settings.login = 'username:password'  # your credentials or None

auth.settings.hmac_key = 'sha512:ddd50313-6cc3-4210-83f9-78408fb23b67'  # before define_tables()
auth.define_tables()  # creates all needed tables
auth.settings.mailer = mail  # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://' + request.env.http_host + URL('default', 'user', args=[
    'verify_email']) + '/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://' + request.env.http_host + URL('default', 'user', args=[
    'reset_password']) + '/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled = \
#    ['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None  # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

auth.settings.create_user_groups = False
auth.define_tables(username=True)
auth.settings.actions_disabled = ['register', 'change_password', 'request_reset_password', 'profile', 'change_password',
                                  'verify_email', 'retrieve_username', 'reset_password', 'impersonate', 'groups']

db.define_table('user',
                Field('username', 'string', length=50, requires=IS_NOT_EMPTY()),
                Field('password', 'string', length=50, requires=IS_NOT_EMPTY()),
                Field('nivel', 'integer', default=1),
                Field('nume', 'string', length=50),
                Field('email', 'string', requires=IS_EMPTY_OR(IS_EMAIL())),
                Field('hash', 'string'),
                format='%(username)s'
                )

db.define_table('user_logs',
                Field('user_id', 'string', length=50),
                Field('username', 'string', length=50),
                Field('tabel', 'string', length=50),
                Field('contract', 'string', length=50),
                Field('ip', 'string', length=50),
                Field('activity', 'string'),
                Field('query', 'text'),
                Field('date_added', 'datetime', default=request.now),
                Field('date', 'date', default=request.now),
                Field('detalii', 'text'),
                )

db.define_table('settings',
                Field('name', 'string', length=50),
                Field('value', 'double')
                )

db.define_table('asigurator',
                Field('denumire', 'string', length=100),
                Field('tip', 'integer')
                )

db.define_table('furnizori',
                Field('denumire', 'string', length=50),
                )

db.define_table('rapoarte',
                Field('denumire', 'string', length=50, requires=IS_NOT_EMPTY()),
                Field('access', 'integer', default=0),
                Field('tot_contractul', 'boolean', default=False),
                )

db.define_table('columns',
                Field('raport_id', db.rapoarte, requires=IS_IN_DB(db, db.rapoarte.id)),
                Field('denumire', 'string', length=50),
                Field('coloana', 'string', length=50, requires=IS_NOT_EMPTY())
                )

db.define_table('hidden_columns',
                Field('raport_id', db.rapoarte, requires=IS_IN_DB(db, db.rapoarte.id)),
                Field('coloana', 'string', length=50, requires=IS_NOT_EMPTY())
                )

db.define_table('disabled_widgets',
                Field('raport_id', db.rapoarte, requires=IS_IN_DB(db, db.rapoarte.id)),
                Field('widget', 'string', length=50)
                )

db.define_table('active_widgets',
                Field('raport_id', db.rapoarte, requires=IS_IN_DB(db, db.rapoarte.id)),
                Field('widget', 'string', length=50),
                Field('gui_values', 'text'),
                Field('sql_where', 'text')
                )

db.define_table('contracte',
                Field('contract', 'string', length=50),
                Field('auto', 'string', length=50),
                Field('numar_auto', 'string', length=50),
                Field('date_added', 'datetime', default=request.now),
                Field('user_id', db.user, requires=IS_IN_DB(db, db.user.id)),
                Field('consilier_id', db.user, requires=IS_IN_DB(db(db.user.nivel.belongs([2, 4])), db.user.id)),
                Field('programare', 'datetime'),
                Field('contactat', 'boolean', readable=False, writable=False, default=False),
                Field('observatii', 'text'),
                Field('finalizat', 'boolean', readable=False, writable=False, default=False),
                Field('stare', 'integer', readable=False, writable=False, default=0),
                Field('motiv', 'string', requires=IS_EMPTY_OR(IS_IN_SET(['Facturat', 'Renuntat']))),
                Field('user_finalizare', db.user, requires=IS_IN_DB(db, db.user.id)),
                )

db.define_table('linii',
                Field('contract_id', db.contracte, requires=IS_IN_DB(db, db.contracte.id)),
                Field('user_id', db.user, requires=IS_IN_DB(db, db.user.id)),
                Field('date_added', 'datetime', default=request.now),
                Field('comanda', 'boolean', default=False),
                Field('denumire', 'string', length=255),
                Field('oe_am', 'string', length=10, requires=IS_IN_SET(['OE', 'AM', 'OE-AM'])),
                Field('asigurator', 'string', length=50),
                Field('cantitate', 'integer'),

                Field('consilier_id', db.user, requires=IS_IN_DB(db(db.user.nivel.belongs([2, 4])), db.user.id)),
                Field('data_edit', 'datetime'),
                Field('furnizor', 'string', length=255),
                Field('termen', 'integer'),
                Field('cod', 'string', length=50),
                Field('cod_cross', 'string', length=50),
                Field('pret_achizitie', 'double'),
                Field('pret_vanzare', 'double'),

                Field('user_cerere', db.user, requires=IS_IN_DB(db, db.user.id)),
                Field('cantitate_in', 'integer', default=0),
                Field('locatie', 'string', length=50),
                Field('user_receptie', db.user, requires=IS_IN_DB(db(db.user.nivel.belongs([3, 4])), db.user.id)),
                Field('data_receptie', 'datetime'),

                Field('user_comanda', db.user, requires=IS_IN_DB(db(db.user.nivel.belongs([2, 4])), db.user.id)),
                Field('stare', 'integer', readable=False, writable=False, default=0),
                # 0 - def, 1 = completat, 2 = receptie, 3 = sters
                Field('ascuns', 'boolean', readable=False, writable=False, default=False),
                # 0 - def, 1 = completat, 2 = receptie, 3 = sters
                Field('sters', 'boolean', readable=False, writable=False, default=False),
                )

# class Totals():
#    def pret_vanzare_tva(self):
#        return self.linii.pret_vanzare * (1 + TVA()/100)
#    def total_tva(self):
#        return (self.linii.pret_vanzare * self.linii.cantitate) * (1 + TVA()/100) 

# db.linii.virtualfields.append(Totals())
