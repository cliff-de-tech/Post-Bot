"""
Posts Routes
Handles post generation, publishing, and scheduling.

This module contains endpoints for:
- Generating AI-powered post previews
- Publishing posts to LinkedIn
- Scheduling posts for later
"""

import os
import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import json

from schemas.requests import RepurposeRequest

logger = structlog.get_logger(__name__)

# =============================================================================
# ROUTER SETUP
# =============================================================================
router = APIRouter(prefix="/api/post", tags=["Posts"])

# =============================================================================
# SERVICE IMPORTS
# =============================================================================
try:
    from services.ai_service import (
        generate_post_with_ai,
        generate_linkedin_post,
        get_available_providers,
        ModelProvider,
    )
except ImportError:
    generate_post_with_ai = None
    generate_linkedin_post = None
    get_available_providers = None
    ModelProvider = None

try:
    from services.persona_service import build_full_persona_context
except ImportError:
    build_full_persona_context = None

try:
    from services.image_service import get_relevant_image
except ImportError:
    get_relevant_image = None

try:
    from services.linkedin_service import post_to_linkedin, upload_image_to_linkedin
except ImportError:
    post_to_linkedin = None
    upload_image_to_linkedin = None

try:
    from services.user_settings import get_user_settings
except ImportError:
    get_user_settings = None

try:
    from services.token_store import (
        get_all_tokens,
        get_access_token_for_urn,
        get_token_by_user_id,
    )
except ImportError:
    get_all_tokens = None
    get_access_token_for_urn = None
    get_token_by_user_id = None

try:
    from services.scheduled_posts import schedule_post
except ImportError:
    schedule_post = None

try:
    from services.scrape_service import scrape_url
except ImportError:
    scrape_url = None

try:
    from services.auth_service import (
        TokenNotFoundError,
        TokenRefreshError,
        AuthProviderError,
    )
except ImportError:
    TokenNotFoundError = Exception
    TokenRefreshError = Exception
    AuthProviderError = Exception

try:
    from services.rate_limiter import (
        post_generation_limiter,
        publish_limiter,
    )
    RATE_LIMITING_ENABLED = True
except ImportError:
    RATE_LIMITING_ENABLED = False
    post_generation_limiter = None
    publish_limiter = None

try:
    from middleware.clerk_auth import get_current_user, require_auth
except ImportError:
    logger.error("clerk_auth_import_failed", detail="Authentication middleware unavailable - all authenticated endpoints will reject requests")
    async def get_current_user():
        """Fallback that rejects all requests when auth middleware is unavailable."""
        raise HTTPException(status_code=503, detail="Authentication service unavailable")

    async def require_auth():
        """Fallback that rejects all requests when auth middleware is unavailable."""
        raise HTTPException(status_code=503, detail="Authentication service unavailable")

from services.db import get_database
from repositories.posts import PostRepository


# =============================================================================
# REQUEST MODELS
# =============================================================================
class GenerateRequest(BaseModel):
    context: dict
    user_id: Optional[str] = None
    model: Optional[str] = "groq"  # groq (free), mistral (free), openai/anthropic/gemini (pro)
    style: Optional[str] = "standard"  # template style


class PostRequest(BaseModel):
    context: Optional[dict] = None
    test_mode: Optional[bool] = True
    user_id: Optional[str] = None
    model: Optional[str] = "groq"
    post_content: Optional[str] = None
    image_url: Optional[str] = None
    post_id: Optional[str] = None


class ScheduleRequest(BaseModel):
    user_id: str
    post_content: str
    scheduled_time: int
    image_url: Optional[str] = None


class BatchGenerateRequest(BaseModel):
    """Request for batch post generation in Bot Mode."""
    user_id: str
    activities: list  # List of GitHub activities to generate posts for
    style: Optional[str] = "standard"  # Template style
    model: Optional[str] = "groq"  # AI provider


def _should_apply_rate_limit(current_user: Optional[dict]) -> bool:
    """Apply rate limiting in production contexts only."""
    if not RATE_LIMITING_ENABLED or not post_generation_limiter:
        return False

    # Explicit bypass for tests/local debugging.
    disable_rate_limit = os.getenv("DISABLE_RATE_LIMITING", "false").lower() in {"1", "true", "yes"}
    is_pytest = bool(os.getenv("PYTEST_CURRENT_TEST"))
    is_dev_mode = bool(current_user and current_user.get("dev_mode"))

    return not (disable_rate_limit or is_pytest or is_dev_mode)


