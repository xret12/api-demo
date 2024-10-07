# API Authentication with FastAPI

This project contains three FastAPI applications demonstrating different types of authentication methods:

1. **No Authentication** (`server_no_auth.py`)
2. **Basic Authentication** (`server_basic_auth.py`)
3. **JWT Token Authentication** (`server_token_auth.py`)

## Table of Contents

- [Overview](#overview)
- [Authentication Types](#authentication-types)
  - [No Authentication](#no-authentication)
  - [Basic Authentication](#basic-authentication)
  - [JWT Token Authentication](#jwt-token-authentication)
- [How to Use](#how-to-use)
  - [Running the Applications](#running-the-applications)
  - [Testing with Postman](#testing-with-postman)
- [Comparison of Authentication Types](#comparison-of-authentication-types)
- [Security Considerations](#security-considerations)

## Overview

This project showcases different authentication strategies in FastAPI, each suited for specific scenarios depending on the application's security requirements.

- **No Authentication**: Suitable for open APIs or when no user-specific access control is required.
- **Basic Authentication**: Easy to implement and suitable for internal applications with simple authentication needs.
- **JWT Token Authentication**: Ideal for scalable, stateless applications that require secure and efficient token-based authentication.

## Authentication Types

### No Authentication

The application in `server_no_auth.py` does not use any authentication mechanism. All endpoints are accessible to any user or client without credentials.

- **Use Case**: Public APIs, open data services, or when no sensitive information is involved.
- **Advantages**: Simple and fast; no overhead of managing authentication.

### Basic Authentication

The application in `server_basic_auth.py` uses HTTP Basic Authentication, where users provide a username and password with each request. The credentials are validated against environment variables.

- **Use Case**: Internal services, simple applications where users trust the environment.
- **Advantages**: Easy to implement.
- **Disadvantages**: Less secure, as credentials are transmitted with each request and are prone to interception if not using HTTPS.

#### Implementation Details:

- Uses `HTTPBasic` from FastAPI's security module.
- Verifies credentials using environment variables.

### JWT Token Authentication

The application in `server_token_auth.py` uses JWT (JSON Web Tokens) for authentication. Users authenticate using their credentials to receive a token, which is then used to access protected routes.

- **Use Case**: Stateless APIs, microservices, and applications needing secure token-based authentication.
- **Advantages**: Scalable, secure, and does not require server-side session storage.
- **Disadvantages**: Slightly more complex to implement and manage.

#### Implementation Details:

- Uses `OAuth2PasswordBearer` for obtaining tokens.
- Tokens are signed with a secret key, ensuring they cannot be tampered with.

## How to Use

### Running the Applications

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** for `server_basic_auth.py` and `server_token_auth.py`:
   ```bash
   APP_USERNAME="your_username"
   APP_PASSWORD="your_password"
   SECRET_KEY="your_secret_key"
   ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   HASHED_PASSWORD="$2b$12$hashed_password_here" # Use a bcrypt-hashed password
   ```
   For the hashed password, you can use the `get_password_hash()` function from `server_token_auth.py` to hash your preferred password.
3. **Start the server**:
   ```bash
   fastapi run <file.py>
   ```

### Testing with Postman

#### No Authentication

1. Make a request to any endpoint without sending any credentials.
2. Example URL: `http://127.0.0.1:8000/items/1`

#### Basic Authentication

1. Set the request to use `Basic Auth` (dropdown option located `Authorization` tab) in Postman.
2. Enter the username and password specified in your environment variables.
3. Send a request to the protected endpoint, e.g., `http://127.0.0.1:8000/items/1`.

#### JWT Token Authentication

1. **Obtain a Token**:
   - Make a POST request to `/token` with `x-www-form-urlencoded` body parameters:
     - `username`: Your username
     - `password`: Your password
2. Use the returned `access_token` to access protected routes by setting it as a `Bearer Token` in the Authorization header of your requests.
3. Example URL: `http://127.0.0.1:8000/items/1`

## Comparison of Authentication Types

| Feature                       | No Authentication | Basic Authentication | JWT Token Authentication     |
| ----------------------------- | ----------------- | -------------------- | ---------------------------- |
| **Security**                  | None              | Low                  | High                         |
| **Scalability**               | High              | Medium               | Very High                    |
| **Implementation Complexity** | Very Low          | Low                  | Moderate                     |
| **Statefulness**              | Stateless         | Stateless            | Stateless                    |
| **Use Cases**                 | Public APIs       | Internal tools       | Scalable APIs, Microservices |

## Security Considerations

1. **Always use HTTPS**: To protect against man-in-the-middle attacks, especially when using Basic Authentication and JWT. For demonstration purposes, the use of HTTP will suffice.
2. **Use strong secret keys**: For signing JWT tokens, use long and randomly generated secret keys.
3. **Token expiration**: Ensure JWT tokens have an expiration time to reduce the risk of compromised tokens being used.
4. **Rotate credentials**: Regularly update passwords and secret keys to enhance security.
