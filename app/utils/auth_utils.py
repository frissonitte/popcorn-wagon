from werkzeug.security import check_password_hash, generate_password_hash


def hash_pw(password):
    return generate_password_hash(password)


def verify_pw(hashed_password, password):
    return check_password_hash(hashed_password, password)
