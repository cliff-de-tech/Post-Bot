"""
Token Validation Helper - Graceful Token Handling

Provides helper functions for validating OAuth tokens with graceful failure handling.

USAGE:
    from services.token_validator import validate_linkedin_token, validate_github_token

GRACEFUL FAILURES:
    - Missing token → Clear error message
    - Expired token → Prompt to reconnect
    - Invalid token → Prompt to reconnect
"""
import time
import logging
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)

# Import token store
try:
    from services.token_store import get_token_by_user_id, get_connection_status
except ImportError:
    get_token_by_user_id = None
    get_connection_status = None


class TokenValidationResult:
    """Result of token validation with status and helpful messages."""
    
    def __init__(self, valid: bool, token: str = None, error_code: str = None, 
                 message: str = None, user_action: str = None):
        self.valid = valid
        self.token = token
        self.error_code = error_code
        self.message = message
        self.user_action = user_action
    
    def to_dict(self) -> Dict:
        return {
            "valid": self.valid,
            "error_code": self.error_code,
            "message": self.message,
            "user_action": self.user_action
        }


def validate_linkedin_token(user_id: str) -> TokenValidationResult:
    """
    Validate LinkedIn OAuth token for a user.
    
    Args:
        user_id: Clerk user ID
        
    Returns:
        TokenValidationResult with status and token if valid
        
    SECURITY: 
        - Token is only returned if valid
        - User can only validate their own token (by user_id)
    """
    if not user_id:
        return TokenValidationResult(
            valid=False,
            error_code="missing_user_id",
            message="User not authenticated",
            user_action="Please sign in to continue"
        )
    
    if not get_token_by_user_id:
        return TokenValidationResult(
            valid=False,
            error_code="service_unavailable",
            message="Token service is not available",
            user_action="Please try again later"
        )
    
    try:
        token_data = get_token_by_user_id(user_id)
        
        if not token_data:
            return TokenValidationResult(
                valid=False,
                error_code="not_connected",
                message="LinkedIn account not connected",
                user_action="Please connect your LinkedIn account in Settings"
            )
        
        access_token = token_data.get('access_token')
        if not access_token:
            return TokenValidationResult(
                valid=False,
                error_code="missing_token",
                message="No access token found",
                user_action="Please reconnect your LinkedIn account"
            )
        
        # Check if token is expired
        expires_at = token_data.get('expires_at')
        if expires_at:
            current_time = int(time.time())
            if current_time >= expires_at:
                return TokenValidationResult(
                    valid=False,
                    error_code="token_expired",
                    message="LinkedIn token has expired",
                    user_action="Please reconnect your LinkedIn account"
                )
            
            # Warn if expiring soon (within 1 hour)
            if expires_at - current_time < 3600:
                logger.warning(f"LinkedIn token for user {user_id} expires in less than 1 hour")
        
        # Token is valid
        return TokenValidationResult(
            valid=True,
            token=access_token,
            message="LinkedIn token is valid"
        )
        
    except Exception as e:
        logger.error(f"Error validating LinkedIn token: {e}")
        return TokenValidationResult(
            valid=False,
            error_code="validation_error",
            message="Failed to validate token",
            user_action="Please try again or reconnect your account"
        )


def validate_github_token(user_id: str) -> TokenValidationResult:
    """
    Validate GitHub OAuth token for a user.
    
    Args:
        user_id: Clerk user ID
        
    Returns:
        TokenValidationResult with status and token if valid
        
    Note: GitHub token is optional (public activity works without it)
    """
    if not user_id:
        return TokenValidationResult(
            valid=False,
            error_code="missing_user_id",
            message="User not authenticated",
            user_action="Please sign in to continue"
        )
    
    if not get_token_by_user_id:
        return TokenValidationResult(
            valid=False,
            error_code="service_unavailable",
            message="Token service is not available",
            user_action="Please try again later"
        )
    
    try:
        token_data = get_token_by_user_id(user_id)
        
        if not token_data:
            # GitHub OAuth is optional
            return TokenValidationResult(
                valid=False,
                error_code="not_connected",
                message="GitHub OAuth not connected (optional)",
                user_action="Connect GitHub in Settings for private repo access"
            )
        
        github_token = token_data.get('github_access_token')
        if not github_token:
            return TokenValidationResult(
                valid=False,
                error_code="no_github_token",
                message="GitHub OAuth not connected",
                user_action="Connect GitHub in Settings for private repo access"
            )
        
        # GitHub tokens don't expire (unless revoked)
        return TokenValidationResult(
            valid=True,
            token=github_token,
            message="GitHub token is valid"
        )
        
    except Exception as e:
        logger.error(f"Error validating GitHub token: {e}")
        return TokenValidationResult(
            valid=False,
            error_code="validation_error",
            message="Failed to validate token",
            user_action="Please try again or reconnect your account"
        )


def get_tokens_for_user(user_id: str) -> Tuple[Optional[str], Optional[str], Dict]:
    """
    Get both LinkedIn and GitHub tokens for a user with validation.
    
    Args:
        user_id: Clerk user ID
        
    Returns:
        (linkedin_token, github_token, status_dict)
        
    MULTI-TENANT: Tokens are scoped by user_id only.
    """
    linkedin_result = validate_linkedin_token(user_id)
    github_result = validate_github_token(user_id)
    
    status = {
        "linkedin": linkedin_result.to_dict(),
        "github": github_result.to_dict()
    }
    
    return (
        linkedin_result.token if linkedin_result.valid else None,
        github_result.token if github_result.valid else None,
        status
    )
