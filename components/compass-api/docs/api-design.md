# API Design Document

## Overview

This document details the API design for the Tech Compass (TC) platform. The API follows RESTful principles and uses JSON for data exchange.

## 1. General Specifications

### 1.1 Base URL

- Development: `http://localhost:8000/api`
- Production: `https://api.techcompass.com/api`

### 1.2 Standard Response Format

```json
{
  "success": true|false,
  "data": {
    // Response data
  },
  "error": "string", // set if success is false, optional
  "total": 100, // only for list endpoints
  "skip": 0, // only for list endpoints
  "limit": 20, // only for list endpoints
}
```

### 1.3 HTTP Status Codes

Common HTTP status codes used in the API:

- 200: OK - Request successful
- 201: Created - Resource created successfully
- 204: No Content - Request successful, no content returned
- 400: Bad Request - Invalid request parameters
- 401: Unauthorized - Authentication required
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Resource not found
- 409: Conflict - Resource conflict (e.g., duplicate slug)
- 422: Unprocessable Entity - Validation error
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - Server error

### 1.4 Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      // Additional error details if available
    }
  }
}
```

### 1.5 Authentication

- JWT-based authentication
- Token included in Authorization header: `Authorization: Bearer <token>`
- Token expiration: 24 hours
- Refresh token mechanism for extended sessions
- Token endpoints:
  - POST /api/auth/login
  - POST /api/auth/refresh
  - POST /api/auth/logout

### 1.6 Rate Limiting

- Basic rate limiting: 100 requests per minute per IP
- Authenticated users: 1000 requests per minute
- Write operations: 50 requests per minute
- Rate limit headers included in response:
  - X-RateLimit-Limit
  - X-RateLimit-Remaining
  - X-RateLimit-Reset

## 2. API Endpoints

### 2.1 Solutions Management

#### List Solutions

```http
GET /api/solutions
```

Query Parameters:

- `page`: int (default: 1)
- `page_size`: int (default: 20, max: 100)
- `category`: string
- `status`: string
- `department`: string
- `search`: string (searches name and description)
- `tags`: array of tag IDs
- `sort_by`: string (name, created_at, status)
- `sort_order`: string (asc, desc)

Response:

```json
{
  "status": "success",
  "data": {
    "solutions": [
      {
        "id": "string",
        "slug": "string",
        "name": "string",
        "description": "string",
        "category": "string",
        "status": "string",
        "department": "string",
        "team": "string",
        "team_email": "string",
        "author_id": "string",
        "author_name": "string",
        "author_email": "string",
        "official_website": "string",
        "documentation_url": "string",
        "demo_url": "string",
        "version": "string",
        "pros": ["string"],
        "cons": ["string"],
        "development_status": "string",
        "recommend_status": "string",
        "created_at": "datetime",
        "created_by": "string",
        "updated_at": "datetime",
        "updated_by": "string"
      }
    ]
  },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

#### Get Solution Detail

```http
GET /api/solutions/{slug}
```

Example:
```http
GET /api/solutions/engineering-cloud-infrastructure-docker
```

Response:

```json
{
  "status": "success",
  "data": {
    "id": "string",
    "slug": "engineering-cloud-infrastructure-docker",
    "name": "Docker",
    "description": "string",
    "category": "string",
    "status": "string",
    "department": "Engineering",
    "team": "Cloud Infrastructure",
    "team_email": "string",
    "author_id": "string",
    "author_name": "string",
    "author_email": "string",
    "official_website": "string",
    "documentation_url": "string",
    "demo_url": "string",
    "version": "string",
    "pros": ["string"],
    "cons": ["string"],
    "development_status": "string",
    "recommend_status": "string",
    "created_at": "datetime",
    "created_by": "string",
    "updated_at": "datetime",
    "updated_by": "string",
    "tags": [
      {
        "id": "string",
        "name": "string"
      }
    ],
    "rating_summary": {
      "average": 4.5,
      "count": 100
    }
  }
}
```

#### Create Solution

```http
POST /api/solutions
```

Request Body:
```json
{
  "name": "Docker",
  "description": "Container platform",
  "category": "Container Platform",
  "status": "Active",
  "department": "Engineering",
  "team": "Cloud Infrastructure",
  "team_email": "cloud-infra@company.com",
  "official_website": "https://www.docker.com",
  "documentation_url": "https://docs.docker.com",
  "version": "24.0.7",
  "development_status": "Stable",
  "recommend_status": "Recommended"
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "string",
    "slug": "engineering-cloud-infrastructure-docker",
    "name": "Docker",
    // ... other fields
  }
}
```

Note: The `slug` field will be automatically generated from department, team, and name.

#### Update Solution

```http
PUT /api/solutions/{slug}
```

Example:
```http
PUT /api/solutions/engineering-cloud-infrastructure-docker
```

Request Body:
```json
{
  "name": "Docker",
  "description": "Updated description",
  // ... other fields
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": "string",
    "slug": "engineering-cloud-infrastructure-docker",
    // ... updated fields
  }
}
```

Note: When updating fields that affect the slug (department, team, or name), the slug will be automatically updated, and the old slug will be preserved for redirection.

#### Delete Solution

```http
DELETE /api/solutions/{slug}
```

Example:
```http
DELETE /api/solutions/engineering-cloud-infrastructure-docker
```

Response:
```json
{
  "status": "success",
  "data": {
    "message": "Solution deleted successfully"
  }
}
```

### 2.2 Ratings and Reviews

#### Get Solution Ratings

```http
GET /api/solutions/{slug}/ratings
```

Query Parameters:

- `page`: int
- `page_size`: int
- `sort_by`: string (score, created_at)
- `include_comments`: boolean

Response:

```json
{
  "status": "success",
  "data": {
    "ratings": [
      {
        "id": "string",
        "solution_slug": "string",
        "username": "string",
        "score": 5,
        "comment": "string",
        "created_at": "datetime",
        "created_by": "string",
        "updated_at": "datetime",
        "updated_by": "string"
      }
    ],
    "summary": {
      "average": 4.5,
      "count": 100,
      "distribution": {
        "1": 10,
        "2": 20,
        "3": 30,
        "4": 20,
        "5": 20
      }
    }
  },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

#### Get User Rating

```http
GET /api/solutions/{slug}/ratings/me
```

Response:

```json
{
  "status": "success",
  "data": {
    "id": "string",
    "solution_slug": "string",
    "username": "string",
    "score": 5,
    "comment": "string",
    "created_at": "datetime",
    "created_by": "string",
    "updated_at": "datetime",
    "updated_by": "string"
  }
}
```

#### Add or Update Rating

```http
POST /api/solutions/{slug}/ratings
```

Request Body:

```json
{
  "score": 5,
  "comment": "string"
}
```

Response:

```json
{
  "status": "success",
  "data": {
    "id": "string",
    "solution_slug": "string",
    "username": "string",
    "score": 5,
    "comment": "string",
    "created_at": "datetime",
    "created_by": "string",
    "updated_at": "datetime",
    "updated_by": "string"
  }
}
```

Notes:

- Each user can only have one active rating per solution
- If a user submits a new rating, it will update their existing rating
- Rating scores must be between 1 and 5 as integer, do not allow other rating scores
- Rating comment is optional

### 2.3 Comments Management

#### List Solution Comments

```http
GET /api/solutions/{slug}/comments
```

Query Parameters:

- `page`: int (default: 1)
- `page_size`: int (default: 20, max: 100)
- `sort_by`: string (created_at)
- `sort_order`: string (asc, desc)

Response:

```json
{
  "status": "success",
  "data": {
    "comments": [
      {
        "id": "string",
        "solution_id": "string",
        "content": "string",
        "user": {
          "id": "string",
          "username": "string",
          "email": "string"
        },
        "created_at": "datetime",
        "created_by": "string",
        "updated_at": "datetime",
        "updated_by": "string"
      }
    ]
  },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

#### Get Comment Detail

```http
GET /api/solutions/{slug}/comments/{comment_id}
```

Response:

```json
{
  "status": "success",
  "data": {
    "id": "string",
    "solution_id": "string",
    "content": "string",
    "user": {
      "id": "string",
      "username": "string",
      "email": "string"
    },
    "created_at": "datetime",
    "created_by": "string",
    "updated_at": "datetime",
    "updated_by": "string"
  }
}
```

#### Create Comment

```http
POST /api/solutions/{slug}/comments
```

Request Body:

```json
{
  "content": "string"
}
```

Response:

```json
{
  "status": "success",
  "data": {
    "id": "string",
    "solution_id": "string",
    "content": "string",
    "created_at": "datetime",
    "created_by": "string"
  }
}
```

#### Update Comment

```http
PUT /api/solutions/{slug}/comments/{comment_id}
```

Request Body:

```json
{
  "content": "string"
}
```

Note: Only the comment author can update their own comments.

#### Delete Comment

```http
DELETE /api/solutions/{slug}/comments/{comment_id}
```

Note: Only the comment author or solution administrators can delete comments.

### 2.4 Categories and Tags

#### List Categories

```http
GET /api/categories
```

Response:

```json
{
  "status": "success",
  "data": {
    "categories": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "parent_id": "string",
        "children": [
          // Nested categories if include_children=true
        ]
      }
    ]
  }
}
```

#### List Tags

```http
GET /api/tags
```

Response:

```json
{
  "status": "success",
  "data": {
    "tags": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "usage_count": 10
      }
    ]
  }
}
```

### 2.8 Site Configuration

#### Get Site Configuration

```http
GET /api/site-config
```

Response:

```json
{
  "status": "success",
  "data": {
    "site_name": "Tech Compass Library",
    "site_logo": "/assets/images/logo.png",
    "site_headline": "Discover and Share Tech Solutions",
    "support_team": "TCL Support Team",
    "support_email": "support@techcompass.com",
    "about_info": "A comprehensive tech solutions library...",
    "features": {
      "enable_comments": true,
      "enable_ratings": true
    },
    "meta": {
      "title": "Tech Compass Library",
      "description": "Find the best tech solutions...",
      "keywords": ["tech", "solutions"]
    },
    "created_at": "2025-01-18T03:46:15Z",
    "updated_at": "2025-01-18T03:46:15Z"
  }
}
```

#### Update Site Configuration

```http
PUT /api/site-config
```

Request Body:

```json
{
  "site_name": "Tech Compass Library",
  "site_logo": "/assets/images/logo.png",
  "site_headline": "Discover and Share Tech Solutions",
  "support_team": "TCL Support Team",
  "support_email": "support@techcompass.com",
  "about_info": "A comprehensive tech solutions library...",
  "features": {
    "enable_comments": true,
    "enable_ratings": true
  },
  "meta": {
    "title": "Tech Compass Library",
    "description": "Find the best tech solutions...",
    "keywords": ["tech", "solutions"]
  }
}
```

Response:

```json
{
  "status": "success",
  "data": {
    "site_name": "Tech Compass Library",
    "site_logo": "/assets/images/logo.png",
    "site_headline": "Discover and Share Tech Solutions",
    "support_team": "TCL Support Team",
    "support_email": "support@techcompass.com",
    "about_info": "A comprehensive tech solutions library...",
    "features": {
      "enable_comments": true,
      "enable_ratings": true
    },
    "meta": {
      "title": "Tech Compass Library",
      "description": "Find the best tech solutions...",
      "keywords": ["tech", "solutions"]
    },
    "created_at": "2025-01-18T03:46:15Z",
    "updated_at": "2025-01-18T03:46:15Z"
  }
}
```

Notes:
- The GET endpoint is public and does not require authentication
- The PUT endpoint requires admin authentication
- Cache-Control headers are included to optimize UI performance:
  - GET response includes: `Cache-Control: public, max-age=300`
  - After PUT, cache is invalidated using cache-busting techniques

## 3. Security Considerations

### 3.1 Authentication and Authorization

- All modification endpoints require authentication
- Role-based access control (RBAC) for sensitive operations
- Token expiration and refresh mechanism
- HTTPS required for all API calls

### 3.2 Data Validation

- Input validation on all endpoints
- Request size limits
- Content type verification
- XSS protection
- SQL injection protection

### 3.3 Security Headers

- CORS configuration
- Content Security Policy
- XSS Protection
- Rate Limiting Headers
- HSTS (HTTP Strict Transport Security)

## 4. API Documentation

- OpenAPI/Swagger documentation available at `/api/docs`
- Interactive documentation with try-it-now functionality
- Code examples in multiple languages
- Authentication examples included
