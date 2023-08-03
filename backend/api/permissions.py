from rest_framework.permissions import IsAuthenticated


class IsAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == "retrieve":
            return True
        return super().has_permission(request, view)
