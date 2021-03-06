from pyramid import tweens
from pyramid import httpexceptions

from foo.lib.exceptions import LoginRequired, APIError
from foo.lib import helpers


def _setup_features(RequestCls, settings, prefix='features.'):
    settings_features = dict((key[len(prefix):], settings[key]) for key in settings if key.startswith(prefix))
    RequestCls.DEFAULT_FEATURES.update(settings_features)


def _setup_models(settings):
    """ Attach connection to model modules. """
    if not settings:
        return

    from sqlalchemy import engine_from_config
    from foo import model

    engine = engine_from_config(settings, 'sqlalchemy.')
    model.init(engine)

    # Set password hash maxtime for User object.
    model.User.PASSWORD_MAXTIME = float(settings.get('password.hash_maxtime', 0.0001))


def _template_globals_factory(system):
    return {'h': helpers}


def _login_tween(handler, registry):
    def _login_handler(request):
        try:
            return handler(request)
        except LoginRequired, e:
            next = request.route_url('account_login', _query={'next': e.next or '/'})
            raise httpexceptions.HTTPSeeOther(next)
        except APIError, e:
            raise httpexceptions.HTTPBadRequest(detail=e.message)

    return _login_handler


def make_config(settings):
    from pyramid.config import Configurator
    return Configurator(settings=settings)


def setup_config(config):
    """ Called by setup with a config instance. Or used for initializing tests
    environment."""
    from .request import Request
    config.set_request_factory(Request)
    config.add_tween('foo.web.environment.setup._login_tween', over=tweens.MAIN)

    settings = config.get_settings()

    # Add Pyramid plugins
    config.include('pyramid_handlers') # Handler-based routes
    config.include('pyramid_mailer') # Email

    # Globals for templates
    config.set_renderer_globals_factory(_template_globals_factory)

    # Beaker sessions
    from pyramid_beaker import session_factory_from_settings
    config.set_session_factory(session_factory_from_settings(settings))

    # Routes
    config.add_renderer(".mako", "pyramid.mako_templating.renderer_factory")
    config.add_static_view("static", "foo.web:static")

    # More routes
    from .routes import add_routes
    add_routes(config)

    # Module-level model global setup
    _setup_models(settings)

    # Figure out which features are enabled by default
    _setup_features(Request, settings)

    # Need more setup? Do it here.
    # ...

    return config


def setup_wsgi(global_config, **settings):
    """ This function returns a Pyramid WSGI application.  """
    settings.update(global_config)
    config = setup_config(make_config(settings=settings))
    config.commit()

    return config.make_wsgi_app()


def setup_testing(**settings):
    from pyramid import testing

    # FIXME: Remove the Registry-related stuff once
    # https://github.com/Pylons/pyramid/issues/856 is fixed.
    from pyramid.registry import Registry
    registry = Registry('testing')
    config = testing.setUp(registry=registry, settings=settings)
    config.registry = registry
    config.setup_registry(settings=settings)

    return setup_config(config)


def setup_shell(env):
    """ Called by pshell. """
    from webtest import TestApp
    env['testapp'] = TestApp(env['app'])
