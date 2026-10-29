from django.urls import path
from .views import (
    register, 
    login, 
    me, 
    books_view, 
    book_detail, 
    author_dashboard_stats, 
    tickets_view,
    ticket_detail_view,
    ticket_messages_view,
    ticket_internal_notes_view,
    operations_desk_stats_view,
    generate_ticket_ai_draft_view,
    health_check
)

urlpatterns = [
    # Health Check
    path('health/', health_check, name='health-check'),

    # 1. Auth Endpoints
    path('v1/auth/register', register, name='auth-register'),
    path('v1/auth/register/', register, name='auth-register-slash'),
    
    path('v1/auth/login', login, name='auth-login'),
    path('v1/auth/login/', login, name='auth-login-slash'),
    
    path('v1/auth/me', me, name='auth-me'),
    path('v1/auth/me/', me, name='auth-me-slash'),

    # 2. Books & Royalties Module Endpoints
    path('v1/books', books_view, name='books-list-create'),
    path('v1/books/', books_view, name='books-list-create-slash'),

    path('v1/books/<str:book_id>', book_detail, name='book-detail'),
    path('v1/books/<str:book_id>/', book_detail, name='book-detail-slash'),

    # 3. Author Dashboard & Royalties Stats
    path('v1/authors/me/dashboard', author_dashboard_stats, name='author-dashboard-stats'),
    path('v1/authors/me/dashboard/', author_dashboard_stats, name='author-dashboard-stats-slash'),

    # 4. Support Tickets & Operations Desk Endpoints
    path('v1/tickets', tickets_view, name='tickets-list-create'),
    path('v1/tickets/', tickets_view, name='tickets-list-create-slash'),

    path('v1/tickets/<str:ticket_id>', ticket_detail_view, name='ticket-detail'),
    path('v1/tickets/<str:ticket_id>/', ticket_detail_view, name='ticket-detail-slash'),

    path('v1/tickets/<str:ticket_id>/messages', ticket_messages_view, name='ticket-messages'),
    path('v1/tickets/<str:ticket_id>/messages/', ticket_messages_view, name='ticket-messages-slash'),

    path('v1/tickets/<str:ticket_id>/internal-notes', ticket_internal_notes_view, name='ticket-internal-notes'),
    path('v1/tickets/<str:ticket_id>/internal-notes/', ticket_internal_notes_view, name='ticket-internal-notes-slash'),

    # 5. AI-Assisted Operations Desk Draft Generation
    path('v1/tickets/<str:ticket_id>/generate-ai-draft', generate_ticket_ai_draft_view, name='generate-ai-draft'),
    path('v1/tickets/<str:ticket_id>/generate-ai-draft/', generate_ticket_ai_draft_view, name='generate-ai-draft-slash'),

    # 6. Admin Operations Desk Stats
    path('v1/admin/operations/stats', operations_desk_stats_view, name='operations-desk-stats'),
    path('v1/admin/operations/stats/', operations_desk_stats_view, name='operations-desk-stats-slash'),
]
