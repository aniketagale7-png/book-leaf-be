from rest_framework import serializers
from .models import User, Author, Book, Ticket, TicketMessage, InternalNote

# ==========================================
# User Serializer
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    author_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'author_id', 'created_at']

    def get_author_id(self, obj):
        if hasattr(obj, 'author_profile') and obj.author_profile:
            return obj.author_profile.author_id
        return None


# ==========================================
# Author Serializer
# ==========================================
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['author_id', 'name', 'email', 'phone', 'city', 'joined_date']


# ==========================================
# Book Serializers
# ==========================================
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'book_id', 'author', 'title', 'isbn', 'genre', 
            'publication_date', 'status', 'mrp', 'author_royalty_per_copy',
            'total_copies_sold', 'total_royalty_earned', 'royalty_paid',
            'royalty_pending', 'last_royalty_payout_date', 'print_partner', 
            'available_on'
        ]


class BookListSerializer(serializers.ModelSerializer):
    author_id = serializers.CharField(source='author.author_id', read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'book_id', 'author_id', 'author_name', 'title', 'isbn', 'genre',
            'publication_date', 'status', 'mrp', 'author_royalty_per_copy',
            'total_copies_sold', 'total_royalty_earned', 'royalty_paid',
            'royalty_pending', 'last_royalty_payout_date', 'print_partner',
            'available_on'
        ]


class BookCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=True)
    genre = serializers.CharField(max_length=100, required=False, default="General Fiction")
    mrp = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=299.00)
    author_royalty_per_copy = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=50.00)
    print_partner = serializers.CharField(max_length=150, required=False, default="BookLeaf Express Print")
    available_on = serializers.ListField(child=serializers.CharField(), required=False, default=lambda: ["BookLeaf Store"])


class DashboardStatsSerializer(serializers.Serializer):
    total_books = serializers.IntegerField()
    published_books = serializers.IntegerField()
    in_production_books = serializers.IntegerField()
    total_copies_sold = serializers.IntegerField()
    total_royalty_earned = serializers.DecimalField(max_digits=12, decimal_places=2)
    royalty_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    royalty_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(default="INR")
    next_payout_date = serializers.CharField()


# ==========================================
# Ticket & Communication Thread Serializers
# ==========================================
class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket_id', 'sender_type', 'sender_name', 'sender_role', 'content', 'timestamp']


class InternalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalNote
        fields = ['id', 'ticket_id', 'admin_name', 'note', 'timestamp']


class TicketListSerializer(serializers.ModelSerializer):
    author_id = serializers.CharField(source='author.author_id', read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True, default=None)
    messages_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'author_id', 'author_name', 'author_email', 'book_id', 'book_title',
            'subject', 'description', 'category', 'priority', 'status',
            'assigned_to', 'attachment_name', 'attachment_size', 'messages_count',
            'created_at', 'updated_at'
        ]

    def get_messages_count(self, obj):
        return obj.messages.count()


class TicketDetailSerializer(serializers.ModelSerializer):
    author_id = serializers.CharField(source='author.author_id', read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    author_phone = serializers.CharField(source='author.phone', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True, default=None)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True, default=None)
    messages = TicketMessageSerializer(many=True, read_only=True)
    internal_notes = serializers.SerializerMethodField()
    ai_draft = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'author_id', 'author_name', 'author_email', 'author_phone',
            'book_id', 'book_title', 'book_isbn', 'subject', 'description',
            'category', 'priority', 'status', 'assigned_to',
            'attachment_name', 'attachment_size', 'messages', 'internal_notes',
            'ai_draft', 'created_at', 'updated_at'
        ]

    def get_internal_notes(self, obj):
        request = self.context.get('request')
        if request and request.user.role == 'admin':
            return InternalNoteSerializer(obj.internal_notes.all(), many=True).data
        return []

    def get_ai_draft(self, obj):
        if obj.ai_draft_content:
            return {
                "draft_content": obj.ai_draft_content,
                "source_policies": obj.ai_source_policies or ["BookLeaf Knowledge Base"],
                "confidence_score": obj.ai_confidence_score or 0.94
            }
        from .ai_service import generate_ai_draft_response
        draft_info = generate_ai_draft_response(obj)
        obj.ai_draft_content = draft_info['draft_content']
        obj.ai_source_policies = draft_info['source_policies']
        obj.ai_confidence_score = draft_info['confidence_score']
        obj.save(update_fields=['ai_draft_content', 'ai_source_policies', 'ai_confidence_score'])
        return draft_info


class TicketCreateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=True)
    category = serializers.ChoiceField(choices=Ticket.CATEGORY_CHOICES, required=False, allow_null=True)
    priority = serializers.ChoiceField(choices=Ticket.PRIORITY_CHOICES, required=False, allow_null=True)
    book_id = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    attachment_name = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    attachment_size = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)


class TicketUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES, required=False)
    priority = serializers.ChoiceField(choices=Ticket.PRIORITY_CHOICES, required=False)
    assigned_to = serializers.CharField(max_length=150, required=False, allow_blank=True, allow_null=True)


class TicketMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)


class InternalNoteCreateSerializer(serializers.Serializer):
    note = serializers.CharField(required=True)


class OperationsDeskStatsSerializer(serializers.Serializer):
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    in_progress_tickets = serializers.IntegerField()
    resolved_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()
    critical_tickets = serializers.IntegerField()


# ==========================================
# Auth Request Serializers
# ==========================================
class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    book_title = serializers.CharField(max_length=255, required=False, allow_blank=True, default="My Debut Book")
    city = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True, default="")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
