from django.db import models
from django.contrib.auth.models import User

# 1. User Profile (Extension of default User)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    
    # NEW: Image Field (default image is optional but good practice)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

# 2. The Skills available
class Skill(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=[
        ('TECH', 'Technology'), ('ART', 'Art'), ('MUSIC', 'Music'), ('LIFE', 'Lifestyle')
    ])

    def __str__(self):
        return self.name

# 3. Linking Users to Skills (Teach vs Learn)
class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('TEACH', 'Teach'), ('LEARN', 'Learn')])

    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.skill.name}"

# 4. Swap Requests
class SwapRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_swaps', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_swaps', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='PENDING', choices=[
        ('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('DECLINED', 'Declined')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

# 5. Chat Messages
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)




