<h1>A simple Helath Tracker API example</h1>



**<u>Todo list:</u>**
- [x] Create skeleton for API
- [X] Create SQL Schema
- [X] Complete API with CRUD operations for all dbs in the schema
  - [X] Users
  - [X] Physical
  - [X] Blood
  - [X] Sleep
- [X] Create the get_health_score endpoint
- [X] Add Security comments
- [X] Test with pytest
  - [X] Simple CRUD operations
  - [X] Complex CRUD operations
  - [X] Health Score
- [X] Final passthrough and refactoring for readability
- [X] Answer Theoretical Questions

# Notes:
This API does not include security measures, as it is intended as a simplified example. Properly implementing security
features would go beyond the scope of this demonstration and might obscure the core objectives of this example.
However, in a real-world application, security would be a critical component.
 To illustrate best practices, I will include comments indicating where security measures should be integrated.
Key Security Considerations for a Production Environment:

1. Authentication: Users should be required to authenticate before accessing their data. 
    This can be implemented using a third-party authentication provider, such as OAuth2,
    or a custom authentication system that supports username-password logins with secure token-based access
    (e.g., JWT or session tokens).
2. Authorization: Each endpoint should enforce authorization checks to ensure that users can only access or 
    modify data they are permitted to. attribute-based access control (ABAC) Should probably be used to ensure Security of health data. 
    Data Encryption:
        * At the API and DB level: Sensitive user data should be encrypted in the database using industry-standard encryption algorithms
            (e.g., AES-256 for structured data or transparent database encryption).
        * In Transit: All communication should be encrypted using TLS (Transport Layer Security) to prevent interception
            and man-in-the-middle attacks.
3. Rate Limiting & API Protection: The API should enforce rate limiting (e.g., using tools like python slow) to 
    prevent abuse, brute-force attacks, and denial-of-service (DoS) attacks.
    Additional protections like IP throttling and request validation can further enhance security.
4. Input Validation & SQL Injection Prevention: User input should always be validated and sanitized to prevent injection
    attacks (e.g., SQL injection, XSS). Using parameterized queries with ORM frameworks like SQLAlchemy helps mitigate these risks.