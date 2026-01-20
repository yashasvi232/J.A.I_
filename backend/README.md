# J.A.I Backend API

Jurist Artificial Intelligence - AI-powered legal platform backend built with FastAPI and MongoDB.

## 🚀 Features

- **FastAPI Framework**: High-performance, automatic API documentation
- **MongoDB Database**: Flexible document storage for legal data
- **JWT Authentication**: Secure user authentication and authorization
- **AI Integration**: Machine learning for lawyer-client matching
- **Real-time Features**: WebSocket support for chat and notifications
- **File Upload**: Secure document handling
- **Email Services**: Automated notifications and communications

## 📋 Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Redis (optional, for caching)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start MongoDB**
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
```

## 🚀 Running the Application

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh-token` - Refresh access token

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/upload-avatar` - Upload profile image

### Lawyers
- `GET /api/lawyers` - Search lawyers
- `GET /api/lawyers/{id}` - Get lawyer details
- `POST /api/lawyers/profile` - Create lawyer profile
- `PUT /api/lawyers/profile` - Update lawyer profile

### Cases
- `POST /api/cases` - Create new case
- `GET /api/cases` - Get user's cases
- `GET /api/cases/{id}` - Get case details
- `PUT /api/cases/{id}` - Update case

### AI Services
- `POST /api/ai/match-lawyers` - Get AI lawyer matches
- `POST /api/ai/analyze-case` - Analyze case with AI
- `POST /api/ai/estimate-cost` - Estimate legal costs

## 🗄️ Database Schema

### Collections

#### Users
```javascript
{
  "_id": ObjectId,
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "user_type": "client|lawyer|admin",
  "profile_image_url": "url",
  "is_verified": false,
  "is_active": true,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### Lawyers
```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "bar_number": "12345",
  "bar_state": "CA",
  "law_firm": "Law Firm Name",
  "years_experience": 10,
  "hourly_rate": 350.00,
  "bio": "Lawyer biography",
  "specializations": ["Family Law", "Corporate Law"],
  "education": [
    {
      "school": "Harvard Law School",
      "degree": "J.D.",
      "year": 2010
    }
  ],
  "certifications": [],
  "languages": ["English", "Spanish"],
  "availability_status": "available",
  "rating": 4.8,
  "total_reviews": 25,
  "total_cases": 100,
  "success_rate": 95.5,
  "ai_match_score": 88.2,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### Cases
```javascript
{
  "_id": ObjectId,
  "case_number": "CASE-2024-001",
  "client_id": ObjectId,
  "lawyer_id": ObjectId,
  "title": "Case Title",
  "description": "Case description",
  "category": "Family Law",
  "urgency_level": "medium",
  "budget_min": 1000.00,
  "budget_max": 5000.00,
  "status": "open",
  "ai_analysis": {
    "complexity": "medium",
    "estimated_duration": "3-6 months",
    "success_probability": 0.85
  },
  "matching_criteria": {},
  "created_at": ISODate,
  "updated_at": ISODate,
  "closed_at": null
}
```

## 🤖 AI Integration

The platform includes AI-powered features:

1. **Lawyer Matching**: Intelligent matching based on case requirements
2. **Case Analysis**: Automated case complexity and outcome prediction
3. **Document Processing**: AI-powered document analysis and categorization
4. **Cost Estimation**: ML-based legal cost predictions

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS protection
- Rate limiting
- File upload security

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_auth.py
```

## 📦 Deployment

### Using Docker
```bash
# Build image
docker build -t jai-backend .

# Run container
docker run -d -p 8000:8000 --name jai-api jai-backend
```

### Using Docker Compose
```bash
docker-compose up -d
```

## 🔧 Configuration

Key environment variables:

- `MONGODB_URL`: MongoDB connection string
- `SECRET_KEY`: JWT secret key
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `SMTP_*`: Email configuration
- `REDIS_URL`: Redis connection for caching

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.