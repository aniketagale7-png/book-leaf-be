import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# ==========================================
# Custom User Manager
# ==========================================
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role='author', **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name='Admin', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, role='admin', **extra_fields)


def generate_user_id():
    return str(uuid.uuid4())

# ==========================================
# 1. User Model
# ==========================================
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('author', 'Author'),
        ('admin', 'Admin'),
    )

    id = models.CharField(max_length=64, primary_key=True, default=generate_user_id, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='author')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} ({self.role})"


# ==========================================
# 2. Author Model
# ==========================================
class Author(models.Model):
    author_id = models.CharField(max_length=20, primary_key=True)  # e.g. AUTH001
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'authors'
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return f"{self.author_id} - {self.name}"


# ==========================================
# 3. Book Model
# ==========================================
class Book(models.Model):
    STATUS_CHOICES = (
        ('In Production - Typesetting', 'In Production - Typesetting'),
        ('Cover Design & Review', 'Cover Design & Review'),
        ('Proofreading & Final Edits', 'Proofreading & Final Edits'),
        ('Published & Live', 'Published & Live'),
        ('Out of Print', 'Out of Print'),
    )

    book_id = models.CharField(max_length=20, primary_key=True)  # e.g. BK001
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=50, blank=True, null=True)
    genre = models.CharField(max_length=100, default='General Fiction')
    publication_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='In Production - Typesetting')
    
    # Financial & Sales Information
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=299.00)
    author_royalty_per_copy = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    total_copies_sold = models.IntegerField(default=0)
    total_royalty_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    royalty_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    royalty_pending = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_royalty_payout_date = models.DateField(blank=True, null=True)
    
    # Distribution Information
    print_partner = models.CharField(max_length=150, default='BookLeaf Express Print')
    available_on = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'books'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"{self.book_id} - {self.title}"


# ==========================================
# 4. Support Ticket Model
# ==========================================
class Ticket(models.Model):
    CATEGORY_CHOICES = (
        ('Royalty & Payments', 'Royalty & Payments'),
        ('ISBN & Metadata Issues', 'ISBN & Metadata Issues'),
        ('Printing & Quality', 'Printing & Quality'),
        ('Distribution & Availability', 'Distribution & Availability'),
        ('Book Status & Production Updates', 'Book Status & Production Updates'),
        ('General Inquiry', 'General Inquiry'),
    )

    PRIORITY_CHOICES = (
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    )

    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    )

    id = models.CharField(max_length=50, primary_key=True)  # e.g., TKT-2026-1001
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='tickets')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='General Inquiry')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Open')
    assigned_to = models.CharField(max_length=150, null=True, blank=True)
    attachment_name = models.CharField(max_length=255, null=True, blank=True)
    attachment_size = models.CharField(max_length=50, null=True, blank=True)
    
    # AI-Assisted Operations Desk Fields
    ai_draft_content = models.TextField(null=True, blank=True)
    ai_source_policies = models.JSONField(default=list, blank=True)
    ai_confidence_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id} - {self.subject}"


# ==========================================
# 5. Ticket Message (Communication Thread)
# ==========================================
class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=20, choices=(('author', 'Author'), ('admin', 'Admin')))
    sender_name = models.CharField(max_length=255)
    sender_role = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.ticket_id} - {self.sender_name}: {self.content[:30]}"


# ==========================================
# 6. Internal Note (Admin Operations Only)
# ==========================================
class InternalNote(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='internal_notes')
    admin_name = models.CharField(max_length=255)
    note = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'internal_notes'
        ordering = ['timestamp']

    def __str__(self):
        return f"Note on {self.ticket_id} by {self.admin_name}"
