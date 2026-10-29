import os
import json
import re
import requests

BOOKLEAF_KNOWLEDGE_BASE = 

VALID_CATEGORIES = [
    'Royalty & Payments',
    'ISBN & Metadata Issues',
    'Printing & Quality',
    'Distribution & Availability',
    'Book Status & Production Updates',
    'General Inquiry'
]

VALID_PRIORITIES = ['Critical', 'High', 'Medium', 'Low']

def get_ai_config():

    api_key = os.getenv('AI_API_KEY', '').strip()
    provider = os.getenv('AI_PROVIDER', 'gemini').lower().strip()
    model = os.getenv('AI_MODEL', '').strip()

    if not model:
        if provider == 'openai':
            model = 'gpt-4o-mini'
        elif provider == 'anthropic':
            model = 'claude-3-haiku-20240307'
        else:
            model = 'gemini-1.5-flash'

    return {
        'api_key': api_key,
        'provider': provider,
        'model': model
    }

def fallback_classify_and_score(subject: str, description: str) -> dict:

    text = f"{subject} {description}".lower()

    if any(k in text for k in ['urgent', 'emergency', 'legal', 'lawsuit', 'unauthorized', 'halt', 'critical', 'copyright infringement']):
        priority = 'Critical'
    elif any(k in text for k in ['discrepancy', 'not received', 'wrong amount', 'missing copies', 'delayed by', 'unresolved', 'damaged batch']):
        priority = 'High'
    elif any(k in text for k in ['question', 'how to', 'general', 'curious', 'query', 'just wondering', 'information']):
        priority = 'Low'
    else:
        priority = 'Medium'

    if any(k in text for k in ['royalty', 'payout', 'payment', 'bank', 'earnings', 'neft', 'statement', 'sales report', 'threshold', '80/20']):
        category = 'Royalty & Payments'
    elif any(k in text for k in ['isbn', 'barcode', 'metadata', 'imprint', 'copyright', 'author name typo', 'blurb error']):
        category = 'ISBN & Metadata Issues'
    elif any(k in text for k in ['print', 'cover', 'binding', 'paper', 'smudge', 'defect', 'damaged', 'lamination', 'matte', 'gloss', 'misprint']):
        category = 'Printing & Quality'
    elif any(k in text for k in ['amazon', 'flipkart', 'out of stock', 'distribution', 'listing', 'buy link', 'marketplace', 'store inventory']):
        category = 'Distribution & Availability'
    elif any(k in text for k in ['production', 'typesetting', 'typeset', 'proofreading', 'manuscript', 'stage', 'status update', 'cover design']):
        category = 'Book Status & Production Updates'
    else:
        category = 'General Inquiry'

    return {
        'category': category,
        'priority': priority,
        'confidence_score': 0.88,
        'source': 'Heuristic Classifier'
    }

def classify_and_score_ticket(subject: str, description: str) -> dict:

    config = get_ai_config()
    api_key = config['api_key']
    provider = config['provider']
    model = config['model']

    if not api_key:
        return fallback_classify_and_score(subject, description)

    prompt = f

    try:
        raw_text = ""
        if provider == 'openai':
            resp = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={
                    'model': model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.1,
                    'response_format': {'type': 'json_object'}
                },
                timeout=6
            )
            if resp.status_code == 200:
                raw_text = resp.json()['choices'][0]['message']['content']

        elif provider == 'gemini':
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            resp = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json={
                    'contents': [{'parts': [{'text': prompt}]}],
                    'generationConfig': {'temperature': 0.1}
                },
                timeout=6
            )
            if resp.status_code == 200:
                raw_text = resp.json()['candidates'][0]['content']['parts'][0]['text']

        if raw_text:
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                category = data.get('category')
                priority = data.get('priority')
                confidence = float(data.get('confidence_score', 0.92))

                if category in VALID_CATEGORIES and priority in VALID_PRIORITIES:
                    return {
                        'category': category,
                        'priority': priority,
                        'confidence_score': confidence,
                        'source': f"LLM ({provider})"
                    }
    except Exception as e:
        print(f"[AI Service] Classification call failed: {e}. Falling back to heuristics.")

    return fallback_classify_and_score(subject, description)

