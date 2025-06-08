# Banner Sizes Documentation

## Overview
This document provides a comprehensive overview of banner sizes used throughout the Academy application for posts, articles, and courses.

## Post/Article Banner Sizes

### ContentCard Component (`ContentCard.tsx`)
**Usage:** Article listings, blog posts, podcasts, videos, webinars, and files

**Dimensions:**
- **Mobile:** `h-32` = **128px** height
- **Desktop:** `h-44` = **176px** height  
- **Width:** Full width of container

**Code Reference:**
```tsx
<img
  src={thumbnail || defaultThumbnail}
  alt={title}
  className="w-full h-32 sm:h-44 object-cover rounded-t-lg"
/>
```

---

## Course Banner Sizes

### 1. Home Page Hero Carousel (`HeroCarousel.tsx`)
**Usage:** Main promotional carousel on homepage

**Dimensions:**
- **Mobile:** `180px` height
- **Tablet:** `240px` height  
- **Desktop:** `300px` height
- **Width:** Mobile = full width, Desktop = half width

**Code Reference:**
```tsx
<div className="relative h-[180px] md:h-[240px] lg:h-[300px] w-full">
```

### 2. Course Cards (`CourseCard.tsx`)
**Usage:** Course listing grids

**Dimensions:**
- **Height:** `h-40` = **160px**
- **Width:** Full width of card

**Code Reference:**
```tsx
<div className="relative h-40 w-full">
  <img className="w-full h-full object-cover rounded-t-xl" />
</div>
```

### 3. Course Detail Hero (`CourseHero.tsx`)
**Usage:** Hero section on individual course pages

**Dimensions:**
- **Height:** `h-80` = **320px**
- **Width:** Full width

**Code Reference:**
```tsx
<div className="relative h-80 bg-gradient-to-r from-orange-500 to-orange-600 overflow-hidden">
  <img className="w-full h-full object-cover opacity-80" />
</div>
```

### 4. Course Info Card (`CourseInfoCard.tsx`)
**Usage:** Sidebar course information card

**Dimensions:**
- **Height:** `h-48` = **192px**
- **Width:** Full width

**Code Reference:**
```tsx
<img className="w-full h-48 object-cover rounded-lg" />
```

### 5. My Courses Page (`MyCoursesPage.tsx`)
**Usage:** User dashboard course listings

**Dimensions:**
- **Height:** `h-48` = **192px** 
- **Width:** Full width

**Code Reference:**
```tsx
<img className="w-full h-48 object-cover" />
```

---

## Complete Banner Sizes Summary

| Component | Usage | Height (Mobile) | Height (Desktop) | Width | File Location |
|-----------|-------|----------------|------------------|-------|---------------|
| **Posts/Articles** | Content listing | 128px | 176px | Full | `ContentCard.tsx` |
| **Home Hero** | Main carousel | 180px | 300px | Full/Half | `HeroCarousel.tsx` |
| **Course Cards** | Course listing | 160px | 160px | Full | `CourseCard.tsx` |
| **Course Detail** | Course page hero | 320px | 320px | Full | `CourseHero.tsx` |
| **Course Info** | Course sidebar | 192px | 192px | Full | `CourseInfoCard.tsx` |
| **My Courses** | User dashboard | 192px | 192px | Full | `MyCoursesPage.tsx` |

---

## Technical Notes

### Responsive Breakpoints
- **Mobile:** Default (no prefix)
- **Small screens:** `sm:` (640px+)
- **Medium screens:** `md:` (768px+)
- **Large screens:** `lg:` (1024px+)

### Common CSS Classes Used
- `w-full` - Full width
- `h-32` - 128px height
- `h-40` - 160px height
- `h-44` - 176px height
- `h-48` - 192px height
- `h-80` - 320px height
- `object-cover` - Maintain aspect ratio while covering container
- `rounded-t-lg` - Rounded top corners
- `rounded-lg` - Rounded corners

### Image Optimization
All banners include:
- `loading="lazy"` for performance
- Error handling with fallback images
- `object-cover` for proper aspect ratio maintenance

---

## Recommendations

### For Optimal Display:
1. **Course banners:** Use 16:9 aspect ratio images
2. **Post banners:** Use 16:10 or 3:2 aspect ratio images
3. **Minimum resolution:** 800x450px for course banners
4. **File formats:** JPEG for photos, PNG for graphics with transparency
5. **File size:** Keep under 500KB for web performance

### Consistency Guidelines:
- All banners use `object-cover` to maintain consistent dimensions
- Rounded corners are applied consistently across components
- Fallback images are implemented for broken links
- Responsive design ensures proper scaling across devices

---

*Document generated on: $(date)*
*Academy Application Banner Sizes Reference* 