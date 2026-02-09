# Multi-stage Dockerfile for Next.js Frontend
# Optimized for production deployment with standalone output
# Final image size: ~150MB (vs ~1GB without optimization)

# ============================================================================
# Stage 1: Dependencies
# Purpose: Install production dependencies only for final image
# Optimization: Separating deps stage allows Docker to cache this layer
# ============================================================================
FROM node:20-alpine AS deps

# Alpine Linux provides minimal base image (~5MB vs ~900MB for full node image)
# node:20-alpine includes Node.js 20 LTS with npm

WORKDIR /app

# Copy only package files first to leverage Docker layer caching
# If package.json hasn't changed, Docker reuses cached dependencies
COPY package.json package-lock.json* ./

# npm ci (clean install) is faster and more reliable than npm install
# --only=production excludes devDependencies, reducing image size
# This stage's output is used in the final runner stage
RUN npm ci --only=production

# ============================================================================
# Stage 2: Builder
# Purpose: Build the Next.js application with all dependencies
# Optimization: Separate build stage keeps build tools out of final image
# ============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install ALL dependencies (including devDependencies needed for build)
# TypeScript, build tools, etc. are required here but not in final image
RUN npm ci

# Copy all source code
# Done after npm ci to maximize cache hits (source changes more often than deps)
COPY . .

# Disable Next.js telemetry for privacy and faster builds
ENV NEXT_TELEMETRY_DISABLED 1

# Build Next.js application with standalone output mode
# Standalone output includes only necessary files (~50MB vs ~500MB full build)
# next.config.js must have: output: 'standalone'
# This creates a minimal server.js with required dependencies
RUN npm run build

# ============================================================================
# Stage 3: Runner (Final Image)
# Purpose: Minimal production image with only runtime dependencies
# Optimization: Only includes built app and production dependencies
# ============================================================================
FROM node:20-alpine AS runner

WORKDIR /app

# Set production environment
# NODE_ENV=production enables optimizations and disables dev features
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user for security best practices
# Running as root is a security risk; non-root limits potential damage
# GID 1001 and UID 1001 are arbitrary but consistent with Kubernetes practices
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy standalone server and static files from builder stage
# --chown sets ownership to nextjs user immediately (more efficient than chown later)
# Standalone output includes only necessary node_modules (tree-shaken)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./

# Copy static assets (JS, CSS, images) generated during build
# These are served by Next.js server and must be in .next/static
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copy public directory (favicon, robots.txt, etc.)
# Public files are served at root path by Next.js
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Switch to non-root user
# All subsequent commands and the container runtime use this user
USER nextjs

# Expose port 3000
# This is documentation only; doesn't actually publish the port
# Kubernetes Service configuration determines actual port mapping
EXPOSE 3000

# Set port environment variable for Next.js server
ENV PORT 3000
# HOSTNAME 0.0.0.0 allows connections from outside the container
# Required for Kubernetes pod networking
ENV HOSTNAME "0.0.0.0"

# Start the application
# Standalone output creates a minimal server.js that starts Next.js
# This is much faster than 'npm start' (no npm overhead)
CMD ["node", "server.js"]