def fallback_generate_draft(category: str, subject: str, description: str, author_name: str, book_title: str) -> dict:

    name = author_name or "Author"
    book_ref = f" regarding '{book_title}'" if book_title else ""

    if category == 'Royalty & Payments':
        draft = (
            f"Dear {name},\n\n"
            f"Thank you for contacting BookLeaf Author Operations{book_ref}.\n\n"
            f"We have noted your inquiry: \"{subject}\". Under BookLeaf's 80/20 Royalty Policy, authors receive 80% of net profits (MRP minus print cost, distribution fee, and shipping). "
            f"Royalties are calculated on a quarterly cycle and disbursed within 45 days of quarter end to registered accounts meeting the ₹1,000 minimum threshold.\n\n"
            f"Our finance desk has pulled your sales logs to reconcile your reporting. We will verify the ledger with partner channels and update this thread within 24–48 business hours.\n\n"
            f"Warm regards,\n"
            f"BookLeaf Operations Desk"
        )
        policies = ["Royalty & Payments Policy (80/20 Net Split)", "Quarterly Payout Schedule & ₹1,000 Threshold"]
        confidence = 0.94

    elif category == 'Printing & Quality':
        draft = (
            f"Dear {name},\n\n"
            f"Thank you for reaching out to BookLeaf Operations{book_ref}.\n\n"
            f"We take our print standards very seriously. In accordance with BookLeaf Printing & Quality Policy, all production orders follow a 5–7 business day turnaround. "
            f"If you have received defective or damaged copies, please attach photos of the affected books here. Upon review, we will initiate a 100% free reprint replacement immediately.\n\n"
            f"Our team has flagged your ticket for express print verification.\n\n"
            f"Warm regards,\n"
            f"BookLeaf Operations Desk"
        )
        policies = ["Printing Turnaround (5–7 Business Days)", "100% Free Defect Replacement Policy"]
        confidence = 0.92

    elif category == 'ISBN & Metadata Issues':
        draft = (
            f"Dear {name},\n\n"
            f"Thank you for writing to BookLeaf Operations{book_ref}.\n\n"
            f"Regarding your query on \"{subject}\": BookLeaf assigns unique registered ISBNs under our imprint for each published format. "
            f"Our metadata specialists have queued this for review. As per our turnaround standards, ISBN and catalog indexing discrepancies are resolved and escalated within 48 business hours.\n\n"
            f"We will update you as soon as the corrections reflect on national bibliographic databases.\n\n"
            f"Warm regards,\n"
            f"BookLeaf Operations Desk"
        )
        policies = ["ISBN Registration & Imprint Guidelines", "48-Hour Metadata Escalation Standard"]
        confidence = 0.93

    elif category == 'Distribution & Availability':
        draft = (
            f"Dear {name},\n\n"
            f"Thank you for contacting us{book_ref}.\n\n"
            f"Under BookLeaf Distribution Policy, new titles are syndicated to Amazon, Flipkart, and the BookLeaf Store within 7–10 business days of production sign-off. "
            f"If you are noticing temporary out-of-stock notices, partner channel inventory feeds synchronize automatically every 24–48 hours.\n\n"
            f"We have pinged our marketplace feed manager to force an inventory sync for your title.\n\n"
            f"Warm regards,\n"
            f"BookLeaf Operations Desk"
        )
        policies = ["Channel Listing Timelines (7–10 Days)", "Inventory Sync Protocol (24–48 Hours)"]
        confidence = 0.91

    elif category == 'Book Status & Production Updates':
        draft = (
            f"Dear {name},\n\n"
            f"Thank you for following up on your book's production progress{book_ref}.\n\n"
            f"Every manuscript at BookLeaf transitions through typesetting, cover review, and final proofreading. "
            f"Our typesetting desk typically completes interior revisions within 3–5 business days. Your manuscript is currently with our production leads and moving on schedule.\n\n"
            f"We will notify you the moment your next milestone is ready for author sign-off.\n\n"
            f"Warm regards,\n"
            f"BookLeaf Production Team"
        )
        policies = ["Production Pipeline Guidelines", "Author Review Turnaround (3–5 Days)"]
        confidence = 0.90

    else:
        draft = (
            f"Dear {name},\n\n"
            f"Thank you for reaching out to BookLeaf Author Support Desk{book_ref}.\n\n"
            f"We have received your message regarding \"{subject}\". An operations specialist has been assigned to your ticket and will review your request thoroughly in accordance with BookLeaf Author Support Guidelines.\n\n"
            f"Expect a personalized follow-up on this thread within 24 business hours.\n\n"
            f"Warm regards,\n"
            f"BookLeaf Operations Desk"
        )
        policies = ["General Author Support SLA (24 Hours)"]
        confidence = 0.88

    return {
        'draft_content': draft,
        'source_policies': policies,
        'confidence_score': confidence
    }

def generate_ai_draft_response(ticket, author_name: str = None, book_title: str = None) -> dict:

    name = author_name or (ticket.author.name if ticket.author else "Author")
    title = book_title or (ticket.book.title if ticket.book else "")

    config = get_ai_config()
    api_key = config['api_key']
    provider = config['provider']
    model = config['model']

    if not api_key:
        return fallback_generate_draft(ticket.category, ticket.subject, ticket.description, name, title)

    system_instruction = f

    user_prompt = f

    try:
        raw_text = ""
        if provider == 'openai':
            resp = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={
                    'model': model,
                    'messages': [
                        {'role': 'system', 'content': system_instruction},
                        {'role': 'user', 'content': user_prompt}
                    ],
                    'temperature': 0.3,
                    'response_format': {'type': 'json_object'}
                },
                timeout=10
            )
            if resp.status_code == 200:
                raw_text = resp.json()['choices'][0]['message']['content']

        elif provider == 'gemini':
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            resp = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json={
                    'contents': [{'parts': [{'text': f"{system_instruction}\n\n{user_prompt}"}]}],
                    'generationConfig': {'temperature': 0.3}
                },
                timeout=10
            )
            if resp.status_code == 200:
                raw_text = resp.json()['candidates'][0]['content']['parts'][0]['text']

        if raw_text:
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                draft = data.get('draft_content')
                policies = data.get('source_policies', ['BookLeaf Operations Policy'])
                confidence = float(data.get('confidence_score', 0.94))
                if draft:
                    return {
                        'draft_content': draft,
                        'source_policies': policies,
                        'confidence_score': confidence
                    }
    except Exception as e:
        print(f"[AI Service] Draft generation failed: {e}. Falling back to knowledge templates.")

    return fallback_generate_draft(ticket.category, ticket.subject, ticket.description, name, title)
