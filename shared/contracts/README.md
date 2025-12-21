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

The script will:
1. Fetch the OpenAPI spec from `http://localhost:8000/openapi.json`
2. Generate TypeScript definitions using `openapi-typescript`
3. Output to `shared/contracts/index.d.ts`

## Usage

```typescript
import type { paths, components } from '@/shared/contracts';

// Use generated types
type Post = components['schemas']['SavePostRequest'];
type GenerateResponse = paths['/api/post/generate-batch']['post']['responses']['200'];
```

## Files

| File | Description | Committed |
|------|-------------|-----------|
| `index.d.ts` | Generated TypeScript types | ❌ No |
| `openapi.json` | Cached OpenAPI spec | ❌ No |
| `README.md` | This documentation | ✅ Yes |

> ⚠️ Generated files are in `.gitignore`. Run `npm run generate:types` after cloning.

