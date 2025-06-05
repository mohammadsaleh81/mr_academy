# URLs of TraderAcademy Project

## Main URLs
- [ ] GET `/admin/` - Django admin interface
- [ ] GET `/api/` - API root (if using DRF)

## Blog App
- [ ] GET `/blog/` - Blog home
- [ ] GET `/blog/&lt;slug:slug&gt;/` - Individual blog post
- [ ] GET `/blog/category/&lt;slug:category_slug&gt;/` - Blog posts by category
- [ ] GET `/blog/tag/&lt;slug:tag_slug&gt;/` - Blog posts by tag
- [ ] GET `/blog/author/&lt;str:username&gt;/` - Blog posts by author

## Course App
- [ ] GET `/courses/` - Course listing
- [ ] GET `/courses/&lt;slug:slug&gt;/` - Individual course detail
- [ ] POST `/courses/&lt;slug:slug&gt;/enroll/` - Course enrollment
- [ ] GET `/courses/&lt;slug:slug&gt;/lessons/` - Course lessons

## Order App
- [ ] GET `/orders/` - Order history
- [ ] GET `/orders/&lt;int:order_id&gt;/` - Order detail
- [ ] GET, POST `/checkout/` - Checkout process

## User App
- [ ] GET, POST `/accounts/login/` - User login
- [ ] GET, POST `/accounts/logout/` - User logout
- [ ] GET, POST `/accounts/register/` - User registration
- [ ] GET, PUT `/accounts/profile/` - User profile
- [ ] GET, POST `/accounts/password_reset/` - Password reset

## Wallet App
- [ ] GET `/wallet/` - Wallet overview
- [ ] GET `/wallet/transactions/` - Transaction history
- [ ] GET, POST `/wallet/deposit/` - Deposit funds
- [ ] GET, POST `/wallet/withdraw/` - Withdraw funds

## API Endpoints
- [ ] GET `/api/blog/` - Blog API
- [ ] GET, POST `/api/blog/posts/` - List and create blog posts
- [ ] GET, PUT, DELETE `/api/blog/posts/&lt;int:id&gt;/` - Retrieve, update, delete blog post

- [ ] GET `/api/courses/` - Courses API
- [ ] GET, POST `/api/courses/list/` - List and create courses
- [ ] GET, PUT, DELETE `/api/courses/&lt;int:id&gt;/` - Retrieve, update, delete course

- [ ] GET `/api/orders/` - Orders API
- [ ] GET, POST `/api/orders/list/` - List and create orders
- [ ] GET, PUT `/api/orders/&lt;int:id&gt;/` - Retrieve and update order

- [ ] GET `/api/users/` - Users API
- [ ] GET, POST `/api/users/list/` - List and create users
- [ ] GET, PUT, DELETE `/api/users/&lt;int:id&gt;/` - Retrieve, update, delete user

- [ ] GET `/api/wallet/` - Wallet API
- [ ] GET `/api/wallet/balance/` - Get wallet balance
- [ ] POST `/api/wallet/transaction/` - Create new transaction

## Media
- [ ] GET `/media/&lt;path&gt;` - Uploaded media files

## Static Files
- [ ] GET `/static/&lt;path&gt;` - Static files (CSS, JS, images)