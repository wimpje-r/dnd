"""Dungeons & Dragons character sheet app."""
from pkg_resources import resource_filename, Requirement, cleanup_resources
from aiohttp import web
import aiohttp_jinja2
import jinja2
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import aiohttp_login
from aiohttp_login.motor_storage import MotorStorage
import jinja_app_loader

from dnd.views.index import index_handler
import dnd.settings as settings

def start():
    """Start Web server."""
    app = web.Application(debug=settings.DEBUG)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.ChoiceLoader([
            jinja_app_loader.Loader(),
            jinja2.FileSystemLoader(resource_filename(
                Requirement.parse('dnd'), 'dnd/templates'))]),
        auto_reload=settings.DEBUG,
        context_processors=[aiohttp_login.flash.context_processor])
    aiohttp_session.setup(app, EncryptedCookieStorage(
        settings.SESSION_SECRET,
        max_age=settings.SESSION_MAX_AGE))
    app.middlewares.append(aiohttp_login.flash.middleware)

    app['db_client'] = AsyncIOMotorClient()
    app['db'] = app['db_client'].dnd
    aiohttp_login.setup(app, MotorStorage(app['db']), settings.AUTH)

    app.router.add_get("/", index_handler)
    web.run_app(app, port=settings.PORT)
    cleanup_resources()