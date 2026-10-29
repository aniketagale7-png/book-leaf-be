import re
from datetime import date
from django.utils import timezone
from django.db.models import Q, Sum
from django.db import transaction

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Author, Book, Ticket, TicketMessage, InternalNote
from .serializers import (
    UserSerializer, 
    AuthorSerializer, 
    BookSerializer,
    BookListSerializer,
    BookCreateSerializer,
    DashboardStatsSerializer,
    TicketMessageSerializer,
    InternalNoteSerializer,
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
    TicketMessageCreateSerializer,
    InternalNoteCreateSerializer,
    OperationsDeskStatsSerializer,
    RegisterSerializer, 
    LoginSerializer
)


# ==========================================
# Helper Functions for ID Generation
# ==========================================
def get_next_author_id():
    """Generates next author_id like AUTH001, AUTH002, etc."""
    authors = Author.objects.filter(author_id__startswith='AUTH')
    max_num = 0
    for a in authors:
        match = re.search(r'AUTH(\d+)', a.author_id)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1
    return f"AUTH{next_num:03d}"


def get_next_book_id():
    """Generates next book_id like BK001, BK002, etc."""
    books = Book.objects.filter(book_id__startswith='BK')
    max_num = 0
    for b in books:
        match = re.search(r'BK(\d+)', b.book_id)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1
    return f"BK{next_num:03d}"


