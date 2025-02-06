# Database Design Document

## Overview

This document details the MongoDB collections and their schemas for the Tech Compass (TC) platform. All collections use MongoDB's default `_id` field as the primary key.

## Audit Fields

All collections include the following audit fields for tracking purposes:

| Field      | Type     | Description                   |
| ---------- | -------- | ----------------------------- |
| created_at | DateTime | When the record was created   |
| created_by | ObjectId | Who created the record        |
| updated_at | DateTime | When last updated             |
| updated_by | ObjectId | Who performed the last update |

## Collections

### 1. Solutions Collection

Stores the main technical solution information.

| Field              | Type          | Description                                                | Example                                                                                    |
| ------------------ | ------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| \_id               | ObjectId      | Unique identifier                                          | "507f1f77bcf86cd799439011"                                                                 |
| name               | String        | Solution name                                              | "Docker"                                                                                   |
| slug               | String        | Unique, human-readable identifier (auto-generated)         | "engineering-cloud-infrastructure-docker"                                                   |
| description        | String        | Detailed description                                       | "Docker is a platform for developing, shipping, and running applications in containers..." |
| category           | String        | Primary category                                           | "Container Platform"                                                                       |
| status             | String        | Current status                                             | "Recommended"                                                                              |
| department         | String        | Department name                                            | "Engineering"                                                                              |
| team               | String        | Team name                                                  | "Cloud Infrastructure"                                                                     |
| team_email         | String        | Team contact email                                         | "cloud-infra@company.com"                                                                  |
| author_id          | ObjectId      | Original author's user ID                                  | "507f1f77bcf86cd799439014"                                                                 |
| author_name        | String        | Original author's name                                     | "Jane Smith"                                                                               |
| author_email       | String        | Original author's email                                    | "jane.smith@company.com"                                                                   |
| official_website   | String        | Official website URL                                       | "https://www.docker.com"                                                                   |
| documentation_url  | String        | Documentation URL                                          | "https://docs.docker.com"                                                                  |
| demo_url           | String        | Demo/POC URL                                               | "https://demo.docker.company.com"                                                          |
| version            | String        | Current version                                            | "24.0.7"                                                                                   |
| pros               | Array[String] | List of advantages                                         | ["Easy to deploy", "Good documentation"]                                                   |
| cons               | Array[String] | List of disadvantages                                      | ["Resource overhead", "Learning curve"]                                                    |
| development_status | String        | Development phase status                                   | "RC"                                                                                       |
| recommend_status   | String        | Strategic recommendation                                   | "BUY"                                                                                      |
| created_at         | DateTime      | Creation timestamp                                         | "2024-03-15T10:30:00Z"                                                                     |
| created_by         | ObjectId      | Reference to users collection                              | "507f1f77bcf86cd799439012"                                                                 |
| updated_at         | DateTime      | Last update timestamp                                      | "2024-03-16T14:20:00Z"                                                                     |
| updated_by         | ObjectId      | User who last updated                                      | "507f1f77bcf86cd799439013"                                                                 |

### 2. Tags Collection

Stores tags for categorizing solutions.

| Field       | Type     | Description        | Example                                     |
| ----------- | -------- | ------------------ | ------------------------------------------- |
| \_id        | ObjectId | Unique identifier  | "507f1f77bcf86cd799439013"                  |
| name        | String   | Tag name           | "Containerization"                          |
| description | String   | Tag description    | "Technologies related to container systems" |
| created_at  | DateTime | Creation timestamp | "2024-03-15T10:30:00Z"                      |
| created_by  | ObjectId | User who created   | "507f1f77bcf86cd799439012"                  |
| updated_at  | DateTime | Last update time   | "2024-03-16T14:20:00Z"                      |
| updated_by  | ObjectId | User who updated   | "507f1f77bcf86cd799439013"                  |

### 3. SolutionTags Collection

Maps solutions to tags (many-to-many relationship).

| Field       | Type     | Description            | Example                    |
| ----------- | -------- | ---------------------- | -------------------------- |
| \_id        | ObjectId | Unique identifier      | "507f1f77bcf86cd799439014" |
| solution_id | ObjectId | Reference to solutions | "507f1f77bcf86cd799439011" |
| tag_id      | ObjectId | Reference to tags      | "507f1f77bcf86cd799439013" |
| created_at  | DateTime | Creation timestamp     | "2024-03-15T10:30:00Z"     |
| created_by  | ObjectId | User who created       | "507f1f77bcf86cd799439012" |
| updated_at  | DateTime | Last update time       | "2024-03-16T14:20:00Z"     |
| updated_by  | ObjectId | User who updated       | "507f1f77bcf86cd799439013" |

### 4. Categories Collection

