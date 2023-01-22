import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
import app_config
from hash_check import AuthorizationManager
import os
from typing import List, Set

import subprocess

app = Flask(__name__)

app.config.from_object(app_config)
Session(app)

admin_auth_manager = AuthorizationManager(email_list_path = 'admin_hashed_email_list.txt') # Used to validate emails. Can also be run on the server (e.g., to add hashed-salted emails) to a list.
user_auth_manager = AuthorizationManager(email_list_path = 'user_hashed_email_list.txt') # Used to validate emails. Can also be run on the server (e.g., to add hashed-salted emails) to a list.

def _check_using_auth_manager(emails : Set[str] , auth_manager : AuthorizationManager):
    for email in emails:
        c = auth_manager.check_if_in_list(email)
        if c:
            return True
    return False

def _check_in_user_emails(email_strings : Set[str]):
    return _check_using_auth_manager(email_strings, user_auth_manager)

def _check_in_admin_emails(email_strings : Set[str]):
    return _check_using_auth_manager(email_strings, admin_auth_manager)




### Kept from the initial template from Microsoft:
# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for = 1, x_proto=1, x_host=1, x_prefix = 1)


@app.route("/anonymous")
def anonymous():
    return "anonymous page"

@app.route("/")
def index():
    #if not session.get("user"):
    #    return redirect(url_for("login"))
        
    if not session.get("user"):
        session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
        return render_template('index.html', auth_url=session["flow"]["auth_uri"], version=msal.__version__)
    else:
        return render_template('index.html', user=session["user"], version=msal.__version__)

@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    print("authorized?")
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)

        session_user_part = result.get("id_token_claims")
        is_allowed = _check_in_user_emails(set(session_user_part['emails']))

        if is_allowed:
            session["user"] = session_user_part
            _save_cache(cache)
        else:
            session.clear()
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))

@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['id_token']},
        ).json()
    return render_template('graph.html', result=graph_data)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template

if __name__ == "__main__":
    # When running with gunicorn set the "host" to 127.0.0.1! (or a unix socket)
    app.run(host='0.0.0.0', port=5000)
