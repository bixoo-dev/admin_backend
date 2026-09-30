# BIXOO API Documentation

| Method | Endpoint | Purpose | Auth | Role | Request | Response |
| ------ | -------- | ------- | ---- | ---- | ------- | -------- |
| POST | `/api/v1/auth/login` | Authenticate and get JWT | None | None | `OAuth2PasswordRequestForm` | `{ access_token, token_type }` |
| GET | `/api/v1/auth/me` | Get current admin details | Yes | Any | None | `AdminResponse` |
| GET | `/api/v1/dashboard/metrics` | Dashboard statistics | Yes | Any | None | `DashboardMetricsResponse` |
| GET | `/api/v1/admin/accounts` | List verification queue | Yes | Any | `?status=...` | `{ accounts: [...] }` |
| POST | `/api/v1/admin/accounts/{id}/decisions` | Approve/Suspend account | Yes | `accounts:verify` | `{ actionType, reasonCode, ... }` | `{ success, message }` |
| GET | `/api/v1/admin/catalog` | List catalog items | Yes | Any | None | `{ listings: [...] }` |
| GET | `/api/v1/admin/requirements` | List requirements | Yes | Any | None | `{ requirements: [...] }` |
| GET | `/api/v1/admin/orders` | List orders | Yes | Any | None | `{ orders: [...] }` |
| GET | `/api/v1/admin/auctions` | List auctions | Yes | Any | None | `{ auctions: [...] }` |
| POST | `/api/v1/admin/auctions/{id}/void` | Void an auction | Yes | `auctions:void` | None | `{ success, message }` |
| GET | `/api/v1/admin/trips` | List trips tracking | Yes | Any | None | `{ trips: [...] }` |
| GET | `/api/v1/admin/settlements` | List settlements | Yes | Any | None | `{ settlements: [...] }` |
| GET | `/api/v1/admin/cases` | List dispute cases | Yes | Any | None | `{ cases: [...] }` |
| GET | `/api/v1/admin/settings/audit-logs` | View audit logs | Yes | `settings:manage` | None | `{ logs: [...] }` |

All endpoints starting with `/api/v1` require the `Authorization: Bearer <token>` header except `/login`.
