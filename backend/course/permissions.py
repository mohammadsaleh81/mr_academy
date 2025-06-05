from rest_framework import permissions

class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow instructors of a course to edit it.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the instructor
        if hasattr(obj, 'instructor'):
            return obj.instructor == request.user
        elif hasattr(obj, 'course'):
            return obj.course.instructor == request.user
        elif hasattr(obj, 'chapter'):
            return obj.chapter.course.instructor == request.user
        return False

class IsEnrolledOrPreview(permissions.BasePermission):
    """
    Custom permission to only allow access to students enrolled in the course,
    or to preview lessons marked as free preview.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return obj.is_free_preview
            
        if request.user.is_staff or obj.chapter.course.instructor == request.user:
            return True
            
        # Check if user is enrolled in the course
        return obj.chapter.course.enrollments.filter(user=request.user).exists() or obj.is_free_preview

class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow instructors or admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or 
            request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        if hasattr(obj, 'course'):
            return obj.course.instructor == request.user
        return obj.instructor == request.user 