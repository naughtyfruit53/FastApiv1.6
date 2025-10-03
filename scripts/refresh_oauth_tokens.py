#!/usr/bin/env python3
"""
CLI tool for bulk OAuth token refresh
Refreshes expired or soon-to-expire OAuth tokens for email accounts
"""
import sys
import os
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import List

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.oauth_models import UserEmailToken, TokenStatus, OAuthProvider
from app.services.oauth_service import OAuth2Service


async def refresh_token_batch(
    db: AsyncSession,
    tokens: List[UserEmailToken],
    dry_run: bool = False
) -> tuple[int, int]:
    """
    Refresh a batch of tokens
    
    Returns:
        Tuple of (success_count, failure_count)
    """
    oauth_service = OAuth2Service(db)
    success_count = 0
    failure_count = 0
    
    for token in tokens:
        try:
            print(f"  Refreshing token ID {token.id} for {token.email_address} ({token.provider.value})...")
            
            if dry_run:
                print(f"    [DRY RUN] Would refresh token")
                success_count += 1
                continue
            
            # Attempt refresh
            success = await oauth_service.refresh_token(token.id)
            
            if success:
                print(f"    ✓ Successfully refreshed")
                success_count += 1
            else:
                print(f"    ✗ Failed to refresh")
                failure_count += 1
                
        except Exception as e:
            print(f"    ✗ Error refreshing token: {str(e)}")
            failure_count += 1
    
    return success_count, failure_count


async def refresh_all_tokens(
    provider: str = None,
    days_before_expiry: int = 7,
    dry_run: bool = False
) -> None:
    """
    Refresh all OAuth tokens that are expired or expiring soon
    
    Args:
        provider: Optional provider filter (google, microsoft, etc.)
        days_before_expiry: Refresh tokens expiring within this many days
        dry_run: If True, don't actually refresh, just show what would be done
    """
    async with async_session_maker() as db:
        # Build query
        stmt = select(UserEmailToken).where(
            UserEmailToken.status == TokenStatus.ACTIVE
        )
        
        # Filter by provider if specified
        if provider:
            try:
                provider_enum = OAuthProvider(provider.lower())
                stmt = stmt.where(UserEmailToken.provider == provider_enum)
            except ValueError:
                print(f"Error: Invalid provider '{provider}'. Valid providers: google, microsoft, outlook, gmail")
                return
        
        # Execute query
        result = await db.execute(stmt)
        all_tokens = result.scalars().all()
        
        print(f"\nFound {len(all_tokens)} active OAuth tokens")
        
        if not all_tokens:
            print("No tokens to refresh")
            return
        
        # Filter tokens that need refresh
        now = datetime.utcnow()
        expiry_threshold = now + timedelta(days=days_before_expiry)
        
        tokens_to_refresh = []
        for token in all_tokens:
            if token.expires_at and token.expires_at <= expiry_threshold:
                tokens_to_refresh.append(token)
        
        print(f"\n{len(tokens_to_refresh)} tokens need refresh (expiring within {days_before_expiry} days)")
        
        if not tokens_to_refresh:
            print("All tokens are up to date!")
            return
        
        if dry_run:
            print("\n[DRY RUN MODE] - No actual changes will be made\n")
        
        # Refresh tokens
        print("\nRefreshing tokens...")
        success, failure = await refresh_token_batch(db, tokens_to_refresh, dry_run)
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total tokens checked: {len(all_tokens)}")
        print(f"Tokens needing refresh: {len(tokens_to_refresh)}")
        print(f"Successfully refreshed: {success}")
        print(f"Failed to refresh: {failure}")
        print("="*60)
        
        if failure > 0:
            print("\n⚠ Some tokens failed to refresh. Check logs for details.")
            sys.exit(1)
        elif success > 0:
            print("\n✓ All tokens refreshed successfully!")
        else:
            print("\n✓ No tokens needed refresh.")


