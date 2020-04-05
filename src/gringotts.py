""" Module for gathering and storing OAuth tokens.

Named for the wizarding bank from Harry Potter
"""

import os
import sys
import threading
import traceback
import webbrowser
import pickle

from urllib.parse import urlparse
import cherrypy
from fitbit.api import Fitbit
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError, MissingTokenError
import config


class OAuth2Server:
    """ OAuth Server class
    """

    def __init__(self, client_id, client_secret, redirect_uri="http://127.0.0.1:8080/"):
        """ Initialize the FitbitOauth2Client """
        self.success_html = """
            <h1>You are now authorized to access the Fitbit API!</h1>
            <br/><h3>You can close this window</h3>"""
        self.failure_html = """
            <h1>ERROR: %s</h1><br/><h3>You can close this window</h3>%s"""

        self.fitbit = Fitbit(
            client_id, client_secret, redirect_uri=redirect_uri, timeout=10,
        )

        self.redirect_uri = redirect_uri

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        url, _ = self.fitbit.client.authorize_token_url()
        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,)).start()

        # Same with redirect_uri hostname and port.
        urlparams = urlparse(self.redirect_uri)
        cherrypy.config.update(
            {
                "server.socket_host": urlparams.hostname,
                "server.socket_port": urlparams.port,
            }
        )

        cherrypy.quickstart(self)

    @cherrypy.expose
    def index(self, state, code=None, error=None):
        """
        Receive a Fitbit response containing a verification code. Use the code
        to fetch the access_token.
        """
        error = None
        if code:
            try:
                self.fitbit.client.fetch_access_token(code)
            except MissingTokenError:
                error = self._fmt_failure(
                    "Missing access token parameter.</br>Please check that "
                    "you are using the correct client_secret"
                )
            except MismatchingStateError:
                error = self._fmt_failure("CSRF Warning! Mismatching state")
        else:
            error = self._fmt_failure("Unknown error while authenticating")
        # Use a thread to shutdown cherrypy so we can return HTML first
        self._shutdown_cherrypy()
        return error if error else self.success_html

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = "<pre>%s</pre>" % ("\n".join(tb)) if tb else ""
        return self.failure_html % (message, tb_html)

    def _shutdown_cherrypy(self):
        """ Shutdown cherrypy in one second, if it's running """
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            threading.Timer(1, cherrypy.engine.exit).start()


def save_token(token):
    """ Saves token (in form of a dict) to a pickle file.

    Having a function that does this allows us to automatically refresh
    tokens per https://python-fitbit.readthedocs.io/en/latest/

    Arguments:
        token (dict): dictionary containing token information.
            Must have a 'user_id' kesy
            For example:
            :code:`{
                'access_token': '_G2iSz-MSR9wFOpvi4CndkJc1oMq3dvXfuoJqI',
                'expires_in': 28800,
                'refresh_token': 'ec282eba08c0',
                'scope':
                    ['settings', 'sleep', 'social', 'heartrate', 'activity',
                    'location', 'nutrition', 'weight', 'profile'],
                'token_type': 'Bearer',
                'user_id': '73DJXK',
                'expires_at': 1580700642.414021
            }`
    """

    print("SAVING TOKEN\n=====\n")

    file_name = "{}_token.pkl".format(token["user_id"])

    full_file_path = os.path.join(config.TOKEN_PATH, file_name)

    with open(full_file_path, "wb") as curr_file:
        pickle.dump(token, curr_file)

    print("TOKEN SAVED TO {} \n=====\n".format(full_file_path))


def load_token(user_id):
    """ Given a user ID, retrieve a that user's access token

    Arguments:
        user_id (str): User's FitBit ID (For example, 73DJXK)

    Returns
        dict: Token for access to user's data in dictionary form
    """

    file_name = "{}_token.pkl".format(user_id)

    full_file_path = os.path.join(config.TOKEN_PATH, file_name)

    with open(full_file_path, "rb") as handle:
        token_dict = pickle.load(handle)

    return token_dict


if __name__ == "__main__":
    import config

    if len(sys.argv) == 3:
        CLIENT_ID, CLIENT_SECRET = sys.argv[
            1:
        ]  # pylint: disable=unbalanced-tuple-unpacking
    elif len(sys.argv) == 1:
        CLIENT_ID, CLIENT_SECRET = config.JOE_ID, config.JOE_SHH
    else:
        print("Arguments: client_id and client_secret")
        print("Or pass none to use the defaults")
        sys.exit(1)

    SERVER = OAuth2Server(CLIENT_ID, CLIENT_SECRET)
    SERVER.browser_authorize()

    PROFILE = SERVER.fitbit.user_profile_get()
    print(
        "You are authorized to access data for the user: {}".format(
            PROFILE["user"]["fullName"]
        )
    )

    print("TOKEN\n=====\n")

    TOKEN = SERVER.fitbit.client.session.token
    for key, value in TOKEN.items():
        print("{} = {}".format(key, value))

    save_token(TOKEN)
