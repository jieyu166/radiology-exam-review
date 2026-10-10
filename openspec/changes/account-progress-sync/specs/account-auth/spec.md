## ADDED Requirements

### Requirement: Invite-only registration

The API SHALL create an account only when the request carries a valid invite code: one whose SHA-256 matches an `invites` row that is unused, unrevoked and unexpired. Registration SHALL mark the invite as used in the same D1 batch that inserts the user. While the `users` table is empty, the code equal to the `BOOTSTRAP_INVITE_CODE` secret SHALL also be accepted; once any user exists it MUST be rejected. Usernames SHALL be normalized to lowercase and MUST match `^[a-z0-9][a-z0-9_.-]{2,31}$`; passwords MUST be 8–128 characters.

#### Scenario: Register with a valid invite

- **WHEN** a client posts `{username: "Chen.Wei", password: "correct horse battery", inviteCode: <unused code>}`
- **THEN** the API responds 201 with a session token, the user row has username `chen.wei`, and the invite row has `used_by` set to that user

#### Scenario: Reject a used, revoked or expired invite

- **WHEN** the invite code was already used, has `revoked_at` set, or `expires_at` is in the past
- **THEN** the API responds 400 with `error: "invite_invalid"` and creates no user

#### Scenario: Bootstrap the first administrator

- **WHEN** the `users` table is empty and the request's invite code equals `BOOTSTRAP_INVITE_CODE`
- **THEN** the user is created with role `admin` if the username is listed in `ADMIN_USERNAMES`, otherwise `member`

##### Example: Username normalization

| Input | Stored | Result |
| --- | --- | --- |
| `Chen.Wei` | `chen.wei` | accepted |
| `ab` | — | 400 `invalid_username` (too short) |
| `_lead` | — | 400 `invalid_username` (must start alphanumeric) |

### Requirement: Password hashing with upgradable PBKDF2

The API SHALL hash passwords with WebCrypto PBKDF2-HMAC-SHA256 using a 16-byte random salt and a 32-byte output, storing the PHC string `$pbkdf2-sha256$i=<iterations>$<salt>$<hash>` with base64url fields. Verification SHALL read the iteration count from the stored string, compare with a constant-time comparison, and SHALL report `needsRehash: true` when the stored count is lower than the current `PBKDF2_ITERATIONS` constant so the next successful login re-hashes transparently. The iteration constant MUST NOT exceed 100,000 (the workerd hard limit).

#### Scenario: Verify and transparently upgrade

- **WHEN** a stored hash uses `i=50000` and the constant is `100000` and the user logs in with the correct password
- **THEN** verification succeeds and the stored hash is replaced by one with `i=100000`

#### Scenario: Reject a wrong password without leaking which field failed

- **WHEN** the password does not match or the username does not exist
- **THEN** the API responds 401 with `error: "auth_failed"` and the same message in both cases

### Requirement: Bearer session tokens

Login SHALL issue a 32-byte random token encoded base64url, return it exactly once, and store only its SHA-256 in `sessions` with `expires_at` 30 days after creation. Every protected route SHALL require `Authorization: Bearer <token>`, SHALL reject expired or unknown tokens and tokens of users with `disabled_at` set with 401, and SHALL update `last_used_at` at most once per five minutes. The API MUST NOT set cookies.

#### Scenario: Authenticated request

- **WHEN** a request carries a bearer token whose hash matches an unexpired session of an enabled user
- **THEN** the route executes as that user

#### Scenario: Disabled user

- **WHEN** an administrator disables a user and that user's existing token is presented
- **THEN** the API responds 401 and the client clears its local session

#### Scenario: Logout

- **WHEN** `POST /auth/logout` is called with a valid token
- **THEN** that session row is deleted and the same token subsequently yields 401

### Requirement: Login throttling and lockout

The API SHALL apply the Workers `ratelimits` binding keyed by normalized username (limit 5 per 60 seconds) before verifying a password and respond 429 when exceeded. It SHALL additionally track consecutive failures in `login_attempts`; after 5 consecutive failures the username SHALL be locked for 15 minutes and the API SHALL respond 423 with `retryAfterSeconds`. A successful login SHALL reset the counter.

#### Scenario: Lock after five failures

- **WHEN** five consecutive wrong passwords are submitted for `chen.wei`
- **THEN** the sixth attempt responds 423 with `retryAfterSeconds` greater than 0 even if the password is correct

#### Scenario: Reset on success

- **WHEN** a user with 3 recorded failures logs in correctly before being locked
- **THEN** the failure counter returns to 0

### Requirement: Administrator invite and user management

Users whose username is listed in `ADMIN_USERNAMES` SHALL have role `admin`. Admin routes SHALL let an administrator create an invite (returning the plaintext code once, with optional `note` and `expiresInDays`, default 14), list invites with their status, revoke an unused invite, list users, and disable a user. Non-admin callers SHALL receive 403.

#### Scenario: Create and reveal an invite once

- **WHEN** an admin posts `POST /admin/invites {note: "R2 王醫師"}`
- **THEN** the response contains the plaintext code and the stored row contains only its hash; a later `GET /admin/invites` shows the note and status but never the code

#### Scenario: Member cannot access admin routes

- **WHEN** a user with role `member` calls any `/admin/*` route
- **THEN** the API responds 403

### Requirement: CORS for the static front end

The API SHALL answer `OPTIONS` requests with 204 and, for origins listed in `ALLOWED_ORIGINS`, SHALL return `Access-Control-Allow-Origin` equal to the request origin, `Vary: Origin`, `Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS`, `Access-Control-Allow-Headers: Content-Type, Authorization`, and `Access-Control-Max-Age: 7200`. Requests from unlisted origins SHALL receive no CORS allow headers.

#### Scenario: Allowed origin preflight

- **WHEN** a preflight arrives with `Origin: https://jieyu166.github.io`
- **THEN** the response is 204 with the allow headers above echoing that origin

#### Scenario: Unlisted origin

- **WHEN** a request arrives with `Origin: https://evil.example`
- **THEN** no `Access-Control-Allow-Origin` header is returned
