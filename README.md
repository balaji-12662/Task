📌 Features
User Authentication

Token-based authentication using a custom @token_required decorator.

Simple login and registration endpoints for teachers.

Student Management

Add a new student with name, subject, and marks.

Update an existing student’s marks via a PUT request.

Validations in place to ensure marks never go above 100.

Name and subject matching is case-insensitive for smoother updates.

Audit Logging

Every insert or update is recorded in an AuditLog table.

Tracks old and new values along with the teacher who made the change.

Secure Transactions

All write operations are wrapped in transaction.atomic() to avoid partial updates.

select_for_update() ensures no two requests can modify the same student at the same time.

🔐 Security Considerations
CSRF protection is disabled for API endpoints using @csrf_exempt (safe for development, but in production this should be replaced with token-based CSRF handling).

Token authentication ensures only logged-in teachers can add or update students.

Strict input validation ensures marks are always between 0 and 100.

Row-level locking prevents race conditions during concurrent updates.

⚠️ Challenges Faced
Handling concurrent updates for the same student — solved using row-level locking with select_for_update().

Designing the calculate_new_marks() helper so it rejects updates that would push marks above 100.

Making sure audit logs are always created for both inserts and updates.

Sorting out URL patterns to fix “Page not found” errors for API endpoints.

⏱ Approximate Time Taken
Project setup and authentication: ~2 hours

Student CRUD endpoints and business logic: ~3 hours

Audit log integration: ~1 hour

Testing and debugging: ~1.5 hours

Writing documentation: ~30 minutes
