from functools import wraps
from jwt import encode, decode
from flask import request, render_template, make_response, flash
from random import randint

# AuthManager object should only be initialised once

class AuthManager():
    def __init__(self, SECRET : str):
        self.OTP : str
        self.SECRET = SECRET # store environment secret in class variable SECRET
        self.devices = {}
        self.regenerateOTP() # make constant random 6 digit number for one time password

    def regenerateOTP(self):
        self.OTP = "".join([str(randint(0, 9)) for _ in range(6)])

    # auth required decorator
    def auth_required(self, f):
        @wraps(f)
        def decorator(*args, **kws):
            user_addr = request.remote_addr
            # if user_addr in ('127.0.0.1', '::1', 'localhost'):
            #     return f(*args, **kws)
            if 'Authorization' not in request.cookies:
                return self.userUnauthenticated() # if no authorization cookie present, user is definitely unauthorised
            data = request.cookies.get('Authorization')
            token = str.replace(str(data), 'Authorization=','')
            try:
                if decode(token, self.SECRET, algorithms=['HS256']) != {user_addr:self.devices[user_addr]}:
                    return self.userUnauthenticated() # if the user's authorisation cookie does not decode to a dictionary containing their IP and the one-time-password, they are unauthorised
            except: # if not in JWT format, there is a chance an error will occur, in this case the user is definitely unauthorised
                return self.userUnauthenticated()
            return f(*args, **kws)     
        return decorator
    
    def authenticate(self, userInput : str, userIP : str):
        if str(userInput) == str(self.OTP): # if correct OTP
            # response = make_response(render_template('index.html'))
            self.devices[request.remote_addr] = self.OTP
            response = make_response()
            response.headers["HX-Redirect"] = "/"
            # return jsonify(success=True), 201, {"HX-Redirect": "/"}
            response.set_cookie('Authorization', self.generate_auth(userIP)) # generate authorization cookie based on user's IP and return it
            self.regenerateOTP()
            return response
        else:
            flash("Incorrect One Time Password!")
            return self.userUnauthenticated() # wrong OTP password entered, user not authorised
        
    def generate_auth(self, sessionIP : str) -> str:
        token = encode({sessionIP:self.OTP}, self.SECRET, algorithm="HS256") # create authorisation cookie encoded with secret containing user's IP and OTP
        return token

    def userUnauthenticated(self):
        print(f"Enter the One Time Password: {self.OTP}")
        return render_template("authenticate.html"), 401 # return authentication page HTML with HTML status code 401 unauthorised.