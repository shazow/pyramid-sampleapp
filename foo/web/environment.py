from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings

from foo.lib import helpers
from foo.web import views


def _setup_models(settings):
    """
    Attach connection to model modules.
    """
    if not settings:
        return

    from sqlalchemy import engine_from_config
    from foo import model

    engine = engine_from_config(settings, 'sqlalchemy.')
    model.init(engine)

    # Set password hash maxtime for User object.
    model.User.PASSWORD_MAXTIME = float(settings.get('password.hash_maxtime', 0.0001))


def _setup_routes(config):
    config.add_route('api', '/api', views.api.index)
    config.add_route('index', '/', views.index.index)
    config.add_route('account.create', '/account/create', views.account.create)


def _template_globals_factory(system):
    return {'h': helpers}


def setup(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    # Globals for templates
    config.set_renderer_globals_factory(_template_globals_factory)

    # Beaker sessions
    config.set_session_factory(session_factory_from_settings(settings))

    # Routes
    config.add_renderer(".mako", "pyramid.mako_templating.renderer_factory")
    config.add_static_view("static", "foo.web:static")

    # More routes
    _setup_routes(config)

    # Module-level model global setup
    _setup_models(settings)

    # Need more setup? Do it here.
    # ...

    return config.make_wsgi_app()
