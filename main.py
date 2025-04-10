# from https://towardsdatascience.com/deploy-to-google-cloud-run-using-github-actions-590ecf957af0
import os
import sys
from flask import Flask, session, render_template
from dotenv import load_dotenv
load_dotenv()
import flask_login
from flask_login import current_user
from flask_principal import identity_loaded, RoleNeed, UserNeed, Principal
from flask_caching import Cache
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURR_DIR)
sys.path.append(CURR_DIR)

# custom error pages
def page_not_found(e):
    return render_template('404.html'), 404

def permission_denied(e):
    return render_template("403.html"), 403


login_manager = flask_login.LoginManager()
# app = Flask(__name__)
def create_app(config_filename=''):
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, permission_denied)
    app.secret_key = os.environ.get("SECRET_KEY", "missing_secret")
    app.cache = Cache(app,config={'CACHE_TYPE': 'SimpleCache'})
    login_manager.init_app(app)
    # app.config.from_pyfile(config_filename)
    with app.app_context():
        from auth.auth import auth
        app.register_blueprint(auth)
        from shopindex.shopindex import shopindex
        app.register_blueprint(shopindex)
        from shop.shop import shop
        app.register_blueprint(shop)
        # load the extension
        principals = Principal(app) # must be defined/initialized for identity to work (flask_principal)
        @login_manager.user_loader
        def load_user(user_id):
            if user_id is None:
                return None
            print("login_manager loading user") # happens each request
            from auth.models import User
            if session["_user_id"] == user_id and "user" in session.keys():
                print("loading user from session")
                # load user from session (convert json to User)
                # see User object for convering json of roles to [Roles]
                import jsons
                return jsons.loads(session["user"], User)
            # failsafe if we don't have a "user" key in session
            from sql.db import DB
            print("loading user from DB") # note: we'd lose roles here since it makes a new user object without a roles query
            try:
                result = DB.selectOne("SELECT cid, email FROM  Customer WHERE id = %s", user_id)
                if result.status:
                    return User(**result.row)
            except Exception as e:
                print(e)
            return None

        @identity_loaded.connect_via(app)
        def on_identity_loaded(sender, identity):
            # Set the identity user object
            identity.user = current_user

            # Add the UserNeed to the identity
            if hasattr(current_user, 'id'):
                identity.provides.add(UserNeed(current_user.id))

            # Assuming the User model has a list of roles, update the
            # identity with the roles that the user provides
            if hasattr(current_user, 'roles'):
                for role in current_user.roles:
                    identity.provides.add(RoleNeed(role.name))
        # DON'T DELETE, this cleans up the DB connection after each request
        # this avoids sleeping queries
        @app.teardown_request 
        def after_request_cleanup(ctx):
            from sql.db import DB
            DB.close()
        return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
