from django.contrib import admin
from .models import Profile, Skill, UserSkill, SwapRequest, Message

# This registers the models so they appear in the admin panel
admin.site.register(Profile)
admin.site.register(Skill)
admin.site.register(UserSkill)
admin.site.register(SwapRequest)
admin.site.register(Message)
