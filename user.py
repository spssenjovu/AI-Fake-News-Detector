from flask import Flask, request, jsonify

class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        
        self.user = {
            "_id": "",
            "name": self.name,
            "email": self.email,
            "password": self.password
        }

    def to_json(self):
        return jsonify(self.user), 200