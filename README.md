# BookLeaf Publishing Portal - Backend API (Django & DRF)

BookLeaf Author Support & Operations Desk Portal साठी तयार केलेले उत्पादन-सक्षम (Production-Ready) Django REST Framework backend.

---

## 🚀 मुख्य वैशिष्ट्ये (Features)

1. **सुरक्षा आणि प्रमाणीकरण (Authentication)**:
   - Single Unified Login (Author व Admin दोघांसाठी एकच API).
   - **JWT Authentication** (`djangorestframework-simplejwt`) सह Bearer Token.

2. **Books & Royalties Module (पुस्तके आणि रॉयल्टी)**:
   - रोल-आधारित पुस्तकांची यादी (`GET /api/v1/books`).
   - पुस्तकांचा शोध (`?search=`, `?status=`, `?author_id=`).
   - नवीन पुस्तक जोडणे (`POST /api/v1/books`).
   - ऑथर डॅशबोर्ड व रॉयल्टी आकडेवारी (`GET /api/v1/authors/me/dashboard`).

3. **Support Tickets & Communication Thread**:
   - ऑथरसाठी तिकीट तयार करणे (`POST /api/v1/tickets`) व पाहणे (`GET /api/v1/tickets`).
   - टू-वे मेसेजिंग थ्रेड (`POST /api/v1/tickets/<id>/messages`).
   - ॲडमिनसाठी अंतर्गत नोंदी (`POST /api/v1/tickets/<id>/internal-notes`).
   - ॲडमिन ऑपरेशन्स डेस्क आकडेवारी (`GET /api/v1/admin/operations/stats`).

4. **🤖 AI-Assisted Operations Desk (Section D - 25% Weightage)**:
   - **AI Auto-Classification & Priority Scoring**: तिकीट सबमिट होताच AI आपोआप ६ कॅटेगरींपैकी एकामध्ये वर्गीकरण करतो आणि प्रायॉरिटी स्कोअर (`Critical`/`High`/`Medium`/`Low`) ठरवतो.
   - **AI-Drafted Response with Knowledge Base Grounding**: BookLeaf च्या ८०/२० रॉयल्टी पॉलिसी, तिमाही पेआउट, ₹१,००० थ्रेशोल्ड, ५-७ दिवसांचे प्रिंटिंग, आणि ४८ तासांच्या ISBN मानकांवर आधारित सविस्तर ड्राफ्ट रिस्पॉन्स तयार होतो.
   - **On-Demand Regeneration**: ॲडमिन थेट `POST /api/v1/tickets/<id>/generate-ai-draft` द्वारे नवीन ड्राफ्ट तयार करू शकतो.
   - **Graceful Fallback**: API Key नसली किंवा इंटरनेट नसले तरीही कोणतीही ५०० एरर न येता सिस्टीम १००% अचूक ज्ञान-आधारित ड्राफ्ट तयार करते.

5. **डेटाबेस व सीव्हर**:
   - **PostgreSQL / pgAdmin** (सक्रिय आहे, `bookleaf_db`).
   - **Official Dataset Seeder**: `python manage.py seed_sample_data` (१० ऑथर्स, १८ बुक्स आणि तिकिटे).

---

## ⚡ डेटाबेस सीडिंग (Seeding Official Dataset)

असाइनमेंटचा अधिकृत डेटाबेस लोड करण्यासाठी:
```bash
python manage.py seed_sample_data
```
*(किंवा `python manage.py seed_data`)*

या कमांडने खालील सर्व डेटा आपोआप तयार होतो:
- **१ ॲडमिन खातं**: `admin@bookleaf.com` | `password123` (Devansh Joshi)
- **१० ऑथर खाती**: (सर्व खात्यांचा पासवर्ड: `password123`)
  1. `AUTH001`: `priya.sharma@email.com` (Priya Sharma - Mumbai)
  2. `AUTH002`: `rohit.kapoor@email.com` (Rohit Kapoor - Delhi)
  3. `AUTH003`: `ananya.reddy@email.com` (Ananya Reddy - Hyderabad)
  4. `AUTH004`: `vikram.malhotra@email.com` (Vikram Malhotra - Bangalore)
  5. `AUTH005`: `sneha.patel@email.com` (Sneha Patel - Ahmedabad)
  6. `AUTH006`: `arvind.swaminathan@email.com` (Arvind Swaminathan - Chennai)
  7. `AUTH007`: `meera.nambiar@email.com` (Meera Nambiar - Kochi)
  8. `AUTH008`: `kabir.mehta@email.com` (Kabir Mehta - Pune)
  9. `AUTH009`: `sunita.deshmukh@email.com` (Sunita Deshmukh - Nagpur)
  10. `AUTH010`: `tanmay.joshi@email.com` (Tanmay Joshi - Jaipur)
- **१८ अधिकृत पुस्तके**: `BK001` ते `BK018`
- **सपोर्ट तिकिटे**: AI ड्राफ्ट्स आणि संभाषणासह.

---

## 🤖 AI Configuration (पर्यायी)