async def refresh_single_token(token_id: int, dry_run: bool = False) -> None:
    """
    Refresh a single OAuth token by ID
    
    Args:
        token_id: ID of the token to refresh
        dry_run: If True, don't actually refresh
    """
    async with async_session_maker() as db:
        # Fetch token
        stmt = select(UserEmailToken).where(UserEmailToken.id == token_id)
        result = await db.execute(stmt)
        token = result.scalars().first()
        
        if not token:
            print(f"Error: Token ID {token_id} not found")
            sys.exit(1)
        
        print(f"\nToken Details:")
        print(f"  ID: {token.id}")
        print(f"  Email: {token.email_address}")
        print(f"  Provider: {token.provider.value}")
        print(f"  Status: {token.status.value}")
        print(f"  Expires: {token.expires_at}")
        print(f"  Is Expired: {token.is_expired()}")
        
        if dry_run:
            print(f"\n[DRY RUN] Would refresh this token")
            return
        
        # Refresh
        print(f"\nRefreshing token...")
        oauth_service = OAuth2Service(db)
        success = await oauth_service.refresh_token(token_id)
        
        if success:
            print("✓ Successfully refreshed token")
            
            # Show updated info
            await db.refresh(token)
            print(f"\nUpdated Info:")
            print(f"  Status: {token.status.value}")
            print(f"  New Expiry: {token.expires_at}")
            print(f"  Refresh Count: {token.refresh_count}")
        else:
            print("✗ Failed to refresh token")
            sys.exit(1)


async def list_tokens(provider: str = None) -> None:
    """
    List all OAuth tokens with their status
    
    Args:
        provider: Optional provider filter
    """
    async with async_session_maker() as db:
        # Build query
        stmt = select(UserEmailToken)
        
        # Filter by provider if specified
        if provider:
            try:
                provider_enum = OAuthProvider(provider.lower())
                stmt = stmt.where(UserEmailToken.provider == provider_enum)
            except ValueError:
                print(f"Error: Invalid provider '{provider}'")
                return
        
        result = await db.execute(stmt)
        tokens = result.scalars().all()
        
        if not tokens:
            print("No OAuth tokens found")
            return
        
        print(f"\n{'='*100}")
        print(f"{'ID':<6} {'Email':<30} {'Provider':<12} {'Status':<15} {'Expires':<20} {'Expired':<8}")
        print(f"{'='*100}")
        
        for token in tokens:
            expires_str = token.expires_at.strftime('%Y-%m-%d %H:%M') if token.expires_at else 'Never'
            expired_str = 'Yes' if token.is_expired() else 'No'
            
            print(f"{token.id:<6} {token.email_address:<30} {token.provider.value:<12} "
                  f"{token.status.value:<15} {expires_str:<20} {expired_str:<8}")
        
        print(f"{'='*100}")
        print(f"Total: {len(tokens)} tokens")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Bulk OAuth token refresh utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all tokens
  python refresh_oauth_tokens.py --list

  # Refresh all tokens expiring within 7 days
  python refresh_oauth_tokens.py --refresh-all

  # Refresh all Google tokens (dry run)
  python refresh_oauth_tokens.py --refresh-all --provider google --dry-run

  # Refresh specific token
  python refresh_oauth_tokens.py --token-id 123

  # Refresh tokens expiring within 3 days
  python refresh_oauth_tokens.py --refresh-all --days 3
        """
    )
    
    parser.add_argument('--list', action='store_true',
                        help='List all OAuth tokens')
    parser.add_argument('--refresh-all', action='store_true',
                        help='Refresh all tokens that are expired or expiring soon')
    parser.add_argument('--token-id', type=int,
                        help='Refresh a specific token by ID')
    parser.add_argument('--provider', type=str,
                        help='Filter by provider (google, microsoft, etc.)')
    parser.add_argument('--days', type=int, default=7,
                        help='Refresh tokens expiring within N days (default: 7)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.list, args.refresh_all, args.token_id]):
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        if args.list:
            asyncio.run(list_tokens(args.provider))
        elif args.token_id:
            asyncio.run(refresh_single_token(args.token_id, args.dry_run))
        elif args.refresh_all:
            asyncio.run(refresh_all_tokens(args.provider, args.days, args.dry_run))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