def get_next_ticket_id():
    """Generates next ticket_id like TKT-2026-1001, TKT-2026-1002, etc."""
    year = timezone.now().year
    prefix = f"TKT-{year}-"
    tickets = Ticket.objects.filter(id__startswith=prefix)
    max_num = 1000
    for t in tickets:
        try:
            num = int(t.id.split('-')[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            pass
    return f"{prefix}{max_num + 1}"


# ==========================================
# 1. Register API
# POST /api/v1/auth/register
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Author Registration API
    - Validates input & unique email
    - Hashes password
    - Generates sequential author_id (e.g. AUTH002)
    - Creates Author record
    - Creates Debut Book in 'In Production - Typesetting' status
    - Returns JWT tokens + user profile
    """
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    email = data['email'].lower().strip()
    name = data['name'].strip()
    password = data['password']
    book_title = data.get('book_title') or "My Debut Book"
    city = data.get('city', '')
    phone = data.get('phone', '')

    # Check unique email
    if User.objects.filter(email=email).exists():
        return Response({
            "error": "Email already exists",
            "message": "An account with this email is already registered."
        }, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        # 1. Create User
        user = User.objects.create_user(
            email=email,
            name=name,
            password=password,
            role='author'
        )

        # 2. Generate Author ID and create Author profile
        author_id = get_next_author_id()
        author = Author.objects.create(
            author_id=author_id,
            user=user,
            name=name,
            email=email,
            phone=phone,
            city=city
        )

        # 3. Create initial debut book in "In Production - Typesetting"
        book_id = get_next_book_id()
        Book.objects.create(
            book_id=book_id,
            author=author,
            title=book_title,
            genre='General Fiction',
            status='In Production - Typesetting',
            mrp=299.00,
            author_royalty_per_copy=50.00,
            print_partner='BookLeaf Express Print',
            available_on=['BookLeaf Store', 'Amazon']
        )

    # 4. Generate JWT Tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        "status": "success",
        "message": "Author registered successfully with debut book initialized.",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "token_type": "bearer",
        "user": UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


# ==========================================
# 2. Single Unified Login API
# POST /api/v1/auth/login
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Single Unified Login API: /api/v1/auth/login
    Accepts: { "email": "...", "password": "..." }
    Automatically detects user role (author or admin) and returns appropriate dashboard profile.
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].lower().strip()
    password = serializer.validated_data['password']

    user = User.objects.filter(email=email).first()
    if not user or not user.check_password(password):
        return Response({
            "error": "Invalid credentials",
            "message": "Invalid email or password."
        }, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)

    return Response({
        "status": "success",
        "message": f"Login successful as {user.role}.",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "token_type": "bearer",
        "user": UserSerializer(user).data
    }, status=status.HTTP_200_OK)


# ==========================================
# 3. Authenticated User Profile API
# GET /api/v1/auth/me
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Returns current authenticated user details.
    Requires: Bearer <access_token> in Authorization header
    """
    user = request.user
    user_data = UserSerializer(user).data
    
    extra_data = {}
    if hasattr(user, 'author_profile'):
        author = user.author_profile
        extra_data['author_details'] = AuthorSerializer(author).data
        books = author.books.all()
        extra_data['books'] = BookSerializer(books, many=True).data

    return Response({
        "status": "success",
        "user": user_data,
        **extra_data
    }, status=status.HTTP_200_OK)


# ==========================================
# 4. Books Module: List & Create
# GET  /api/v1/books
# POST /api/v1/books
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def books_view(request):
    """
    GET  /api/v1/books: List books with role-based filtering, search, and status.
    POST /api/v1/books: Create new book for logged-in author.
    """
    user = request.user

    # GET: List Books
    if request.method == 'GET':
        if user.role == 'author':
            if not hasattr(user, 'author_profile'):
                return Response([], status=status.HTTP_200_OK)
            queryset = Book.objects.filter(author=user.author_profile)
        elif user.role == 'admin':
            queryset = Book.objects.all()
            author_id = request.query_params.get('author_id')
            if author_id:
                queryset = queryset.filter(author__author_id=author_id)
        else:
            queryset = Book.objects.none()

        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(author__name__icontains=search) | 
                Q(isbn__icontains=search)
            )

        serializer = BookListSerializer(queryset.select_related('author').order_by('-book_id'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST: Create New Book (Author only)
    elif request.method == 'POST':
        if user.role != 'author' or not hasattr(user, 'author_profile'):
            return Response({
                "error": "Forbidden",
                "message": "Only registered authors can create books."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = BookCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        book_id = get_next_book_id()
        author = user.author_profile

        book = Book.objects.create(
            book_id=book_id,
            author=author,
            title=data['title'].strip(),
            genre=data.get('genre', 'General Fiction'),
            mrp=data.get('mrp', 299.00),
            author_royalty_per_copy=data.get('author_royalty_per_copy', 50.00),
            print_partner=data.get('print_partner', 'BookLeaf Express Print'),
            available_on=data.get('available_on') or ["BookLeaf Store"],
            status='In Production - Typesetting'
        )

        return Response(BookListSerializer(book).data, status=status.HTTP_201_CREATED)


# ==========================================
# 5. Single Book Detail API
# GET /api/v1/books/<str:book_id>
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def book_detail(request, book_id):
    """Get single book details by book_id."""
    book = Book.objects.filter(book_id=book_id).select_related('author').first()
    if not book:
        return Response({
            "error": "Not Found",
            "message": f"Book with ID '{book_id}' does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'author':
        if not hasattr(request.user, 'author_profile') or book.author != request.user.author_profile:
            return Response({
                "error": "Forbidden",
                "message": "You do not have permission to view this book."
            }, status=status.HTTP_403_FORBIDDEN)

    serializer = BookListSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 6. Author Dashboard Stats API
# GET /api/v1/authors/me/dashboard
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def author_dashboard_stats(request):
    """Returns aggregated portfolio & royalty metrics for the logged-in author."""
    user = request.user
    if user.role != 'author' or not hasattr(user, 'author_profile'):
        return Response({
            "error": "Forbidden",
            "message": "Only authors can access author dashboard statistics."
        }, status=status.HTTP_403_FORBIDDEN)

    author = user.author_profile
    books = author.books.all()

    total_books = books.count()
    published_books = books.filter(status='Published & Live').count()
    in_production_books = books.exclude(status__in=['Published & Live', 'Out of Print']).count()

    total_copies_sold = books.aggregate(s=Sum('total_copies_sold'))['s'] or 0
    total_royalty_earned = books.aggregate(s=Sum('total_royalty_earned'))['s'] or 0.00
    royalty_paid = books.aggregate(s=Sum('royalty_paid'))['s'] or 0.00
    royalty_pending = books.aggregate(s=Sum('royalty_pending'))['s'] or 0.00

    today = timezone.now().date()
    if today.day < 15:
        next_payout_date = today.replace(day=15).strftime('%Y-%m-%d')
    else:
        year = today.year + 1 if today.month == 12 else today.year
        month = 1 if today.month == 12 else today.month + 1
        next_payout_date = date(year, month, 15).strftime('%Y-%m-%d')

    data = {
        "total_books": total_books,
        "published_books": published_books,
        "in_production_books": in_production_books,
        "total_copies_sold": total_copies_sold,
        "total_royalty_earned": total_royalty_earned,
        "royalty_paid": royalty_paid,
        "royalty_pending": royalty_pending,
        "currency": "INR",
        "next_payout_date": next_payout_date
    }

    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 7. Support Tickets Module: List & Create
# GET  /api/v1/tickets
# POST /api/v1/tickets
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tickets_view(request):
    """
    GET  /api/v1/tickets: List support tickets with role filtering & search.
    POST /api/v1/tickets: Create a new support ticket (Author only).
    """
    user = request.user

    # GET: List Tickets
    if request.method == 'GET':
        if user.role == 'author':
            if not hasattr(user, 'author_profile'):
                return Response([], status=status.HTTP_200_OK)
            queryset = Ticket.objects.filter(author=user.author_profile)
        elif user.role == 'admin':
            queryset = Ticket.objects.all()
            author_id = request.query_params.get('author_id')
            if author_id:
                queryset = queryset.filter(author__author_id=author_id)
        else:
            queryset = Ticket.objects.none()

        # Query Filters
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        category_param = request.query_params.get('category')
        if category_param:
            queryset = queryset.filter(category=category_param)

        priority_param = request.query_params.get('priority')
        if priority_param:
            queryset = queryset.filter(priority=priority_param)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(subject__icontains=search) |
                Q(author__name__icontains=search) |
                Q(book__title__icontains=search)
            )

        serializer = TicketListSerializer(queryset.select_related('author', 'book'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST: Create New Ticket (Author only)
    elif request.method == 'POST':
        if user.role != 'author' or not hasattr(user, 'author_profile'):
            return Response({
                "error": "Forbidden",
                "message": "Only registered authors can create support tickets."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = TicketCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        author = user.author_profile
        ticket_id = get_next_ticket_id()
        subject = data['subject'].strip()
        description = data['description'].strip()

        # Check optional book
        book = None
        book_id = data.get('book_id')
        if book_id:
            book = Book.objects.filter(book_id=book_id, author=author).first()

        # AI Auto-Classification & Priority Scoring (with graceful fallback)
        from .ai_service import classify_and_score_ticket, generate_ai_draft_response
        ai_triage = classify_and_score_ticket(subject, description)
        category = data.get('category') or ai_triage.get('category', 'General Inquiry')
        priority = data.get('priority') or ai_triage.get('priority', 'Medium')

        with transaction.atomic():
            ticket = Ticket.objects.create(
                id=ticket_id,
                author=author,
                book=book,
                subject=subject,
                description=description,
                category=category,
                priority=priority,
                status='Open',
                attachment_name=data.get('attachment_name'),
                attachment_size=data.get('attachment_size')
            )

            # Auto-create initial message in conversation thread
            TicketMessage.objects.create(
                ticket=ticket,
                sender_type='author',
                sender_name=user.name,
                sender_role='Author',
                content=description
            )

            # Auto-generate initial AI Draft response grounded in BookLeaf Knowledge Base
            draft_info = generate_ai_draft_response(ticket, author_name=author.name, book_title=book.title if book else None)
            ticket.ai_draft_content = draft_info['draft_content']
            ticket.ai_source_policies = draft_info['source_policies']
            ticket.ai_confidence_score = draft_info['confidence_score']
            ticket.save(update_fields=['ai_draft_content', 'ai_source_policies', 'ai_confidence_score'])

        detail_serializer = TicketDetailSerializer(ticket, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


# ==========================================
# 8. Single Ticket Details & Management API
# GET   /api/v1/tickets/<str:ticket_id>
# PATCH /api/v1/tickets/<str:ticket_id>
# ==========================================
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def ticket_detail_view(request, ticket_id):
    """
    GET   /api/v1/tickets/<ticket_id> - View full ticket thread & history
    PATCH /api/v1/tickets/<ticket_id> - Update status, priority, or assigned admin
    """
    user = request.user
    ticket = Ticket.objects.filter(id=ticket_id).select_related('author', 'book').first()
    if not ticket:
        return Response({
            "error": "Not Found",
            "message": f"Ticket with ID '{ticket_id}' does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    # Permission check for Author
    if user.role == 'author':
        if not hasattr(user, 'author_profile') or ticket.author != user.author_profile:
            return Response({
                "error": "Forbidden",
                "message": "You do not have permission to access this ticket."
            }, status=status.HTTP_403_FORBIDDEN)

    # GET: Retrieve full details
    if request.method == 'GET':
        serializer = TicketDetailSerializer(ticket, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PATCH: Update ticket status / priority / assignment
    elif request.method == 'PATCH':
        serializer = TicketUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        # Author can only change status to 'Resolved' or 'Closed'
        if user.role == 'author':
            new_status = data.get('status')
            if new_status and new_status in ['Resolved', 'Closed']:
                ticket.status = new_status
                ticket.save()
            else:
                return Response({
                    "error": "Forbidden",
                    "message": "Authors can only update status to Resolved or Closed."
                }, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'admin':
            if 'status' in data:
                ticket.status = data['status']
            if 'priority' in data:
                ticket.priority = data['priority']
            if 'assigned_to' in data:
                ticket.assigned_to = data['assigned_to']
            ticket.save()

        serializer = TicketDetailSerializer(ticket, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 9. Ticket Communication Thread Messages
# POST /api/v1/tickets/<str:ticket_id>/messages
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticket_messages_view(request, ticket_id):
    """Post a reply to the ticket communication thread."""
    user = request.user
    ticket = Ticket.objects.filter(id=ticket_id).select_related('author').first()
    if not ticket:
        return Response({
            "error": "Not Found",
            "message": f"Ticket '{ticket_id}' not found."
        }, status=status.HTTP_404_NOT_FOUND)

    # Author permission check
    if user.role == 'author':
        if not hasattr(user, 'author_profile') or ticket.author != user.author_profile:
            return Response({
                "error": "Forbidden",
                "message": "You cannot message on this ticket."
            }, status=status.HTTP_403_FORBIDDEN)

    serializer = TicketMessageCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    content = serializer.validated_data['content'].strip()
    sender_type = 'admin' if user.role == 'admin' else 'author'
    sender_role = 'Operations Desk' if user.role == 'admin' else 'Author'

    with transaction.atomic():
        message = TicketMessage.objects.create(
            ticket=ticket,
            sender_type=sender_type,
            sender_name=user.name,
            sender_role=sender_role,
            content=content
        )

        # If author replies to resolved ticket, re-open it
        if user.role == 'author' and ticket.status in ['Resolved', 'Closed']:
            ticket.status = 'In Progress'
        elif user.role == 'admin' and ticket.status == 'Open':
            ticket.status = 'In Progress'
        ticket.save()

    return Response(TicketMessageSerializer(message).data, status=status.HTTP_201_CREATED)


# ==========================================
# 10. Internal Notes (Admin Operations Only)
# POST /api/v1/tickets/<str:ticket_id>/internal-notes
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticket_internal_notes_view(request, ticket_id):
    """Add private internal operational note (Admin only)."""
    user = request.user
    if user.role != 'admin':
        return Response({
            "error": "Forbidden",
            "message": "Only admin operations staff can add internal notes."
        }, status=status.HTTP_403_FORBIDDEN)

    ticket = Ticket.objects.filter(id=ticket_id).first()
    if not ticket:
        return Response({
            "error": "Not Found",
            "message": f"Ticket '{ticket_id}' not found."
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = InternalNoteCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "error": "Validation failed",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    note = InternalNote.objects.create(
        ticket=ticket,
        admin_name=user.name,
        note=serializer.validated_data['note'].strip()
    )

    return Response(InternalNoteSerializer(note).data, status=status.HTTP_201_CREATED)


# ==========================================
# 11. Admin Operations Desk Stats API
# GET /api/v1/admin/operations/stats
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def operations_desk_stats_view(request):
    """Returns overview metrics for the Operations Desk (Admin only)."""
    if request.user.role != 'admin':
        return Response({
            "error": "Forbidden",
            "message": "Only admins can access operations desk metrics."
        }, status=status.HTTP_403_FORBIDDEN)

    data = {
        "total_tickets": Ticket.objects.count(),
        "open_tickets": Ticket.objects.filter(status='Open').count(),
        "in_progress_tickets": Ticket.objects.filter(status='In Progress').count(),
        "resolved_tickets": Ticket.objects.filter(status='Resolved').count(),
        "closed_tickets": Ticket.objects.filter(status='Closed').count(),
        "critical_tickets": Ticket.objects.filter(priority='Critical').count(),
    }

    serializer = OperationsDeskStatsSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# 12. Regenerate AI Draft API
# POST /api/v1/tickets/<str:ticket_id>/generate-ai-draft
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_ticket_ai_draft_view(request, ticket_id):
    """Regenerates AI Draft response for a ticket on demand."""
    ticket = Ticket.objects.filter(id=ticket_id).select_related('author', 'book').first()
    if not ticket:
        return Response({
            "error": "Not Found",
            "message": f"Ticket '{ticket_id}' not found."
        }, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'author':
        if not hasattr(request.user, 'author_profile') or ticket.author != request.user.author_profile:
            return Response({
                "error": "Forbidden",
                "message": "You do not have permission to access this ticket."
            }, status=status.HTTP_403_FORBIDDEN)

    from .ai_service import generate_ai_draft_response
    draft_info = generate_ai_draft_response(ticket)

    ticket.ai_draft_content = draft_info['draft_content']
    ticket.ai_source_policies = draft_info['source_policies']
    ticket.ai_confidence_score = draft_info['confidence_score']
    ticket.save(update_fields=['ai_draft_content', 'ai_source_policies', 'ai_confidence_score'])

    return Response({
        "status": "success",
        "message": "AI Draft generated successfully.",
        "ticket_id": ticket.id,
        "ai_draft": draft_info
    }, status=status.HTTP_200_OK)


# ==========================================
# 13. Health Check API
# GET /api/health/
# ==========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        "status": "success",
        "message": "BookLeaf Django API backend is working properly!",
        "version": "1.0.0"
    }, status=status.HTTP_200_OK)
