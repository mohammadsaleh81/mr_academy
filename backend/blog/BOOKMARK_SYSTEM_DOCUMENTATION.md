# سیستم بوکمارک Master Trader Academy

## خلاصه سیستم

سیستم بوکمارک Master Trader Academy امکان نشان‌گذاری مقالات توسط کاربران را فراهم می‌کند. این سیستم کاملاً پیاده‌سازی شده و آماده استفاده است.

## ویژگی‌های سیستم

### 🔒 امنیت و دسترسی
- احراز هویت برای ایجاد/حذف بوکمارک الزامی است
- کنترل دسترسی: فقط صاحب بوکمارک می‌تواند آن را حذف کند
- محافظت از duplicate bookmark (یک کاربر نمی‌تواند یک مقاله را چندبار بوکمارک کند)

### 📱 سازگاری با فرانت‌اند
- API های RESTful کامل
- پاسخ‌های JSON ساختاریافته
- Error handling مناسب

## API های بوکمارک

### دریافت بوکمارک‌های کاربر
```
GET /content/bookmarks/
```

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**پاسخ نمونه:**
```json
[
  {
    "id": 1,
    "user": {
      "id": "1",
      "username": "user1",
      "first_name": "علی",
      "last_name": "محمدی",
      "email": "user@example.com"
    },
    "article": {
      "id": "1",
      "title": "راهنمای کامل ترید بیت‌کوین",
      "slug": "complete-bitcoin-trading-guide",
      "thumbnail": "https://api.gport.sbs/media/blog/thumbnails/bitcoin.jpg"
    },
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```

### اضافه کردن بوکمارک
```
POST /content/bookmarks/
```

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**پارامترهای ورودی:**
```json
{
  "article": 1
}
```

**پاسخ موفق:**
```json
{
  "id": 2,
  "user": {
    "id": "1",
    "username": "user1",
    "first_name": "علی",
    "last_name": "محمدی",
    "email": "user@example.com"
  },
  "article": {
    "id": "1",
    "title": "راهنمای کامل ترید بیت‌کوین",
    "slug": "complete-bitcoin-trading-guide",
    "thumbnail": "https://api.gport.sbs/media/blog/thumbnails/bitcoin.jpg"
  },
  "created_at": "2024-01-01T10:00:00Z"
}
```

### حذف بوکمارک
```
DELETE /content/bookmarks/{bookmark_id}/
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**پاسخ موفق:**
```
HTTP 204 No Content
```

## نحوه استفاده در فرانت‌اند

### React Context
سیستم بوکمارک به صورت کامل در ContentContext پیاده‌سازی شده است:

```javascript
import { useContent } from '@/contexts/ContentContext';

const { 
  bookmarks, 
  addBookmark, 
  removeBookmark, 
  isBookmarked 
} = useContent();
```

### کامپوننت ContentActions
کامپوننت آماده برای نمایش دکمه بوکمارک:

```jsx
import ContentActions from '@/components/content/ContentActions';

<ContentActions 
  articleId="1" 
  title="عنوان مقاله" 
/>
```

### صفحه BookmarksPage
صفحه اختصاصی برای نمایش بوکمارک‌های کاربر:

```
/bookmarks
```

## نمونه‌های کاربردی

### 1. اضافه کردن بوکمارک

```javascript
import { useContent } from '@/contexts/ContentContext';
import { useToast } from '@/hooks/use-toast';

const BookmarkButton = ({ articleId }) => {
  const { addBookmark, isBookmarked } = useContent();
  const { toast } = useToast();

  const handleBookmark = async () => {
    try {
      await addBookmark(articleId);
      toast({
        title: "موفقیت",
        description: "مقاله به نشان‌شده‌ها اضافه شد"
      });
    } catch (error) {
      toast({
        title: "خطا",
        description: "مشکلی در بوکمارک کردن وجود دارد",
        variant: "destructive"
      });
    }
  };

  return (
    <button 
      onClick={handleBookmark}
      disabled={isBookmarked(articleId)}
    >
      {isBookmarked(articleId) ? "بوکمارک شده" : "بوکمارک کن"}
    </button>
  );
};
```

### 2. حذف بوکمارک

```javascript
const RemoveBookmarkButton = ({ articleId }) => {
  const { removeBookmark } = useContent();
  const { toast } = useToast();

  const handleRemove = async () => {
    try {
      await removeBookmark(articleId);
      toast({
        title: "موفقیت",
        description: "مقاله از نشان‌شده‌ها حذف شد"
      });
    } catch (error) {
      toast({
        title: "خطا",
        description: "مشکلی در حذف بوکمارک وجود دارد",
        variant: "destructive"
      });
    }
  };

  return (
    <button onClick={handleRemove}>
      حذف از نشان‌شده‌ها
    </button>
  );
};
```

### 3. نمایش لیست بوکمارک‌ها

```javascript
const BookmarksList = () => {
  const { bookmarks, isLoading } = useContent();

  if (isLoading.bookmarks) {
    return <div>در حال بارگذاری...</div>;
  }

  if (bookmarks.length === 0) {
    return <div>هنوز مقاله‌ای بوکمارک نکرده‌اید</div>;
  }

  return (
    <div>
      {bookmarks.map(bookmark => (
        <div key={bookmark.id}>
          <h3>{bookmark.article.title}</h3>
          <p>بوکمارک شده در: {bookmark.created_at}</p>
        </div>
      ))}
    </div>
  );
};
```

## فایل‌های مرتبط

### Backend
- `blog/models.py` - ArticleBookmark model
- `blog/serializers.py` - ArticleBookmarkSerializer
- `blog/views.py` - ArticleBookmarkListCreateView, ArticleBookmarkDetailView
- `blog/urls.py` - URL patterns
- `blog/admin.py` - Admin interface

### Frontend
- `src/lib/api.ts` - bookmarksApi
- `src/lib/config.ts` - API endpoints
- `src/contexts/ContentContext.tsx` - React context
- `src/components/content/ContentActions.tsx` - UI component
- `src/pages/BookmarksPage.tsx` - Bookmarks page
- `src/types/content.ts` - TypeScript types

## وضعیت سیستم

✅ **آماده استفاده**: سیستم بوکمارک کاملاً پیاده‌سازی شده و تست شده است.

### چه کاری انجام شده:
1. ✅ Backend API های کامل
2. ✅ Frontend Context و Services
3. ✅ UI Components
4. ✅ صفحه BookmarksPage
5. ✅ Error Handling
6. ✅ Authentication & Authorization
7. ✅ URL Configuration
8. ✅ Admin Interface

### قابلیت‌های فعال:
- بوکمارک کردن مقالات
- حذف بوکمارک
- مشاهده لیست بوکمارک‌ها
- UI responsive و کاربرپسند
- Auto-refresh بعد از login/logout

## کدهای خطا

- `400`: پارامترهای ورودی نامعتبر
- `401`: نیاز به احراز هویت
- `403`: عدم دسترسی (مثلاً حذف بوکمارک دیگران)
- `404`: مقاله یا بوکمارک یافت نشد

## تست سیستم

برای تست سیستم:
1. وارد اکانت کاربری شوید
2. به صفحه مقاله‌ای بروید
3. روی دکمه بوکمارک کلیک کنید
4. به صفحه `/bookmarks` بروید
5. بوکمارک را مشاهده کنید

🎉 **سیستم بوکمارک Master Trader Academy آماده استفاده است!** 