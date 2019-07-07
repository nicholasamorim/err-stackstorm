.. _quick_start:

************
Quick Start
************

If you are familiar with Errbot and Stackstorm, this guide will get you up and running in no time. For in-depth information, refer to :ref:`installation` and :ref:`configuration`

1. Enable Errbot's webserver::

   !repos install https://github.com/tkit/errbot-plugin-webserverconfiguration

2. Paste the sample configuration below in Errbot's ``config.py`` file adjusting the URLs to match your Stackstorm instance and set up one of the authentication methods.

.. code-block:: python

    STACKSTORM = {
        'auth_url': 'https://your.stackstorm.com/auth/v1',
        'api_url': 'https://your.stackstorm.com/api/v1',
        'stream_url': 'https://your.stackstorm.com/stream/v1',

        'verify_cert': True,
        'secrets_store': 'cleartext',
        'api_auth': {
            'user': {
                'name': 'my_username',
                'password': "my_password",
            },
            'token': "<User token>",
            'apikey': '<API Key>'
        },
        'rbac_auth': {
            'standalone': {},
        },
        'timer_update': 900, #  Unit: second.  Interval to check the user token is still valid.
    }


3. Install err-stackstorm::

   !repos install https://github.com/nzlosh/err-stackstorm.git

4. Install ``ChatOps`` pack on Stackstorm and copy `this rule <https://raw.githubusercontent.com/nzlosh/err-stackstorm/master/contrib/stackstorm-chatops/rules/notify_errbot.yaml>`_ to it.

5. Edit the ``chatops/actions/post_message.yaml`` file and replace ``chatops`` with ``errbot``.

6. Set up an `action alias <https://docs.stackstorm.com/chatops/aliases.html>`_ on Stackstorm. See :ref:`action_aliases` for more details.

7. Sending ``!st2help`` to your bot will list the available Stackstorms's aliases.

8. Aliases can be run like this: ``!st2 run date on 192.168.5.1``
