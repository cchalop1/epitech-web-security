import json
from app.middleware.token_optionnal import token_optionnal
from app.models.Users import Users
from flask import jsonify, request, Blueprint, send_file
from mongoengine.errors import ValidationError
from flask_jwt_extended import jwt_required
from app.errors import *
from app.middleware.token_valid import token_valid
from app.middleware.request_form import request_form
from app.models.File import File
from flask_jwt_extended import get_jwt_identity

file_upload = Blueprint('file_upload', __name__)

CONTENT_TYPE_ACCEPTED = ['image/jpeg', 'image/png', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf']

@file_upload.route('/upload', methods=['POST'])
@jwt_required()
@token_valid
@request_form
def upload(form, user):
    try:
        if not request.files.getlist("files"):
            return jsonify({'msg': 'File required'}), 404
        file = File(owner=user.id)
        if form.get('public').lower() == 'true':
            file.public = True
        if not CONTENT_TYPE_ACCEPTED in request.files["files"].content_type:
            return jsonify({'msg': 'File type is not allowed'}), 404
        file.name = request.files["files"].filename
        file.fs.put(request.files["files"])
        file.save()
        return jsonify({'msg': 'File successfully created'}), 201
    except ValidationError as error:
        return jsonify(error.to_dict()), 403

@file_upload.route('/my', methods=['GET'])
@jwt_required()
@token_valid
def my_uploads(user):
    files = File.objects(owner=user.id)
    return jsonify(json.loads(files.to_json())), 200

@file_upload.route('/<file_id>', methods=['GET'])
@jwt_required(optional=True)
@token_optionnal
def download(user, file_id):
    file = File.objects(id=file_id).first()
    if not file:
        return jsonify({'msg': RESOURCE_NOT_FOUND}), 404
    if not file.public:
      if user == 'noauth' or file.owner.id != user.id:
        return jsonify({'msg': 'Not your private file'}), 403
    return send_file(file.fs, as_attachment=True, attachment_filename=file.name), 200

@file_upload.route('/<file_id>', methods=['DELETE'])
@jwt_required()
@token_valid
def delete(user, file_id):
    file = File.objects(id=file_id).first()
    if not file:
        return jsonify({'msg': RESOURCE_NOT_FOUND}), 404
    if file.owner.id != user.id:
        return jsonify({'msg': 'Not your file'}), 403
    file.fs.delete()
    file.delete()
    return jsonify({'msg': 'Successfully deleted'}), 200
