"""
Django Management Command: seed_sample_data
Seeds the official BookLeaf technical assignment dataset:
- 1 Admin Account (Devansh Joshi)
- 10 Author Accounts (AUTH001 - AUTH010)
- 18 Books (BK001 - BK018)
- Initial Support Tickets with AI drafts and communication threads
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import User, Author, Book, Ticket, TicketMessage, InternalNote
from api.ai_service import generate_ai_draft_response
from datetime import date

class Command(BaseCommand):
    help = 'Seeds official BookLeaf assignment dataset (1 Admin, 10 Authors, 18 Books, Support Tickets)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("=================================================="))
        self.stdout.write(self.style.NOTICE("  BookLeaf Assignment Official Dataset Seeder    "))
        self.stdout.write(self.style.NOTICE("=================================================="))

        with transaction.atomic():
            # ----------------------------------------------------
            # 1. Admin Account
            # ----------------------------------------------------
            admin_user, _ = User.objects.get_or_create(
                email="admin@bookleaf.com",
                defaults={
                    'name': 'Devansh Joshi',
                    'role': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            admin_user.set_password("password123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[✓] Admin Account: admin@bookleaf.com (Devansh Joshi)"))

            # ----------------------------------------------------
            # 2. 10 Author Accounts
            # ----------------------------------------------------
            authors_data = [
                {"id": "AUTH001", "name": "Priya Sharma", "email": "priya.sharma@email.com", "city": "Mumbai", "phone": "+91-98765-43210"},
                {"id": "AUTH002", "name": "Rohit Kapoor", "email": "rohit.kapoor@email.com", "city": "Delhi", "phone": "+91-87654-32109"},
                {"id": "AUTH003", "name": "Ananya Reddy", "email": "ananya.reddy@email.com", "city": "Hyderabad", "phone": "+91-76543-21098"},
                {"id": "AUTH004", "name": "Vikram Malhotra", "email": "vikram.malhotra@email.com", "city": "Bangalore", "phone": "+91-65432-10987"},
                {"id": "AUTH005", "name": "Sneha Patel", "email": "sneha.patel@email.com", "city": "Ahmedabad", "phone": "+91-54321-09876"},
                {"id": "AUTH006", "name": "Arvind Swaminathan", "email": "arvind.swaminathan@email.com", "city": "Chennai", "phone": "+91-43210-98765"},
                {"id": "AUTH007", "name": "Meera Nambiar", "email": "meera.nambiar@email.com", "city": "Kochi", "phone": "+91-32109-87654"},
                {"id": "AUTH008", "name": "Kabir Mehta", "email": "kabir.mehta@email.com", "city": "Pune", "phone": "+91-21098-76543"},
                {"id": "AUTH009", "name": "Sunita Deshmukh", "email": "sunita.deshmukh@email.com", "city": "Nagpur", "phone": "+91-10987-65432"},
                {"id": "AUTH010", "name": "Tanmay Joshi", "email": "tanmay.joshi@email.com", "city": "Jaipur", "phone": "+91-99887-76655"},
            ]

            author_objs = {}
            for ad in authors_data:
                u, _ = User.objects.get_or_create(
                    email=ad['email'],
                    defaults={'name': ad['name'], 'role': 'author'}
                )
                u.name = ad['name']
                u.set_password("password123")
                u.save()

                a, _ = Author.objects.get_or_create(
                    author_id=ad['id'],
                    defaults={
                        'user': u,
                        'name': ad['name'],
                        'email': ad['email'],
                        'city': ad['city'],
                        'phone': ad['phone']
                    }
                )
                a.user = u
                a.name = ad['name']
                a.email = ad['email']
                a.city = ad['city']
                a.phone = ad['phone']
                a.save()
                author_objs[ad['id']] = a
                self.stdout.write(f"    Author {ad['id']}: {ad['name']} ({ad['city']})")

            self.stdout.write(self.style.SUCCESS("[✓] All 10 Author Accounts Seeded."))

            # ----------------------------------------------------
            # 3. 18 Books Seeding
            # ----------------------------------------------------
            books_data = [
                # Priya Sharma (AUTH001)
                {
                    "book_id": "BK001", "author_id": "AUTH001",
                    "title": "Whispers of the Ganges", "isbn": "978-81-923456-7-8", "genre": "Contemporary Fiction",
                    "publication_date": date(2025, 8, 15), "status": "Published & Live", "mrp": 349.00,
                    "author_royalty_per_copy": 70.00, "total_copies_sold": 140, "total_royalty_earned": 9800.00,
                    "royalty_paid": 7000.00, "royalty_pending": 2800.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                {
                    "book_id": "BK002", "author_id": "AUTH001",
                    "title": "The Saffron Diaries", "isbn": "978-81-923456-8-5", "genre": "Historical Romance",
                    "publication_date": date(2026, 1, 20), "status": "Published & Live", "mrp": 399.00,
                    "author_royalty_per_copy": 80.00, "total_copies_sold": 95, "total_royalty_earned": 7600.00,
                    "royalty_paid": 5000.00, "royalty_pending": 2600.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                # Rohit Kapoor (AUTH002)
                {
                    "book_id": "BK003", "author_id": "AUTH002",
                    "title": "Code & Karma", "isbn": "978-81-934567-0-1", "genre": "Tech & Philosophy",
                    "publication_date": date(2025, 9, 10), "status": "Published & Live", "mrp": 299.00,
                    "author_royalty_per_copy": 60.00, "total_copies_sold": 210, "total_royalty_earned": 12600.00,
                    "royalty_paid": 10000.00, "royalty_pending": 2600.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                {
                    "book_id": "BK004", "author_id": "AUTH002",
                    "title": "Startup Sutra", "isbn": "978-81-934567-1-8", "genre": "Business & Entrepreneurship",
                    "publication_date": date(2026, 3, 5), "status": "In Production - Typesetting", "mrp": 449.00,
                    "author_royalty_per_copy": 90.00, "total_copies_sold": 0, "total_royalty_earned": 0.00,
                    "royalty_paid": 0.00, "royalty_pending": 0.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store"]
                },
                # Ananya Reddy (AUTH003)
                {
                    "book_id": "BK005", "author_id": "AUTH003",
                    "title": "Cyber City Blues", "isbn": "978-81-945678-2-2", "genre": "Crime & Mystery",
                    "publication_date": date(2025, 7, 22), "status": "Published & Live", "mrp": 299.00,
                    "author_royalty_per_copy": 60.00, "total_copies_sold": 180, "total_royalty_earned": 10800.00,
                    "royalty_paid": 8000.00, "royalty_pending": 2800.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon"]
                },
                {
                    "book_id": "BK006", "author_id": "AUTH003",
                    "title": "Tales from Charminar", "isbn": "978-81-945678-3-9", "genre": "Short Stories",
                    "publication_date": date(2025, 11, 14), "status": "Published & Live", "mrp": 249.00,
                    "author_royalty_per_copy": 50.00, "total_copies_sold": 130, "total_royalty_earned": 6500.00,
                    "royalty_paid": 4500.00, "royalty_pending": 2000.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                # Vikram Malhotra (AUTH004)
                {
                    "book_id": "BK007", "author_id": "AUTH004",
                    "title": "Silicon Valley Desi", "isbn": "978-81-956789-4-3", "genre": "Memoir / Non-Fiction",
                    "publication_date": date(2025, 10, 1), "status": "Published & Live", "mrp": 499.00,
                    "author_royalty_per_copy": 100.00, "total_copies_sold": 160, "total_royalty_earned": 16000.00,
                    "royalty_paid": 12000.00, "royalty_pending": 4000.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                {
                    "book_id": "BK008", "author_id": "AUTH004",
                    "title": "Coffee at Brigade Road", "isbn": "978-81-956789-5-0", "genre": "Literary Fiction",
                    "publication_date": date(2026, 2, 18), "status": "Cover Design & Review", "mrp": 329.00,
                    "author_royalty_per_copy": 65.00, "total_copies_sold": 0, "total_royalty_earned": 0.00,
                    "royalty_paid": 0.00, "royalty_pending": 0.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store"]
                },
                # Sneha Patel (AUTH005)
                {
                    "book_id": "BK009", "author_id": "AUTH005",
                    "title": "Dhandha: The Gujarati Way", "isbn": "978-81-967890-6-4", "genre": "Business & Finance",
                    "publication_date": date(2025, 6, 12), "status": "Published & Live", "mrp": 399.00,
                    "author_royalty_per_copy": 80.00, "total_copies_sold": 320, "total_royalty_earned": 25600.00,
                    "royalty_paid": 20000.00, "royalty_pending": 5600.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                {
                    "book_id": "BK010", "author_id": "AUTH005",
                    "title": "Sabarmati Sunsets", "isbn": "978-81-967890-7-1", "genre": "Poetry",
                    "publication_date": date(2025, 12, 5), "status": "Published & Live", "mrp": 199.00,
                    "author_royalty_per_copy": 40.00, "total_copies_sold": 85, "total_royalty_earned": 3400.00,
                    "royalty_paid": 2500.00, "royalty_pending": 900.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon"]
                },
                # Arvind Swaminathan (AUTH006)
                {
                    "book_id": "BK011", "author_id": "AUTH006",
                    "title": "Filter Coffee & Carnatic", "isbn": "978-81-978901-8-5", "genre": "Culture & Arts",
                    "publication_date": date(2025, 5, 20), "status": "Published & Live", "mrp": 299.00,
                    "author_royalty_per_copy": 60.00, "total_copies_sold": 115, "total_royalty_earned": 6900.00,
                    "royalty_paid": 5000.00, "royalty_pending": 1900.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon"]
                },
                {
                    "book_id": "BK012", "author_id": "AUTH006",
                    "title": "The Temple City Chronicles", "isbn": "978-81-978901-9-2", "genre": "Historical Fiction",
                    "publication_date": date(2026, 4, 10), "status": "In Production - Typesetting", "mrp": 379.00,
                    "author_royalty_per_copy": 75.00, "total_copies_sold": 0, "total_royalty_earned": 0.00,
                    "royalty_paid": 0.00, "royalty_pending": 0.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store"]
                },
                # Meera Nambiar (AUTH007)
                {
                    "book_id": "BK013", "author_id": "AUTH007",
                    "title": "Backwaters & Beyond", "isbn": "978-81-989012-0-8", "genre": "Travelogue",
                    "publication_date": date(2025, 9, 30), "status": "Published & Live", "mrp": 349.00,
                    "author_royalty_per_copy": 70.00, "total_copies_sold": 150, "total_royalty_earned": 10500.00,
                    "royalty_paid": 8000.00, "royalty_pending": 2500.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                {
                    "book_id": "BK014", "author_id": "AUTH007",
                    "title": "Monsoon in Malabar", "isbn": "978-81-989012-1-5", "genre": "Romance",
                    "publication_date": date(2026, 1, 15), "status": "Proofreading & Final Edits", "mrp": 279.00,
                    "author_royalty_per_copy": 55.00, "total_copies_sold": 0, "total_royalty_earned": 0.00,
                    "royalty_paid": 0.00, "royalty_pending": 0.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store"]
                },
                # Kabir Mehta (AUTH008)
                {
                    "book_id": "BK015", "author_id": "AUTH008",
                    "title": "Maratha Shadows", "isbn": "978-81-990123-2-2", "genre": "Historical Thriller",
                    "publication_date": date(2025, 4, 18), "status": "Published & Live", "mrp": 399.00,
                    "author_royalty_per_copy": 80.00, "total_copies_sold": 240, "total_royalty_earned": 19200.00,
                    "royalty_paid": 15000.00, "royalty_pending": 4200.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                {
                    "book_id": "BK016", "author_id": "AUTH008",
                    "title": "Forts of Freedom", "isbn": "978-81-990123-3-9", "genre": "History & Heritage",
                    "publication_date": date(2025, 10, 25), "status": "Published & Live", "mrp": 449.00,
                    "author_royalty_per_copy": 90.00, "total_copies_sold": 175, "total_royalty_earned": 15750.00,
                    "royalty_paid": 12000.00, "royalty_pending": 3750.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
                # Sunita Deshmukh (AUTH009)
                {
                    "book_id": "BK017", "author_id": "AUTH009",
                    "title": "Orange City Stories", "isbn": "978-81-991234-4-6", "genre": "Social Realism",
                    "publication_date": date(2025, 8, 8), "status": "Published & Live", "mrp": 249.00,
                    "author_royalty_per_copy": 50.00, "total_copies_sold": 90, "total_royalty_earned": 4500.00,
                    "royalty_paid": 3500.00, "royalty_pending": 1000.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon"]
                },
                # Tanmay Joshi (AUTH010)
                {
                    "book_id": "BK018", "author_id": "AUTH010",
                    "title": "The Pink City Mirage", "isbn": "978-81-992345-5-3", "genre": "Mystery & Detective",
                    "publication_date": date(2025, 11, 20), "status": "Published & Live", "mrp": 319.00,
                    "author_royalty_per_copy": 65.00, "total_copies_sold": 145, "total_royalty_earned": 9425.00,
                    "royalty_paid": 7000.00, "royalty_pending": 2425.00, "print_partner": "BookLeaf Express Print",
                    "available_on": ["BookLeaf Store", "Amazon", "Flipkart"]
                },
            ]

            for bd in books_data:
                author_obj = author_objs[bd['author_id']]
                book_obj, _ = Book.objects.get_or_create(
                    book_id=bd['book_id'],
                    defaults={
                        'author': author_obj,
                        'title': bd['title'],
                        'isbn': bd['isbn'],
                        'genre': bd['genre'],
                        'publication_date': bd['publication_date'],
                        'status': bd['status'],
                        'mrp': bd['mrp'],
                        'author_royalty_per_copy': bd['author_royalty_per_copy'],
                        'total_copies_sold': bd['total_copies_sold'],
                        'total_royalty_earned': bd['total_royalty_earned'],
                        'royalty_paid': bd['royalty_paid'],
                        'royalty_pending': bd['royalty_pending'],
                        'print_partner': bd['print_partner'],
                        'available_on': bd['available_on'],
                    }
                )
                book_obj.title = bd['title']
                book_obj.author = author_obj
                book_obj.isbn = bd['isbn']
                book_obj.genre = bd['genre']
                book_obj.publication_date = bd['publication_date']
                book_obj.status = bd['status']
                book_obj.mrp = bd['mrp']
                book_obj.author_royalty_per_copy = bd['author_royalty_per_copy']
                book_obj.total_copies_sold = bd['total_copies_sold']
                book_obj.total_royalty_earned = bd['total_royalty_earned']
                book_obj.royalty_paid = bd['royalty_paid']
                book_obj.royalty_pending = bd['royalty_pending']
                book_obj.print_partner = bd['print_partner']
                book_obj.available_on = bd['available_on']
                book_obj.save()
                self.stdout.write(f"    Book {bd['book_id']}: {bd['title']} ({bd['status']})")

            self.stdout.write(self.style.SUCCESS("[✓] All 18 Official Books Seeded."))

            # ----------------------------------------------------
            # 4. Realistic Support Tickets with AI Drafts
            # ----------------------------------------------------
            tickets_seed = [
                {
                    "id": "TKT-2026-1001",
                    "author": author_objs["AUTH001"],
                    "book_id": "BK001",
                    "subject": "Royalty payout discrepancy for Q3 2025",
                    "description": "I noticed that the royalty calculation for September copies shows 140 sold, but received payout was for 100 copies.",
                    "category": "Royalty & Payments",
                    "priority": "High",
                    "status": "In Progress",
                    "assigned_to": "Devansh Joshi",
                    "attachment_name": "sales_report_sept.pdf",
                    "attachment_size": "1.2 MB"
                },
                {
                    "id": "TKT-2026-1002",
                    "author": author_objs["AUTH001"],
                    "book_id": "BK001",
                    "subject": "ISBN Barcode positioning on back cover",
                    "description": "Please ensure the ISBN barcode does not overlap with the author bio summary on the back cover.",
                    "category": "ISBN & Metadata Issues",
                    "priority": "Medium",
                    "status": "Open",
                    "assigned_to": None,
                    "attachment_name": None,
                    "attachment_size": None
                },
                {
                    "id": "TKT-2026-1003",
                    "author": author_objs["AUTH002"],
                    "book_id": "BK004",
                    "subject": "Interior typesetting font size inquiry",
                    "description": "For Startup Sutra, can we increase the body font from 10pt to 11pt Garamond for readability?",
                    "category": "Book Status & Production Updates",
                    "priority": "Medium",
                    "status": "In Progress",
                    "assigned_to": "Devansh Joshi",
                    "attachment_name": "chapter1_sample.docx",
                    "attachment_size": "850 KB"
                },
                {
                    "id": "TKT-2026-1004",
                    "author": author_objs["AUTH005"],
                    "book_id": "BK009",
                    "subject": "Amazon India listing temporarily showing Out of Stock",
                    "description": "Readers from Mumbai are reporting that Dhandha is showing currently unavailable on Amazon India.",
                    "category": "Distribution & Availability",
                    "priority": "High",
                    "status": "Open",
                    "assigned_to": None,
                    "attachment_name": None,
                    "attachment_size": None
                },
                {
                    "id": "TKT-2026-1005",
                    "author": author_objs["AUTH008"],
                    "book_id": "BK015",
                    "subject": "Smudged cover print on 10 author copies",
                    "description": "Received the 20 author copies box yesterday. 10 copies have noticeable ink smudges on the spine and front title.",
                    "category": "Printing & Quality",
                    "priority": "High",
                    "status": "Open",
                    "assigned_to": None,
                    "attachment_name": "damaged_copies.jpg",
                    "attachment_size": "3.4 MB"
                }
            ]

            for td in tickets_seed:
                book = Book.objects.filter(book_id=td['book_id']).first() if td['book_id'] else None
                t, created = Ticket.objects.get_or_create(
                    id=td['id'],
                    defaults={
                        'author': td['author'],
                        'book': book,
                        'subject': td['subject'],
                        'description': td['description'],
                        'category': td['category'],
                        'priority': td['priority'],
                        'status': td['status'],
                        'assigned_to': td['assigned_to'],
                        'attachment_name': td['attachment_name'],
                        'attachment_size': td['attachment_size']
                    }
                )
                if created:
                    # Initial message from author
                    TicketMessage.objects.create(
                        ticket=t,
                        sender_type='author',
                        sender_name=td['author'].name,
                        sender_role='Author',
                        content=td['description']
                    )
                    # If in progress, add reply from admin
                    if td['status'] == 'In Progress':
                        TicketMessage.objects.create(
                            ticket=t,
                            sender_type='admin',
                            sender_name='Devansh Joshi',
                            sender_role='Operations Desk',
                            content="Hello, our team has reviewed your inquiry and initiated verification with the respective department."
                        )
                        InternalNote.objects.create(
                            ticket=t,
                            admin_name='Devansh Joshi',
                            note='Internal verification initiated. Escalated with logistics/finance.'
                        )

                    # Generate initial AI Draft
                    draft_res = generate_ai_draft_response(t, author_name=td['author'].name, book_title=book.title if book else "")
                    t.ai_draft_content = draft_res['draft_content']
                    t.ai_source_policies = draft_res['source_policies']
                    t.ai_confidence_score = draft_res['confidence_score']
                    t.save(update_fields=['ai_draft_content', 'ai_source_policies', 'ai_confidence_score'])

                self.stdout.write(f"    Ticket {td['id']}: {td['subject'][:40]}... ({td['category']})")

            self.stdout.write(self.style.SUCCESS("[✓] Support Tickets with AI Drafts Seeded."))

        self.stdout.write(self.style.NOTICE("=================================================="))
        self.stdout.write(self.style.SUCCESS("✓ Official Dataset Seeding Complete! Ready for Evaluation."))
        self.stdout.write(self.style.NOTICE("=================================================="))