Stores solution categories.

| Field       | Type     | Description               | Example                              |
| ----------- | -------- | ------------------------- | ------------------------------------ |
| \_id        | ObjectId | Unique identifier         | "507f1f77bcf86cd799439015"           |
| name        | String   | Category name             | "Development Tools"                  |
| description | String   | Category description      | "Tools used in software development" |
| parent_id   | ObjectId | Parent category reference | null                                 |
| created_at  | DateTime | Creation timestamp        | "2024-03-15T10:30:00Z"               |
| created_by  | ObjectId | User who created          | "507f1f77bcf86cd799439012"           |
| updated_at  | DateTime | Last update time          | "2024-03-16T14:20:00Z"               |
| updated_by  | ObjectId | User who updated          | "507f1f77bcf86cd799439013"           |

### 5. Ratings Collection

Stores user ratings for solutions.

| Field           | Type     | Description            | Example                              |
| --------------- | -------- | ---------------------- | ------------------------------------ |
| \_id            | ObjectId | Unique identifier      | "507f1f77bcf86cd799439016"           |
| solution_id     | ObjectId | Reference to solutions | "507f1f77bcf86cd799439011"           |
| user_id         | ObjectId | Reference to users     | "507f1f77bcf86cd799439012"           |
| score           | Number   | Rating score (1-5)     | 4                                    |
| created_at      | DateTime | Creation timestamp     | "2024-03-15T10:30:00Z"               |
| updated_at      | DateTime | Last update timestamp  | "2024-03-16T14:20:00Z"               |
| comment         | String   | Rating comment         | "Great performance in production"    |
| previous_scores | Array    | History of scores      | [3, 4]                               |
| update_history  | Array    | History of updates     | [{                                   |
|                 |          |                        | "score": 3,                          |
|                 |          |                        | "timestamp": "2024-03-15T10:30:00Z", |
|                 |          |                        | "comment": "Initial rating"          |
|                 |          |                        | }]                                   |

### 6. Comments Collection

Stores user comments on solutions.

| Field       | Type     | Description            | Example                           |
| ----------- | -------- | ---------------------- | --------------------------------- |
| \_id        | ObjectId | Unique identifier      | "507f1f77bcf86cd799439017"        |
| solution_id | ObjectId | Reference to solutions | "507f1f77bcf86cd799439011"        |
| user_id     | ObjectId | Reference to users     | "507f1f77bcf86cd799439012"        |
| content     | String   | Comment text           | "Great tool for containerization" |
| created_at  | DateTime | Creation timestamp     | "2024-03-15T10:30:00Z"            |
| updated_at  | DateTime | Last update timestamp  | "2024-03-15T10:30:00Z"            |
| created_by  | ObjectId | User who created       | "507f1f77bcf86cd799439012"        |
| updated_by  | ObjectId | User who updated       | "507f1f77bcf86cd799439013"        |

### 7. Users Collection

Stores user information.

| Field         | Type     | Description          | Example                    |
| ------------- | -------- | -------------------- | -------------------------- |
| \_id          | ObjectId | Unique identifier    | "507f1f77bcf86cd799439012" |
| username      | String   | Username             | "john_doe"                 |
| email         | String   | Email address        | "john@example.com"         |
| password_hash | String   | Hashed password      | "hash_value_here"          |
| role          | String   | User role            | "admin"                    |
| created_at    | DateTime | Creation timestamp   | "2024-03-15T10:30:00Z"     |
| last_login    | DateTime | Last login timestamp | "2024-03-16T14:20:00Z"     |
| created_by    | ObjectId | User who created     | "507f1f77bcf86cd799439012" |
| updated_at    | DateTime | Last update time     | "2024-03-16T14:20:00Z"     |
| updated_by    | ObjectId | User who updated     | "507f1f77bcf86cd799439013" |

### 8. Links Collection

Stores related links for solutions.

| Field       | Type     | Description            | Example                                           |
| ----------- | -------- | ---------------------- | ------------------------------------------------- |
| \_id        | ObjectId | Unique identifier      | "507f1f77bcf86cd799439018"                        |
| solution_id | ObjectId | Reference to solutions | "507f1f77bcf86cd799439011"                        |
| title       | String   | Link title             | "Docker Best Practices"                           |
| url         | String   | Link URL               | "https://docs.docker.com/develop/best-practices/" |
| type        | String   | Link type              | "documentation"                                   |
| created_at  | DateTime | Creation timestamp     | "2024-03-15T10:30:00Z"                            |
| created_by  | ObjectId | User who created       | "507f1f77bcf86cd799439012"                        |
| updated_at  | DateTime | Last update time       | "2024-03-16T14:20:00Z"                            |
| updated_by  | ObjectId | User who updated       | "507f1f77bcf86cd799439013"                        |

