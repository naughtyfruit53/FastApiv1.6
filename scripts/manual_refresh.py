# scripts/manual_refresh.py

"""
Manual token refresh script for operators
"""

import argparse
from app.services.oauth_service import OAuth2Service
from app.core.database import SessionLocal

def main():
    parser = argparse.ArgumentParser(description='Manually refresh OAuth token')
    parser.add_argument('--token-id', type=int, required=True, help='Token ID to refresh')
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        oauth_service = OAuth2Service()
        result = oauth_service.refresh_token(args.token_id, db)
        print(f"Refresh result: {result}")
    finally:
        db.close()

if __name__ == '__main__':
    main()