# =============================================================================
# ENDPOINTS
# =============================================================================
@router.post("/generate-preview")
async def generate_preview(
    req: GenerateRequest,
    current_user: dict = Depends(require_auth)
):
    """Generate an AI post preview from context.
    
    Rate limited to 10 requests per hour per user to prevent abuse.
    
    Supports multiple AI providers with tier enforcement:
    - Free tier: Always routes to Groq (fast, free)
    - Pro tier: Can choose groq, mistral, openai (GPT-4o), anthropic (Claude 3.5), or gemini
    """
    if not generate_linkedin_post:
        # Fallback to legacy if new function unavailable
        if not generate_post_with_ai:
            raise HTTPException(status_code=503, detail="AI service not available")
    
    # Auth is required for this endpoint, so use authenticated user_id only
    user_id = current_user.get("user_id") if current_user else None
    
    # Rate limiting check (10 requests/hour for AI generation)
    if _should_apply_rate_limit(current_user) and user_id:
        allowed, rate_info = post_generation_limiter.is_allowed(user_id)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded for post generation",
                headers={"Retry-After": str(rate_info.get('retry_after', 60))}
            )
    
    # Get user's API keys if user_id available
    groq_api_key = None
    openai_api_key = None
    anthropic_api_key = None
    gemini_api_key = None
    
    if user_id and get_user_settings:
        try:
            settings = await get_user_settings(user_id)
            if settings:
                groq_api_key = settings.get('groq_api_key')
                openai_api_key = settings.get('openai_api_key')
                anthropic_api_key = settings.get('anthropic_api_key')
                gemini_api_key = settings.get('gemini_api_key')
        except Exception as e:
            logger.warning("failed_to_get_user_settings", error=str(e))
    
    # Get user's persona context
    persona_context = None
    if user_id and build_full_persona_context:
        try:
            persona_context = await build_full_persona_context(user_id)
            if persona_context:
                logger.info("persona_loaded", user_id=user_id[:8], length=len(persona_context))
        except Exception as e:
            logger.warning("failed_to_get_persona", error=str(e))
    
    # Use new multi-model router
    if generate_linkedin_post:
        result = await generate_linkedin_post(
            context_data=req.context,
            user_id=user_id,
            model_provider=req.model or "groq",
            style=req.style or "standard",
            groq_api_key=groq_api_key,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
            gemini_api_key=gemini_api_key,
            persona_context=persona_context,
        )
        
        if result:
            return {
                "post": result.content,
                "provider": result.provider.value,
                "model": result.model,
                "was_downgraded": result.was_downgraded,
            }
        else:
            return {"error": "Failed to generate post"}
    
    # Fallback to legacy sync function
    post = generate_post_with_ai(req.context, groq_api_key=groq_api_key, persona_context=persona_context)
    return {"post": post, "provider": "groq", "model": "llama-3.3-70b-versatile"}


