from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_approved')
    list_filter = ('is_approved',)
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Usuários aprovados com sucesso!")
    approve_users.short_description = "Aprovar usuários selecionados"
