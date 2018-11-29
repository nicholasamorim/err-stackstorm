# coding:utf-8
import string
import logging
from random import SystemRandom
from lib.session_manager import SessionManager
from lib.errors import SessionInvalidError

LOG = logging.getLogger(__name__)


def generate_password(length=8):
    rnd = SystemRandom()
    if length > 255:
        length = 255
    return "".join([rnd.choice(string.hexdigits) for _ in range(length)])


class BotPluginIdentity(object):
    """
    For internal use only by err-stackstorm.  The object is used to call methods that will create a
    session and authenticate err-stackstorm credentials with StackStorm.
    """
    def __init__(self, name="errbot%service", secret=generate_password(16)):
        self.name = name
        self.secret = secret


class AuthenticationController(object):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = SessionManager()

    def consume_session(self, session_id):
        """
        Fetch the session and unseal it to make it as consumed.
        """
        session = self.sessions.get_by_uuid(session_id)
        if session is False:
            LOG.debug("Invalid session id '{}'.".format(session_id))
            raise SessionInvalidError
        session.unseal()
        return True

    def list_sessions(self):
        """
        Returns a list of sessions.
        """
        return self.sessions.list_sessions()

    def session_url(self, session_id, url_path="/"):
        """
        Return a URL formatted with the UUID query string attached.
        """
        return "{}{}?uuid={}".format(
            self.bot.st2config.rbac_auth_opts.get("url"), url_path, session_id
        )

    def delete_session(self, session_id):
        """
        Delete a session from the store.
        """
        session = self.sessions.get_by_uuid(session_id)
        if session is False:
            LOG.debug("Session '{}' doesn't exist to be deleted".format(session_id))
            raise SessionInvalidError
        else:
            self.sessions.delete(session.user_id)

    def get_session_token(self, user):
        """
        Get the associated StackStorm token/key given chat backend username.
        Return StackStorm token/key associated with the user or False if session isn't valid or
        secret is missing.
        """
        secret = False
        if isinstance(user, BotPluginIdentity):
            user = user.name
        session = self.sessions.get_by_userid(user)
        if session:
            LOG.debug("Get token for '{}' with session id {}".format(user, session.session_id))
            secret = self.sessions.get_secret(session.session_id)
        return secret

    def set_session_token(self, session, token):
        return self.sessions.put_secret(session.session_id, token)

    def request_session(self, user, user_secret):
        """
        Handle an initial request to establish a session.  If a session already exists, return it.
        """
        if isinstance(user, BotPluginIdentity):
            user_id = user.name
        else:
            user_id = self.bot.chatbackend.normalise_user_id(user)

        try:
            session = self.sessions.create(user_id, user_secret)
        except SessionInvalidError:
            session = self.sessions.get_by_userid(user_id)

        try:
            session.expired()
        except:

            self.sessions.delete(user_id)
            session = self.sessions.create(user_id, user_secret)

        return session

    def match_secret(self, session_id, user_secret):
        """
        Fetch session and compare user_secret.
        """
        session = self.sessions.get_by_uuid(session_id)
        if session is False:
            LOG.debug("Session '{}' doesn't exist.".format(session_id))
            raise SessionInvalidError

        if session.is_sealed():
            LOG.warning("Attempting to check secret while session is sealed.")
            return False
        else:
            return session.match_secret(user_secret)