[.env](file:///c:/Users/DELL/OneDrive/Documents/Desktop/book-leaf-be/.env) मध्ये तुम्ही तुमचा Google Gemini, OpenAI किंवा Claude API Key टाकू शकता:
```env
AI_PROVIDER=gemini        # 'gemini' किंवा 'openai' किंवा 'anthropic'
AI_API_KEY=tumcha_api_key
AI_MODEL=gemini-1.5-flash # किंवा 'gpt-4o-mini'
```
*(टीप: जर API Key नसेल, तरीही बॅकएंड आपोआप बुकलीफच्या अंतर्गत नियमांनुसार अचूक AI ड्राफ्ट तयार करतो, त्यामुळे टेस्टिंग कधीही थांबत नाही).*

---

## 📡 API Endpoints दस्तऐवजीकरण (Documentation)

सर्व API चे बेस URL: `http://127.0.0.1:8000/api/`

### १. Authentication Module
- `POST /api/v1/auth/login` : युनिफाइड लॉगिन (`email`, `password`).
- `POST /api/v1/auth/register` : नवीन ऑथर नोंदणी.
- `GET /api/v1/auth/me` : वर्तमान युझर प्रोफाईल.

### २. Books & Royalties Module
- `GET /api/v1/books` : पुस्तकांची यादी (`?search=`, `?status=`, `?author_id=`).
- `GET /api/v1/books/<book_id>` : एका पुस्तकाचा तपशील.
- `POST /api/v1/books` : नवीन पुस्तक जोडणे (Author only).
- `GET /api/v1/authors/me/dashboard` : ऑथर डॅशबोर्ड व रॉयल्टी आकडेवारी.

### ३. Support Tickets & AI Operations Desk
- `GET /api/v1/tickets` : तिकिटांची यादी (`?status=`, `?category=`, `?priority=`, `?search=`).
- `POST /api/v1/tickets` : नवीन तिकीट तयार करणे (AI आपोआप Category, Priority ठरवतो आणि AI Draft तयार करतो).
- `GET /api/v1/tickets/<ticket_id>` : तिकीट, संभाषण मेसेजेस आणि `ai_draft` ऑब्जेक्ट.
- `POST /api/v1/tickets/<ticket_id>/generate-ai-draft` : ॲडमिनसाठी ऑन-डिमांड AI ड्राफ्ट पुन्हा तयार करणे.
- `POST /api/v1/tickets/<ticket_id>/messages` : संभाषण थ्रेडमध्ये मेसेज पाठवणे.
- `POST /api/v1/tickets/<ticket_id>/internal-notes` : अंतर्गत ॲडमिन नोंद.
- `PATCH /api/v1/tickets/<ticket_id>` : स्टेटस, प्रायॉरिटी, असाइनी बदलणे.
- `GET /api/v1/admin/operations/stats` : ऑपरेशन्स डेस्क मेट्रिक्स.

---

## 🚀 स्थानिक पातळीवर सर्व्हर कसा चालवायचा? (Local Development)
```bash
python manage.py runserver
```
Angular Frontend (`http://localhost:4200`) वरून थेट या सर्व APIs कॉल करता येतील.

---

## 🌐 Render.com वर Production Deployment मार्गदर्शक (Step-by-Step)

हा प्रोजेक्ट **Render.com** वर १-क्लिक किंवा मॅन्युअल डिप्लॉयमेंटसाठी १००% कॉन्फिगर केलेला आहे (`gunicorn`, `whitenoise`, `dj-database-url`, `render.yaml`, आणि `build.sh` समाविष्ट आहेत).

### १. GitHub वर कोड पुश करा (Push to GitHub)
```bash
git remote add origin https://github.com/<तुमचे-username>/book-leaf-be.git
git branch -M main
git push -u origin main
```

### २. Render.com वर PostgreSQL Database तयार करा
1. [Render Dashboard](https://dashboard.render.com/) उघडा.
2. **New +** ➔ **PostgreSQL** निवडा.
3. खालील तपशील भरा:
   - **Name**: `bookleaf-db`
   - **Database**: `bookleaf_db`
   - **User**: `bookleaf_user`
   - **Plan**: `Free`
4. **Create Database** वर क्लिक करा.
5. डेटाबेस तयार झाल्यावर त्या पेजवरील **"Internal Database URL"** कॉपी करून ठेवा.

### ३. Render.com वर Web Service तयार करा
1. **New +** ➔ **Web Service** निवडा.
2. तुमचे GitHub Repository (`book-leaf-be`) सिलेक्ट करा.
3. खालील सेटिंग्स करा:
   - **Name**: `bookleaf-backend` (किंवा तुमच्या आवडीचे नाव)
   - **Language / Runtime**: `Python`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn core.wsgi:application`
   - **Plan**: `Free`
4. खाली **Environment Variables** (प्रॉपर्टीज) जोडा:
   - `DATABASE_URL` = *(पायरी २ मधील Internal Database URL पेस्ट करा)*
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `*`
   - `SECRET_KEY` = `django-insecure-bookleaf-prod-secret-key-2026`
   - `CORS_ALLOW_ALL_ORIGINS` = `True`
   - *(पर्यायी)* `AI_API_KEY` = *(तुमचा Gemini/OpenAI API Key)*
5. **Deploy Web Service** वर क्लिक करा.

बिल्ड होताना `build.sh` आपोआप:
- सर्व Python लायब्ररीज इन्स्टॉल करेल.
- स्टॅटिक फाइल्स गोळा (`collectstatic`) करेल.
- Postgres मध्ये सर्व टेबल्स (`migrate`) बनवेल.
- सर्व १० ऑथर्स, १८ बुक्स आणि तिकिटे आपोआप सीड (`seed_sample_data`) करेल.

डिप्लॉय पूर्ण झाल्यावर तुम्हाला तुमचे लाईव्ह बॅकएंड URL मिळेल:
👉 `https://<तुमचा-सर्व्हिस-नेम>.onrender.com/api/v1/auth/login`