### 9. Articles Collection

Stores additional information for solutions.

| Field        | Type     | Description             | Example                                         |
| ------------ | -------- | ----------------------- | ----------------------------------------------- |
| \_id         | ObjectId | Unique identifier       | "507f1f77bcf86cd799439019"                      |
| solution_id  | ObjectId | Reference to solutions  | "507f1f77bcf86cd799439011"                      |
| type         | String   | Info type               | "case_study"                                    |
| title        | String   | Info title              | "Docker at Netflix"                             |
| content      | String   | Detailed content        | "Netflix uses Docker for..."                    |
| link         | String   | Related URL             | "https://netflixtechblog.com/docker-at-netflix" |
| author_id    | ObjectId | Original author's ID    | "507f1f77bcf86cd799439014"                      |
| author_name  | String   | Original author's name  | "Jane Smith"                                    |
| author_email | String   | Original author's email | "jane.smith@company.com"                        |
| created_at   | DateTime | Creation timestamp      | "2024-03-15T10:30:00Z"                          |
| created_by   | ObjectId | Reference to users      | "507f1f77bcf86cd799439012"                      |
| updated_at   | DateTime | Last update time        | "2024-03-16T14:20:00Z"                          |
| updated_by   | ObjectId | User who updated        | "507f1f77bcf86cd799439013"                      |

### 10. Site Configurations Collection

Stores site-wide configuration settings.

| Field         | Type          | Description                                | Example                                    |
| ------------- | ------------- | ------------------------------------------ | ------------------------------------------ |
| _id           | ObjectId      | Unique identifier                          | "507f1f77bcf86cd799439011"                |
| site_name     | String        | Name of the site                          | "Tech Compass Library"                   |
| site_logo     | String        | URL or path to site logo                  | "/assets/images/logo.png"                  |
| site_headline | String        | Main headline or tagline                  | "Discover and Share Tech Solutions"        |
| support_team  | String        | Name of the support team                  | "TC Support Team"                         |
| support_email | String        | Support team email                        | "support@techcompass.com"                |
| about_info    | String        | Site description or about information      | "A comprehensive tech solutions library..." |
| features      | Object        | Feature flags and configurations           | {                                          |
|               |               |                                            |   "enable_comments": true,                 |
|               |               |                                            |   "enable_ratings": true                   |
|               |               |                                            | }                                          |
| meta          | Object        | SEO and meta information                  | {                                          |
|               |               |                                            |   "title": "Tech Compass Library",       |
|               |               |                                            |   "description": "Find the best tech...",  |
|               |               |                                            |   "keywords": ["tech", "solutions"]        |
|               |               |                                            | }                                          |
| created_at    | DateTime      | Creation timestamp                         | "2025-01-18T03:42:37Z"                    |
| created_by    | ObjectId      | Reference to users collection              | "507f1f77bcf86cd799439012"                |
| updated_at    | DateTime      | Last update timestamp                      | "2025-01-18T03:42:37Z"                    |
| updated_by    | ObjectId      | User who last updated                      | "507f1f77bcf86cd799439013"                |

## Indexes

### Required Indexes

1. Solutions Collection:

   - name (unique)
   - category
   - status
   - created_at
   - slug (unique)

2. Tags Collection:

   - name (unique)

3. Categories Collection:

   - name (unique)
   - parent_id

4. Ratings Collection:

   - solution_id
   - user_id
   - created_at
   - Compound index: [solution_id, user_id] (unique)
   - Compound index: [solution_id, score]

5. Comments Collection:

   - solution_id
   - user_id
   - created_at

6. Users Collection:

   - username (unique)
   - email (unique)

7. Links Collection:
   - solution_id
   - type

8. Site Configurations Collection:
   - site_name (unique)
   - created_at

## Data Relationships

- Solutions -> Categories (Many-to-One)
- Solutions -> Tags (Many-to-Many through SolutionTags)
- Solutions -> Ratings (One-to-Many)
- Solutions -> Comments (One-to-Many)
- Solutions -> Links (One-to-Many)
- Solutions -> Articles (One-to-Many)
- Categories -> Categories (Self-referential for hierarchy)

## Enums and Constants

### Development Status Values

- `DEVELOPING` - Solution is under active development
- `RC` - Release Candidate
- `EOVS` - End of Vendor Support
- `ACTIVE` - Actively used in production
- `DEPRECATED` - No longer recommended for new projects
- `RETIRED` - Completely phased out

### Recommend Status Values

- `BUY` - Recommended for new projects and expansion
- `HOLD` - Maintain existing usage, but don't expand
- `SELL` - Plan for replacement/retirement
