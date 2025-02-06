# Tech Solutions API Guide

This document provides a comprehensive guide to the Tech Solutions API endpoints.

## Base URL

```
http://localhost:8000/api
```

## Authentication

### Login

```http
POST /auth/login
```

Authenticate a user and receive an access token.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Using Authentication

Include the access token in the Authorization header for protected endpoints:

```
Authorization: Bearer {access_token}
```

## Solutions

### Search Solutions

```http
GET /api/solutions/search
```

Search solutions using text similarity across multiple fields.

**Query Parameters:**

- `keyword` (string, required): Search keyword

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "_id": "956fDdc25eFF7aDcEc5cb5AE",
      "created_at": "2025-02-04T03:55:44.626Z",
      "created_by": "string",
      "updated_at": "2025-02-04T03:55:44.626Z",
      "updated_by": "string",
      "name": "string",
      "description": "string",
      "brief": "string",
      "logo": "",
      "category": "string",
      "department": "string",
      "team": "string",
      "team_email": "string",
      "maintainer_id": "string",
      "maintainer_name": "string",
      "maintainer_email": "string",
      "official_website": "string",
      "documentation_url": "string",
      "demo_url": "string",
      "version": "string",
      ...
    }
  ],
  "detail": "string",
  "total": 0,
  "skip": 0,
  "limit": 0
}
```

Results are sorted by relevance score, with higher weights given to matches in more important fields.

### List Solutions

```http
GET /solutions
```

Get a paginated list of solutions with optional filtering.

**Query Parameters:**

- `page` (integer, default: 1): Page number
- `limit` (integer, default: 10): Items per page
- `category` (string, optional): Filter by category
- `department` (string, optional): Filter by department
- `team` (string, optional): Filter by team
- `recommend_status` (string, optional): Filter by recommendation status (ADOPT/TRIAL/ASSESS/HOLD)
- `stage` (string, optional): Filter by stage (DEVELOPING/UAT/PRODUCTION/DEPRECATED/RETIRED)

### Get Solution

```http
GET /solutions/{slug}
```

Get detailed information about a specific solution.

### Create Solution

```http
POST /solutions
```

Create a new solution. Requires authentication.

**Request Body:**

```json
{
  "name": "string (required)",
  "description": "string (required)",
  "brief": "string (required, max 200 chars)",
  "category": "string",
  "department": "string (required)",
  "team": "string (required)",
  "recommend_status": "string",
  "stage": "string",
  "maintainer_id": "string",
  "maintainer_name": "string",
  "maintainer_email": "string",
  "adoption_level": "string (PILOT/TEAM/DEPARTMENT/ENTERPRISE/INDUSTRY)",
  "adoption_user_count": "integer (>= 0)",
  "tags": ["string"]
}
```

### Update Solution

```http
PUT /solutions/{slug}
```

Update an existing solution. Requires authentication.

## Tags

### List Tags

```http
GET /tags
```

Get a list of all tags.

### Create Tag

```http
POST /tags
```

Create a new tag. Requires authentication.

**Request Body:**

```json
{
  "name": "string",
  "description": "string"
}
```

### Update Tag

```http
PUT /tags/{name}
```

Update a tag. Requires authentication. Will also update the tag name in all solutions using it.

### Delete Tag

```http
DELETE /tags/{name}
```

Delete a tag. Requires authentication. Cannot delete tags that are in use by solutions.

### Get Solution Tags

```http
GET /tags/solution/{solution_slug}
```

Get all tags for a specific solution.

### Add Tag to Solution

```http
POST /tags/solution/{solution_slug}/tag/{tag_name}
```

Add a tag to a solution. Creates the tag if it doesn't exist.

### Remove Tag from Solution

```http
DELETE /tags/solution/{solution_slug}/tag/{tag_name}
```

Remove a tag from a solution.

## Categories

### List Categories

```http
GET /categories
```

Get a list of all categories.

### Create Category

```http
POST /categories
```

Create a new category. Requires authentication.

**Request Body:**

```json
{
  "name": "string",
  "description": "string"
}
```

### Update Category

```http
PUT /categories/{name}
```

Update a category. Requires authentication.

### Delete Category

```http
DELETE /categories/{name}
```

Delete a category. Requires authentication. Cannot delete categories that are in use by solutions.

## Ratings

### Get Solution Ratings

```http
GET /ratings/solution/{solution_slug}
```

Get all ratings for a solution.

**Query Parameters:**

- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20): Items per page
- `sort_by` (string, default: "created_at"): Field to sort by

### Get User Rating

```http
GET /ratings/solution/{solution_slug}/me
```

Get the current user's rating for a solution. Requires authentication.

### Create/Update Rating

```http
POST /ratings/solution/{solution_slug}
```

Create or update a rating for a solution. Requires authentication.

**Request Body:**

```json
{
  "score": "integer (1-5)",
  "comment": "string (optional)"
}
```

### Get Rating Summary

```http
GET /ratings/solution/{solution_slug}/summary
```

Get rating summary statistics for a solution.

## Comments

### Get Solution Comments

```http
GET /comments/solution/{solution_slug}
```

Get all comments for a solution.

**Query Parameters:**

- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20): Items per page
- `sort_by` (string, default: "created_at"): Field to sort by (comments are sorted by created_at desc by default)

### Create Comment

```http
POST /comments/solution/{solution_slug}
```

Create a new comment for a solution. Requires authentication.

**Request Body:**

```json
{
  "content": "string (1-1000 characters)"
}
```

### Update Comment

```http
PUT /comments/solution/{solution_slug}/comment/{comment_id}
```

Update a comment. Requires authentication. Only the comment author can update it.

**Request Body:**

```json
{
  "content": "string (1-1000 characters)"
}
```

### Delete Comment

```http
DELETE /comments/solution/{solution_slug}/comment/{comment_id}
```

Delete a comment. Requires authentication. Only the comment author can delete it.

## Response Format

Most endpoints return responses in the following format:

**Success Response:**

```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "meta": {
    // Pagination metadata (if applicable)
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

**Error Response:**

```json
{
  "detail": "Error message"
}
```

## HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Site Configuration

### Get Site Config

```http
GET /site-config
```

Get the current site configuration. This endpoint is public and does not require authentication.

### Create Site Config

```http
POST /site-config
```

Create initial site configuration. Requires authentication. Can only be called once when no configuration exists.

**Request Body:**

```json
{
  "site_name": "string",
  "site_description": "string",
  "welcome_message": "string",
  "contact_email": "string",
  "features": {
    "ratings_enabled": true,
    "comments_enabled": true,
    "tags_enabled": true
  },
  "custom_links": [
    {
      "title": "string",
      "url": "string",
      "icon": "string"
    }
  ],
  "theme": {
    "primary_color": "#1890ff",
    "secondary_color": "#52c41a",
    "layout": "default"
  },
  "meta": {
    "keywords": ["string"],
    "author": "string",
    "favicon": "string"
  }
}
```

### Update Site Config

```http
PUT /site-config
```

Update site configuration. Requires authentication. Only updates the fields that are provided.

**Request Body:**

```json
{
  "site_name": "string",
  "site_description": "string",
  "welcome_message": "string",
  "contact_email": "string",
  "features": {},
  "custom_links": [],
  "theme": {},
  "meta": {}
}
```

All fields are optional. Only include the fields you want to update.

### Reset Site Config

```http
POST /site-config/reset
```

Reset site configuration to default values. Requires authentication.
