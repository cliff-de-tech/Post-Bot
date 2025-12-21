#!/usr/bin/env node
/**
 * Generate TypeScript types from FastAPI OpenAPI specification
 * 
 * Usage: node scripts/generate-api-types.js
 * 
 * This script:
 * 1. Fetches the OpenAPI JSON from the backend
 * 2. Runs openapi-typescript to generate TypeScript definitions
 * 3. Outputs to shared/contracts/index.d.ts
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('http');

// Configuration
const API_URL = process.env.API_URL || 'http://localhost:8000';
const OPENAPI_ENDPOINT = '/openapi.json';
const OUTPUT_DIR = path.join(__dirname, '..', 'shared', 'contracts');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'index.d.ts');
const SPEC_CACHE_FILE = path.join(OUTPUT_DIR, 'openapi.json');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Fetch OpenAPI spec from the backend
 */
function fetchOpenAPISpec() {
    return new Promise((resolve, reject) => {
        const url = `${API_URL}${OPENAPI_ENDPOINT}`;
        console.log(`📡 Fetching OpenAPI spec from ${url}...`);

        const client = url.startsWith('https') ? require('https') : require('http');

        client.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    resolve(data);
                } else {
                    reject(new Error(`Failed to fetch OpenAPI spec: ${res.statusCode}`));
                }
            });
        }).on('error', reject);
    });
}

/**
 * Generate TypeScript types using openapi-typescript
 */
function generateTypes() {
    console.log('🔧 Generating TypeScript types...');

    try {
        execSync(
            `npx openapi-typescript "${SPEC_CACHE_FILE}" -o "${OUTPUT_FILE}"`,
            { stdio: 'inherit' }
        );
        console.log(`✅ Generated types at: ${OUTPUT_FILE}`);
    } catch (error) {
        console.error('❌ Failed to generate types:', error.message);
        process.exit(1);
    }
}

/**
 * Main execution
 */
async function main() {
    console.log('🚀 API Type Generator\n');

    try {
        // Try to fetch fresh spec from running backend
        const spec = await fetchOpenAPISpec();
        fs.writeFileSync(SPEC_CACHE_FILE, spec);
        console.log(`💾 Cached OpenAPI spec at: ${SPEC_CACHE_FILE}\n`);

        // Generate types
        generateTypes();

    } catch (error) {
        // If backend is not running, check for cached spec
        if (fs.existsSync(SPEC_CACHE_FILE)) {
            console.log('⚠️  Backend not available, using cached OpenAPI spec...\n');
            generateTypes();
        } else {
            console.error('❌ Error:', error.message);
            console.error('\n💡 Make sure the backend is running: cd backend && python app.py');
            process.exit(1);
        }
    }
}

main();
