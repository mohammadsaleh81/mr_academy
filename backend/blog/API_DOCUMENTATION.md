# مستندات API سیستم کامنت

این مستندات راهنمای کاملی برای استفاده از API های سیستم کامنت در پلتفرم Master Trader Academy ارائه می‌دهد.

## فهرست مطالب
- [API های کامنت مقالات](#api-های-کامنت-مقالات)
- [API های کامنت رسانه‌ها](#api-های-کامنت-رسانهها)
- [API های عمومی کامنت](#api-های-عمومی-کامنت)
- [نمونه‌های کاربردی](#نمونههای-کاربردی)

## API های کامنت مقالات

### دریافت کامنت‌های یک مقاله
```
GET /api/blog/articles/{article_id}/comments/
```

**پاسخ نمونه:**
```json
[
  {
    "id": 1,
    "article": 1,
    "author": {
      "id": 1,
      "username": "user1",
      "email": "user@example.com",
      "first_name": "علی",
      "last_name": "محمدی"
    },
    "parent": null,
    "content": "مقاله بسیار مفیدی بود",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z",
    "is_approved": true,
    "replies": [
      {
        "id": 2,
        "article": 1,
        "author": {
          "id": 2,
          "username": "admin",
          "email": "admin@example.com",
          "first_name": "مدیر",
          "last_name": "سایت"
        },
        "parent": 1,
        "content": "متشکرم از نظر شما",
        "created_at": "2024-01-01T11:00:00Z",
        "updated_at": "2024-01-01T11:00:00Z",
        "is_approved": true,
        "replies": []
      }
    ]
  }
]
```

### اضافه کردن کامنت به مقاله
```
POST /api/blog/articles/{article_id}/comments/
```

**پارامترهای ورودی:**
```json
{
  "content": "متن کامنت",
  "parent": null  // یا ID کامنت والد برای پاسخ
}
```

## API های کامنت رسانه‌ها

### دریافت کامنت‌های یک ویدیو
```
GET /api/blog/videos/{video_id}/comments/
```

### اضافه کردن کامنت به ویدیو
```
POST /api/blog/videos/{video_id}/comments/
```

**پارامترهای ورودی:**
```json
{
  "content": "متن کامنت",
  "parent": null  // یا ID کامنت والد برای پاسخ
}
```

### دریافت کامنت‌های یک پادکست
```
GET /api/blog/podcasts/{podcast_id}/comments/
```

### اضافه کردن کامنت به پادکست
```
POST /api/blog/podcasts/{podcast_id}/comments/
```

## API های عمومی کامنت رسانه

### دریافت کامنت‌های هر نوع محتوا
```
GET /api/blog/media-comments/?content_type={content_type}&object_id={object_id}
```

**پارامترها:**
- `content_type`: نوع محتوا (video, podcast, file, livestream)
- `object_id`: شناسه محتوا

**مثال:**
```
GET /api/blog/media-comments/?content_type=video&object_id=1
```

### اضافه کردن کامنت به هر نوع محتوا
```
POST /api/blog/media-comments/
```

**پارامترهای ورودی:**
```json
{
  "content_type": "video",
  "object_id": 1,
  "content": "متن کامنت",
  "parent": null
}
```

### لیست کلی کامنت‌های رسانه
```
GET /api/blog/media-comments/list/
```

**فیلترها (اختیاری):**
- `content_type`: فیلتر بر اساس نوع محتوا
- `object_id`: فیلتر بر اساس شناسه محتوا

### مدیریت کامنت‌های رسانه

#### دریافت جزئیات یک کامنت
```
GET /api/blog/media-comments/{comment_id}/
```

#### ویرایش کامنت (فقط صاحب کامنت)
```
PUT /api/blog/media-comments/{comment_id}/
```

**پارامترهای ورودی:**
```json
{
  "content": "متن جدید کامنت"
}
```

#### حذف کامنت (فقط صاحب کامنت)
```
DELETE /api/blog/media-comments/{comment_id}/
```

## نمونه‌های کاربردی

### 1. نمایش کامنت‌های یک ویدیو در React

```javascript
// دریافت کامنت‌های ویدیو
const fetchVideoComments = async (videoId) => {
  try {
    const response = await fetch(`/api/blog/videos/${videoId}/comments/`);
    const comments = await response.json();
    return comments;
  } catch (error) {
    console.error('خطا در دریافت کامنت‌ها:', error);
  }
};

// اضافه کردن کامنت جدید
const addVideoComment = async (videoId, content, parentId = null) => {
  try {
    const response = await fetch(`/api/blog/videos/${videoId}/comments/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        content: content,
        parent: parentId
      })
    });
    
    if (response.ok) {
      const newComment = await response.json();
      return newComment;
    }
  } catch (error) {
    console.error('خطا در ارسال کامنت:', error);
  }
};
```

### 2. استفاده از API عمومی برای انواع محتوا

```javascript
// دریافت کامنت‌های هر نوع محتوا
const fetchMediaComments = async (contentType, objectId) => {
  try {
    const response = await fetch(
      `/api/blog/media-comments/?content_type=${contentType}&object_id=${objectId}`
    );
    const comments = await response.json();
    return comments;
  } catch (error) {
    console.error('خطا در دریافت کامنت‌ها:', error);
  }
};

