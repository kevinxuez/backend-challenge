# API Routes Documentation

This document describes all available API endpoints for the Penn Club Review application.

## Base URL
All endpoints are prefixed with the base URL of your application.

## Authentication
Currently, no authentication is required for any endpoints.

## Response Format
All responses are in JSON format. Error responses follow this structure:
```json
{
  "error": "Error message description"
}
```

## Endpoints

### Root Endpoints

#### GET /
Returns a welcome message.
- **Response**: Plain text welcome message

#### GET /api
Returns a simple API greeting.
- **Response**: JSON greeting

---

## Club Endpoints

#### GET /api/clubs
Get all clubs.
- **Response**: Array of club objects

#### POST /api/clubs
Create a new club.
- **Request Body**:
  ```json
  {
    "code": "string (required, 2-50 chars, alphanumeric/hyphens/underscores)",
    "name": "string (required, 3-255 chars)",
    "description": "string (required, 10-2000 chars)",
    "tags": ["string"] (optional),
    "memberCount": "integer (optional, 0-100000)",
    "undergraduatesAllowed": "boolean (required)",
    "graduatesAllowed": "boolean (required)"
  }
  ```
- **Response**: Created club object (201) or validation error (400)

#### PUT /api/clubs/{clubCode}
Update an existing club.
- **Parameters**: `clubCode` (string) - The club's code
- **Request Body**: Any combination of club fields to update
- **Response**: Updated club object (200) or error (400/404)

#### DELETE /api/clubs/{clubCode}
Delete a club.
- **Parameters**: `clubCode` (string) - The club's code
- **Response**: Confirmation message (200) or error (400/404)

#### GET /api/clubs/search?query={searchTerm}
Search clubs by name.
- **Query Parameters**: 
  - `query` (required, 1-100 chars) - Search term
- **Response**: Array of matching club objects

#### GET /api/clubs/{clubCode}/favoritedBy
Get users who favorited a specific club.
- **Parameters**: `clubCode` (string) - The club's code
- **Response**: Object with club code and array of usernames

---

## User Endpoints

#### GET /api/users
Get all users.
- **Response**: Array of user objects

#### POST /api/users
Create a new user.
- **Request Body**:
  ```json
  {
    "username": "string (required, 3-50 chars)",
    "email": "string (required, valid email format)",
    "favorites": ["string"] (optional, array of club codes)
  }
  ```
- **Response**: Created user object (201) or validation error (400)

#### GET /api/users/{userId}
Get a specific user.
- **Parameters**: `userId` (integer) - The user's ID
- **Response**: User object (200) or error (404)

#### PUT /api/users/{userId}
Update an existing user.
- **Parameters**: `userId` (integer) - The user's ID
- **Request Body**: Any combination of user fields to update
- **Response**: Updated user object (200) or error (400/404)

#### DELETE /api/users/{userId}
Delete a user.
- **Parameters**: `userId` (integer) - The user's ID
- **Response**: Confirmation message (200) or error (404/500)

---

## Tag Endpoints

#### GET /api/tags/{tagName}
Get clubs associated with a specific tag.
- **Parameters**: `tagName` (string) - The tag name
- **Response**: Object with tag name and array of associated clubs

---

## Review Endpoints

#### GET /api/reviews
Get all reviews with pagination.
- **Query Parameters**:
  - `page` (optional, integer, default: 1) - Page number
  - `per_page` (optional, integer, default: 10, max: 100) - Items per page
- **Response**: Object with reviews array, total count, pages, and current page

#### POST /api/reviews
Create a new review.
- **Request Body**:
  ```json
  {
    "user_id": "integer (required)",
    "club_code": "string (required)",
    "rating": "integer (required, 1-10)",
    "title": "string (required, 5-100 chars)",
    "text": "string (optional, 0-2000 chars)"
  }
  ```
- **Response**: Created review object (201) or validation error (400)

#### GET /api/reviews/{reviewId}
Get a specific review.
- **Parameters**: `reviewId` (integer) - The review's ID
- **Response**: Review object (200) or error (404)

#### PUT /api/reviews/{reviewId}
Update an existing review.
- **Parameters**: `reviewId` (integer) - The review's ID
- **Request Body**: Any combination of review fields to update
- **Response**: Updated review object (200) or error (400/404)

#### DELETE /api/reviews/{reviewId}
Delete a review.
- **Parameters**: `reviewId` (integer) - The review's ID
- **Response**: Confirmation message (200) or error (404/500)

#### GET /api/clubs/{clubCode}/reviews
Get all reviews for a specific club.
- **Parameters**: `clubCode` (string) - The club's code
- **Query Parameters**:
  - `sort_by` (optional) - "rating" or "created_at" (default)
  - `order` (optional) - "asc" or "desc" (default)
  - `min_rating` (optional, integer) - Minimum rating filter
- **Response**: Array of review objects

#### GET /api/clubs/{clubCode}/reviews/stats
Get review statistics for a specific club.
- **Parameters**: `clubCode` (string) - The club's code
- **Response**: Object with statistics including total reviews, average rating, and rating distribution

#### GET /api/users/{userId}/reviews
Get all reviews written by a specific user.
- **Parameters**: `userId` (integer) - The user's ID
- **Response**: Array of review objects ordered by creation date (newest first)

#### GET /api/users/{userId}/reviews/{clubCode}
Get a user's review for a specific club.
- **Parameters**: 
  - `userId` (integer) - The user's ID
  - `clubCode` (string) - The club's code
- **Response**: Review object (200) or error (404)

---

## Data Models

### Club Object
```json
{
  "code": "string",
  "name": "string", 
  "description": "string",
  "tags": ["string"],
  "memberCount": "integer",
  "undergraduatesAllowed": "boolean",
  "graduatesAllowed": "boolean",
  "dateCreated": "string (ISO format)",
  "reviews_count": "integer",
  "average_rating": "float"
}
```

### User Object
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "favorites": ["string"],
  "reviews_count": "integer"
}
```

### Review Object
```json
{
  "id": "integer",
  "user_id": "integer",
  "club_code": "string",
  "rating": "integer",
  "title": "string",
  "text": "string",
  "created_at": "string (ISO format)",
  "updated_at": "string (ISO format)",
  "user_username": "string",
  "club_name": "string"
}
```

## Status Codes

- **200**: Success
- **201**: Created successfully
- **400**: Bad Request (validation error)
- **404**: Not Found
- **500**: Internal Server Error

## Validation Rules

### Club Code
- 2-50 characters
- Only letters, numbers, hyphens, and underscores
- Must be unique

### Username
- 3-50 characters
- HTML sanitized

### Email
- Must be valid email format
- Case insensitive

### Review Rating
- Integer between 1-10 (inclusive)

### Review Title
- 5-100 characters
- Required for all reviews

### Review Text
- 0-2000 characters
- Optional field