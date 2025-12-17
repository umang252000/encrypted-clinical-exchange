# auth/generate_jwt.py  (dev only)
from jose import jwt
import os
import time
import argparse

JWT_SECRET = os.getenv('JWT_SECRET', 'dev-secret-change-me')
JWT_ALG = os.getenv('JWT_ALG', 'HS256')

def create_token(sub: str, role: str, exp_seconds: int = 3600):
    payload = {
        'sub': sub,
        'role': role,
        'iat': int(time.time()),
        'exp': int(time.time()) + exp_seconds
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--sub', default='test-user')
    p.add_argument('--role', default='clinician', choices=['admin','clinician','researcher','auditor'])
    p.add_argument('--exp', type=int, default=3600)
    args = p.parse_args()
    print(create_token(args.sub, args.role, args.exp))