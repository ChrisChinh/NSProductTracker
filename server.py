from flask import Flask, request
from flask_cors import CORS
import flask
import secrets
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from database.database import Database
from database.userdb import UserDB

TOKEN_LENGTH = 32  # Length of the token to be generated
TOKEN_EXPIRY_LENGTH = 60  # Number of minutes to allow users to stay logged in


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/login": {"origins": "*"}})

        # PRODUCTION
        self.userdb = UserDB()
        self.database = Database()
        self.index = lambda: flask.render_template('login.html')

        def dashboard():
            return flask.render_template('dashboard.html')
        self.auth_tokens = {}

        self.add_route('/', self.index)
        self.add_route('/login', self.login, methods=['POST'])
        self.add_route('/logout', self.logout, methods=['POST'])
        self.add_route('/lookup', self.request, methods=['POST'])
        self.add_route('/images/<filename>', self.get_image)
        self.add_route('/pdf/<filename>', self.get_pdf)
        self.add_route('/dashboard', dashboard)
        self.add_route('/edit', self.edit)
        self.add_route('/edit_item', self.edit_item, methods=['POST'])

        # For clearing expired auth tokens
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.remove_expired_tokens, 'interval', minutes=1)
        scheduler.start()

    def edit(self):
        return flask.render_template('edit.html')

    def edit_item(self):
        data: dict | None = None
        try:
            data = request.get_json()
        except:
            data = None
        finally:
            response = self.run_checks(data)
            if response is not None:
                self.app.logger.warning('Returning non-success response')
                return response
            serial = data['serial']
            self.app.logger.warning('Editing item: ' + serial)
            data.pop('token')
            data.pop('username')
            data.pop('serial')
            success = self.database.edit_item(data, serial)
            return flask.jsonify({'success': success})

    def get_pdf(self, filename):
        # self.check_auth(token)
        self.app.logger.warning('Getting pdf: ' + filename)
        return flask.send_from_directory('pdfs', filename)

    def get_image(self, filename):
        self.app.logger.warning('Getting image: ' + filename)
        return flask.send_from_directory('images', filename)

    def run_checks(self, data):
        """ Check for commonly expected data
        Username token, and a serial number that is valid
        Return a response if any of the data is missing or invalid
        Else return None
        """
        if data is None:
            return flask.jsonify({'error': 'Invalid JSON'})

        # Check to ensure correct data is present
        required_data = ['token', 'serial', 'username']
        for key in required_data:
            if key not in data:
                return flask.jsonify({'error': 'Missing required data'})

        # Check to ensure serial is valid
        serial = data['serial']
        if not self.database.serial_exists(serial):
            return flask.jsonify({'error': 'Invalid serial', "success": False})

        # Check to ensure username is valid
        username = data['username']
        if self.userdb.get_user(username) is None:
            return flask.jsonify({'error': 'Invalid username', "success": False})

        # Check to ensure token is valid
        token = data['token']
        if not self.check_auth(token, username):
            return flask.jsonify({'error': 'Invalid token', "success": False})

        return None

    def request(self):
        data = None
        try:
            data = request.get_json()
        except:
            return flask.jsonify({'error': 'Invalid JSON'})
        finally:
            response = self.run_checks(data)
            if response is not None:
                return response
            serial = data['serial']
            # Return the information associated with the serial
            return_data = self.database.get_item(serial)
            if return_data is None:
                return flask.jsonify({'error': 'Unknwon error'})
            return flask.jsonify(return_data)

    def check_auth(self, token, username):
        if username not in self.auth_tokens and username is not None:
            return False
        return self.auth_tokens[username][0] == token

    def logout(self):
        try:
            data = request.get_json()
            self.app.logger.warning(data)
            token = data['token']
            username = data['username']
            if username in self.auth_tokens:
                self.auth_tokens.pop(username)
                return flask.jsonify({'success': True})
            else:
                return flask.jsonify({'success': False, 'error': 'Invalid token'})
        except:
            return flask.jsonify({'error': 'Invalid JSON'})

    def login(self):
        try:
            data = request.get_json()
            self.app.logger.warning(data)
            username = data['username']
            password = data['password']
            if self.userdb.get_user(username) == password:
                if username in self.auth_tokens:
                    return flask.jsonify({'success': True, 'token': self.auth_tokens[username][0]})
                token = secrets.token_urlsafe(TOKEN_LENGTH)
                self.auth_tokens[username] = (token, datetime.now())
                return flask.jsonify({'success': True, 'token': token})
            else:
                return flask.jsonify({'success': False, 'error': 'Invalid username or password'})
        except:
            return flask.jsonify({'error': 'Invalid JSON'})

    def run(self):
        # self.app.run(host='0.0.0.0', port=5000)
        self.app.run()

    def add_route(self, route, func, methods=['POST', 'GET']):
        self.app.add_url_rule(route, view_func=func, methods=methods)

    def start(self):
        self.run()

    def remove_expired_tokens(self):
        for user in self.auth_tokens:
            if datetime.now() - self.auth_tokens[user][1] > timedelta(minutes=TOKEN_EXPIRY_LENGTH):
                self.auth_tokens.pop(user)


if __name__ == '__main__':
    server = Server()
    server.start()