// اضافه کردن کامنت به هر نوع محتوا
const addMediaComment = async (contentType, objectId, content, parentId = null) => {
  try {
    const response = await fetch('/api/blog/media-comments/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        content_type: contentType,
        object_id: objectId,
        content: content,
        parent: parentId
      })
    });
    
    if (response.ok) {
      const newComment = await response.json();
      return newComment;
    }
  } catch (error) {
    console.error('خطا در ارسال کامنت:', error);
  }
};
```

### 3. کامپوننت کامنت در React

```javascript
import React, { useState, useEffect } from 'react';

const CommentSystem = ({ contentType, objectId }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState(null);

  useEffect(() => {
    loadComments();
  }, [contentType, objectId]);

  const loadComments = async () => {
    let url;
    if (contentType === 'article') {
      url = `/api/blog/articles/${objectId}/comments/`;
    } else {
      url = `/api/blog/media-comments/?content_type=${contentType}&object_id=${objectId}`;
    }
    
    try {
      const response = await fetch(url);
      const data = await response.json();
      setComments(data);
    } catch (error) {
      console.error('خطا در بارگذاری کامنت‌ها:', error);
    }
  };

  const submitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      let url, body;
      
      if (contentType === 'article') {
        url = `/api/blog/articles/${objectId}/comments/`;
        body = {
          content: newComment,
          parent: replyTo
        };
      } else {
        url = '/api/blog/media-comments/';
        body = {
          content_type: contentType,
          object_id: objectId,
          content: newComment,
          parent: replyTo
        };
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        setNewComment('');
        setReplyTo(null);
        loadComments(); // بارگذاری مجدد کامنت‌ها
      }
    } catch (error) {
      console.error('خطا در ارسال کامنت:', error);
    }
  };

  const Comment = ({ comment, depth = 0 }) => (
    <div style={{ marginLeft: depth * 20 + 'px' }} className="comment">
      <div className="comment-header">
        <strong>{comment.author.first_name} {comment.author.last_name}</strong>
        <span className="comment-date">{comment.created_at}</span>
      </div>
      <div className="comment-content">{comment.content}</div>
      <button onClick={() => setReplyTo(comment.id)}>پاسخ</button>
      
      {comment.replies && comment.replies.map(reply => (
        <Comment key={reply.id} comment={reply} depth={depth + 1} />
      ))}
    </div>
  );

  return (
    <div className="comment-system">
      <h3>نظرات</h3>
      
      <form onSubmit={submitComment}>
        {replyTo && (
          <div>
            در پاسخ به کامنت #{replyTo}
            <button type="button" onClick={() => setReplyTo(null)}>لغو</button>
          </div>
        )}
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="نظر خود را بنویسید..."
          rows={4}
        />
        <button type="submit">ارسال نظر</button>
      </form>

      <div className="comments-list">
        {comments.map(comment => (
          <Comment key={comment.id} comment={comment} />
        ))}
      </div>
    </div>
  );
};

export default CommentSystem;
```

## نکات مهم

1. **احراز هویت**: برای ارسال کامنت نیاز به احراز هویت دارید.
2. **تایید کامنت‌ها**: کامنت‌ها به صورت پیش‌فرض نیاز به تایید ادمین دارند.
3. **سطح پاسخ**: فقط یک سطح پاسخ مجاز است (نمی‌توان به پاسخ‌ها پاسخ داد).
4. **ویرایش و حذف**: فقط صاحب کامنت می‌تواند آن را ویرایش یا حذف کند.
5. **فیلتر وضعیت**: فقط محتواهای منتشر شده قابل کامنت گذاری هستند.

## کدهای خطا

- `400`: پارامترهای ورودی نامعتبر
- `401`: نیاز به احراز هویت
- `403`: عدم دسترسی (مثلاً ویرایش کامنت دیگران)
- `404`: محتوا یا کامنت یافت نشد 