@router.post("/repurpose")
async def repurpose_url(
    req: RepurposeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Takes a URL, scrapes its content, and generates 3 diverse LinkedIn posts using AI.
    """
    if not generate_linkedin_post or not scrape_url:
        raise HTTPException(status_code=503, detail="Required services not available")
        
    user_id = req.user_id if getattr(req, 'user_id', None) else (current_user.get("user_id") if current_user else None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    # Rate limit check
    if _should_apply_rate_limit(current_user):
        allowed, rate_info = post_generation_limiter.is_allowed(user_id)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded for post generation",
                headers={"Retry-After": str(rate_info.get('retry_after', 60))}
            )

    # 1. Scrape the URL
    try:
        scraped_content = await scrape_url(req.url)
    except Exception as e:
        logger.error("scraping_failed", url=req.url, error=str(e))
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")

    if not scraped_content:
        raise HTTPException(status_code=400, detail="Could not extract content from the URL")

    # Limit scraped content size to avoid context window explosion
    max_chars = 8000
    if len(scraped_content) > max_chars:
        scraped_content = scraped_content[:max_chars] + "..."

    # 2. Get API Keys & Settings
    groq_api_key = None
    openai_api_key = None
    anthropic_api_key = None
    gemini_api_key = None
    
    if get_user_settings:
        try:
            settings = await get_user_settings(user_id)
            if settings:
                groq_api_key = settings.get('groq_api_key')
                openai_api_key = settings.get('openai_api_key')
                anthropic_api_key = settings.get('anthropic_api_key')
                gemini_api_key = settings.get('gemini_api_key')
        except Exception as e:
            logger.warning("failed_to_get_user_settings", error=str(e))
            
    # Get user's persona context
    persona_context = None
    if build_full_persona_context:
        try:
            persona_context = await build_full_persona_context(user_id)
        except Exception as e:
            logger.warning("failed_to_get_persona", error=str(e))

    # 3. Build Context
    context_data = {
        "url": req.url,
        "content": scraped_content,
        "type": "repurpose"
    }

    # 4. Generate AI content
    result = await generate_linkedin_post(
        context_data=context_data,
        user_id=user_id,
        model_provider=req.model or "groq",
        style="standard",
        groq_api_key=groq_api_key,
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
        gemini_api_key=gemini_api_key,
        persona_context=persona_context,
    )
    
    if not result or not result.content:
        raise HTTPException(status_code=500, detail="Failed to generate posts from AI")
        
    # 5. Parse JSON array
    try:
        # Sometimes the AI returns backticks around JSON
        raw_content = result.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
            
        posts_array = json.loads(raw_content.strip())
        if not isinstance(posts_array, list):
            # Fallback if AI somehow returns a string or object not array
            posts_array = [result.content]
    except Exception as e:
        logger.error("repurpose_json_parse_failed", error=str(e), content=result.content)
        # Fallback to single raw post if JSON parsing fails
        posts_array = [result.content]

    # Save to database (as drafts)
    saved_posts = []
    try:
        db = await get_database()
        post_repo = PostRepository(db)
        
        for post_content in posts_array:
            saved_post = await post_repo.create_post(
                user_id=user_id,
                content=post_content,
                status="draft", # they start as drafts
                context=context_data,
                model_used=result.model
            )
            # MongoDB returns _id as ObjectId, need to stringify
            post_id = str(saved_post["_id"]) if "_id" in saved_post else str(saved_post.get("id", ""))
            saved_posts.append({
                "id": post_id,
                "content": saved_post.get("content", post_content),
                "status": "draft",
                "createdAt": saved_post.get("created_at")
            })
    except Exception as e:
        logger.error("failed_to_save_repurposed_posts", error=str(e))
        # We can still return the generated content
        for idx, post_content in enumerate(posts_array):
            saved_posts.append({
                "id": f"temp_{idx}",
                "content": post_content,
                "status": "draft"
            })
            
    return {
        "posts": saved_posts,
        "provider": result.provider.value if result else "unknown",
        "model": result.model if result else "unknown"
    }


@router.post("/generate-batch")
async def generate_batch(
    req: BatchGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate multiple posts for Bot Mode.
    
    Takes a list of GitHub activities and generates posts for each one.
    Returns the list of generated posts with success/failure counts.
    
    Supports tier-based model selection:
    - Free tier: Always Groq
    - Pro tier: Can specify groq, mistral, openai, anthropic, or gemini
    """
    if not generate_linkedin_post and not generate_post_with_ai:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    # Use authenticated user_id if available, otherwise fall back to request body
    user_id = req.user_id
    if current_user and current_user.get("user_id"):
        user_id = current_user["user_id"]
        if user_id != req.user_id:
            raise HTTPException(status_code=403, detail="Cannot generate posts for other users")
    activities = req.activities
    style = req.style or "standard"
    model = req.model or "groq"
    
    # Get user settings for API keys and persona
    groq_api_key = None
    openai_api_key = None
    anthropic_api_key = None
    gemini_api_key = None
    persona_context = None
    
    if user_id and get_user_settings:
        try:
            settings = await get_user_settings(user_id)
            if settings:
                groq_api_key = settings.get('groq_api_key')
                openai_api_key = settings.get('openai_api_key')
                anthropic_api_key = settings.get('anthropic_api_key')
                gemini_api_key = settings.get('gemini_api_key')
        except Exception as e:
            logger.warning("failed_to_get_user_settings", error=str(e))
    
    if user_id and build_full_persona_context:
        try:
            persona_context = await build_full_persona_context(user_id)
        except Exception as e:
            logger.warning("failed_to_get_persona", error=str(e))
    
    # Generate posts for each activity
    generated_posts = []
    success_count = 0
    failed_count = 0
    used_provider = None
    was_downgraded = False
    
    for activity in activities:
        try:
            # Build context from activity
            context = {
                "type": activity.get("type", "push"),
                "repo": activity.get("repo") or activity.get("full_repo", "").split("/")[-1],
                "full_repo": activity.get("full_repo", ""),
                "commits": activity.get("commits", 1),
                "date": activity.get("date", activity.get("time_ago", "recently")),
                "title": activity.get("title", ""),
                "description": activity.get("description", ""),
                "tone": style  # Use the selected template/style
            }
            
            # Use new multi-model router if available
            if generate_linkedin_post:
                result = await generate_linkedin_post(
                    context_data=context,
                    user_id=user_id,
                    model_provider=model,
                    style=style,
                    groq_api_key=groq_api_key,
                    openai_api_key=openai_api_key,
                    anthropic_api_key=anthropic_api_key,
                    gemini_api_key=gemini_api_key,
                    persona_context=persona_context,
                )
                
                if result:
                    final_post = {
                        "id": f"gen_{success_count}_{activity.get('id', '')}",
                        "content": result.content,
                        "activity": activity,
                        "style": style,
                        "status": "draft",
                        "provider": result.provider.value,
                        "model": result.model,
                    }
                    generated_posts.append(final_post)
                    
                    # PERSISTENCE: Save as draft immediately
                    try:
                        db = get_database()
                        repo = PostRepository(db, user_id)
                        saved_id = await repo.save_post(
                            post_content=result.content,
                            post_type='bot',
                            context=activity,
                            status='draft'
                        )
                        final_post['id'] = str(saved_id)
                        final_post['db_id'] = saved_id
                    except Exception as e:
                        logger.error("failed_to_persist_post_provider", error=str(e))
                        
                    used_provider = result.provider.value
                    was_downgraded = result.was_downgraded
                    success_count += 1
                else:
                    failed_count += 1
            else:
                # Fallback to legacy function
                post_content = generate_post_with_ai(
                    context, 
                    groq_api_key=groq_api_key, 
                    persona_context=persona_context
                )
                
                if post_content:
                    final_post = {
                        "id": f"gen_{success_count}_{activity.get('id', '')}",
                        "content": post_content,
                        "activity": activity,
                        "style": style,
                        "status": "draft",
                        "provider": "groq",
                        "model": "llama-3.3-70b-versatile",
                    }
                    generated_posts.append(final_post)
                    
                    # PERSISTENCE: Save as draft immediately
                    try:
                        db = get_database()
                        repo = PostRepository(db, user_id)
                        saved_id = await repo.save_post(
                            post_content=post_content,
                            post_type='bot',
                            context=activity,
                            status='draft'
                        )
                        # Build full object with real ID so frontend can use it for publishing
                        final_post['id'] = str(saved_id)
                        final_post['db_id'] = saved_id  # explicitly track DB ID
                    except Exception as e:
                        logger.error("failed_to_persist_post", error=str(e))
                        
                    success_count += 1
                else:
                    failed_count += 1
                    
        except Exception as e:
            logger.error("failed_to_generate_post", error=str(e))
            failed_count += 1
            
    # For provider-based generation loop above, we also need persistence
    # (Note: I'm patching the loop above in a second chunk or assuming the user meant to cover both paths. 
    # To be safe and clean, I will wrap the persistence logic in a helper or duplicate it for the first branch if I can't easily merge.)
    # Actually, the previous 'if result:' block also needs persistence. 
    # Let me re-read the file content to ensure I catch both branches.
    # The file view showed headers 300-450.
    
    return {
        "posts": generated_posts,
        "generated_count": success_count,
        "failed_count": failed_count,
        "total": len(activities),
        "provider": used_provider,
        "was_downgraded": was_downgraded,
    }


@router.get("/bot-stats")
async def get_bot_stats(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get statistics for bot mode (generated vs published)."""
    if current_user and current_user.get("user_id") != user_id:
         raise HTTPException(status_code=403, detail="Unauthorized")
         
    try:
        db = get_database()
        repo = PostRepository(db, user_id)
        return await repo.get_bot_stats()
    except Exception as e:
        logger.error("failed_to_get_bot_stats", error=str(e))
        return {"generated": 0, "published": 0}


@router.get("/providers")
async def list_providers(
    current_user: dict = Depends(get_current_user)
):
    """List available AI providers and their configuration status.
    
    Returns provider availability based on configured API keys and user tier.
    Free tier users will see premium providers as unavailable for them.
    """
    if not get_available_providers:
        return {
            "providers": {
                "groq": {"available": False, "model": "unknown", "tier": "free"},
                "mistral": {"available": False, "model": "unknown", "tier": "free"},
                "openai": {"available": False, "model": "unknown", "tier": "pro"},
                "anthropic": {"available": False, "model": "unknown", "tier": "pro"},
                "gemini": {"available": False, "model": "unknown", "tier": "pro"},
            },
            "user_tier": "free",
        }
    
    providers = get_available_providers()
    
    # Get user tier if authenticated
    user_tier = "free"
    if current_user and current_user.get("user_id") and get_user_settings:
        try:
            settings = await get_user_settings(current_user["user_id"])
            if settings:
                user_tier = settings.get("subscription_tier", "free")
        except Exception:
            pass
    
    # Mark pro providers as unavailable for free users
    if user_tier == "free":
        for name, info in providers.items():
            if info.get("tier") == "pro":
                info["available_to_user"] = False
            else:
                info["available_to_user"] = info.get("available", False)
    else:
        for name, info in providers.items():
            info["available_to_user"] = info.get("available", False)
    
    return {
        "providers": providers,
        "user_tier": user_tier,
    }


@router.post("/publish")
async def publish(
    req: PostRequest,
    current_user: dict = Depends(get_current_user)
):
    """Publish a post to LinkedIn.

    Accepts either pre-generated post_content (bot mode) or a context dict
    to generate from (manual mode).
    """
    # Use authenticated user_id if available
    user_id = None
    if current_user and current_user.get("user_id"):
        user_id = current_user["user_id"]
    elif req.user_id:
        user_id = req.user_id

    # If post_content was provided directly (bot mode), use it as-is
    post = req.post_content

    # Otherwise generate from context (manual mode)
    if not post and req.context:
        if not generate_post_with_ai:
            raise HTTPException(status_code=503, detail="AI service not available")

        # Get user's Groq API key if user_id provided
        groq_api_key = None
        user_settings = None
        if user_id and get_user_settings:
            try:
                user_settings = await get_user_settings(user_id)
                if user_settings:
                    groq_api_key = user_settings.get('groq_api_key')
            except Exception as e:
                logger.warning("failed_to_get_user_settings", error=str(e))

        # Get user's persona context
        persona_context = None
        if user_id and build_full_persona_context:
            try:
                persona_context = await build_full_persona_context(user_id)
            except Exception as e:
                logger.warning("failed_to_get_persona", error=str(e))

        post = generate_post_with_ai(req.context, groq_api_key=groq_api_key, persona_context=persona_context)

    if not post:
        return {"error": "failed_to_generate_post", "success": False}

    if req.test_mode:
        return {"success": True, "test_mode": True, "message": "Test publish successful (no real post created)", "post": post}

    # Actual publishing logic - ONLY use user's own token
    image_data = None
    image_asset = None

    if not user_id or not get_token_by_user_id:
        raise HTTPException(status_code=401, detail="Authentication required to publish")

    try:
        user_token = await get_token_by_user_id(user_id)
        if not user_token or not user_token.get('access_token'):
            raise HTTPException(status_code=401, detail="LinkedIn not connected. Please reconnect your account.")
        
        linkedin_urn = user_token.get('linkedin_user_urn')
        token = user_token.get('access_token')

        # Check if token has expired and attempt refresh
        import time as _time
        expires_at = user_token.get('expires_at')
        if expires_at and int(expires_at) < int(_time.time()):
            logger.warning("token_expired_attempting_refresh", user_id=user_id)
            refresh_token = user_token.get('refresh_token')
            if refresh_token:
                try:
                    from services.auth_service import refresh_access_token
                    from services.token_store import save_token
                    refreshed = refresh_access_token(refresh_token, user_id=user_id)
                    token = refreshed.access_token
                    # Persist refreshed token
                    await save_token(
                        linkedin_urn, refreshed.access_token,
                        refreshed.refresh_token, refreshed.expires_at,
                        user_id=user_id
                    )
                    logger.info("token_refreshed_before_publish", user_id=user_id)
                except Exception as refresh_err:
                    logger.error("token_refresh_failed_before_publish", error=str(refresh_err))
                    raise HTTPException(
                        status_code=401,
                        detail="LinkedIn session expired and could not be refreshed. Please reconnect your account in Settings."
                    )
            else:
                raise HTTPException(
                    status_code=401,
                    detail="LinkedIn session expired. Please reconnect your account in Settings."
                )
        
        if get_relevant_image and token:
            image_data = get_relevant_image(post)
        if image_data and upload_image_to_linkedin and token:
            image_asset = upload_image_to_linkedin(image_data, access_token=token, linkedin_user_urn=linkedin_urn)

        # Try async linkedin_api first, fall back to sync linkedin_service
        publish_success = False
        try:
            from services.linkedin_api import post_to_linkedin as async_post
            result = await async_post(
                user_urn=linkedin_urn,
                access_token=token,
                post_content=post,
                image_url=None,
            )
            publish_success = True
        except ImportError:
            # Fallback to sync service
            if post_to_linkedin and token:
                publish_success = post_to_linkedin(post, image_asset, access_token=token, linkedin_user_urn=linkedin_urn)
        except PermissionError as perm_err:
            raise HTTPException(status_code=401, detail=str(perm_err))
        except RuntimeError as rt_err:
            raise HTTPException(status_code=502, detail=str(rt_err))

        if not publish_success:
            raise HTTPException(
                status_code=502,
                detail="LinkedIn rejected the post. Your token may be expired — try reconnecting your account in Settings."
            )

        # Persist successful publish in post history (backend-authoritative).
        try:
            from services.db import get_database
            from repositories.posts import PostRepository

            db = get_database()
            repo = PostRepository(db, user_id)

            linkedin_post_id = result.get("id") if isinstance(result, dict) else None

            # If caller supplied a DB post_id, update it; otherwise create a published row.
            if req.post_id:
                try:
                    await repo.update_status(int(req.post_id), 'published', linkedin_post_id)
                except Exception:
                    await repo.save_post(
                        post_content=post,
                        post_type='mixed',
                        context=req.context if isinstance(req.context, dict) else {},
                        status='published',
                        linkedin_post_id=linkedin_post_id,
                    )
            else:
                await repo.save_post(
                    post_content=post,
                    post_type='mixed',
                    context=req.context if isinstance(req.context, dict) else {},
                    status='published',
                    linkedin_post_id=linkedin_post_id,
                )
        except Exception as e:
            logger.error("failed_to_persist_published_post", user_id=user_id, error=str(e))
        
        # Refresh learned patterns after successful publish (fire-and-forget)
        if user_id:
            try:
                from services.persona_service import refresh_learned_patterns
                import asyncio
                asyncio.create_task(refresh_learned_patterns(user_id))
            except Exception:
                pass  # Non-critical, don't block publish response
        
        return {"status": "posted", "post": post, "image_asset": image_asset, "account": linkedin_urn}
    
    except TokenNotFoundError as e:
        logger.warning("token_not_found", user_id=user_id, error=str(e))
        raise HTTPException(status_code=401, detail="LinkedIn not connected. Please reconnect your account.")
    
    except TokenRefreshError as e:
        logger.warning("token_refresh_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=401, detail="LinkedIn session expired. Please reconnect your account.")
    
    except AuthProviderError as e:
        logger.error("linkedin_api_unavailable", user_id=user_id, error=str(e))
        raise HTTPException(status_code=502, detail="LinkedIn is temporarily unavailable. Please try again later.")
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error("publish_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to publish post")


@router.post("/schedule")
async def schedule(
    req: ScheduleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Schedule a post for later publishing."""
    # Verify ownership
    if current_user and current_user.get("user_id") != req.user_id:
        raise HTTPException(status_code=403, detail="Cannot schedule posts for other users")
    
    if not schedule_post:
        raise HTTPException(status_code=500, detail="Schedule service not available")

    result = await schedule_post(
        user_id=req.user_id,
        post_content=req.post_content,
        scheduled_time=req.scheduled_time,
        image_url=req.image_url
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result

