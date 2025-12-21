# Shared API Contracts

This directory contains TypeScript types auto-generated from the FastAPI OpenAPI specification.

## Purpose

- **Type Safety**: Ensures frontend API calls match backend schemas
- **Auto-generated**: Types are generated from `/openapi.json`
- **Single Source of Truth**: Backend schemas define the contract

## Regenerating Types

Run the generation script from the project root:

```bash
npm run generate:types
```

Or manually:

```bash
# Ensure backend is running
curl http://localhost:8000/openapi.json > shared/contracts/openapi.json

# Generate TypeScript types (requires openapi-typescript)
npx openapi-typescript shared/contracts/openapi.json -o shared/contracts/api.ts
```

## Usage

```typescript
import type { paths, components } from '@/shared/contracts/api';

// Use generated types
type Post = components['schemas']['SavePostRequest'];
type GenerateResponse = paths['/api/post/generate-batch']['post']['responses']['200'];
```

## Files

| File | Description |
|------|-------------|
| `api.ts` | Generated TypeScript types (do not edit manually) |
| `openapi.json` | Cached OpenAPI spec (auto-updated) |
| `README.md` | This file |

> ⚠️ Files in this directory (except README.md) are auto-generated. Do not edit manually.
