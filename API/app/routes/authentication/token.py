from flask import jsonify, Blueprint

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from app.middleware.bouncer import ban_checking

import jwt

token = Blueprint('token', __name__)


@token.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@ban_checking
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
