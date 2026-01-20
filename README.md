# J.A.I Platform - Jurist Artificial Intelligence

A comprehensive AI-powered legal platform connecting clients with qualified lawyers through intelligent matching and case management.

## 🚀 Features

### For Clients
- **Smart Lawyer Matching**: AI-powered recommendations based on case requirements
- **Case Management**: Post cases, track progress, and communicate with lawyers
- **Request System**: Send requests to lawyers with detailed case information
- **Dashboard**: Comprehensive overview of cases, requests, and connected lawyers

### For Lawyers
- **Profile Management**: Complete professional profiles with specializations
- **Request Handling**: Accept/reject client requests with response messages
- **Case Tracking**: Manage assigned cases and client communications
- **Availability Control**: Toggle availability for new case matches

### Technical Features
- **FastAPI Backend**: High-performance Python API with async support
- **MongoDB Integration**: Scalable document database for user and case data
- **JWT Authentication**: Secure token-based authentication system
- **Responsive Frontend**: Mobile-friendly HTML/CSS/JavaScript interface
- **AI Matching**: Intelligent lawyer-case matching algorithms

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Deployment**: Railway, Docker-ready

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- MongoDB (local or cloud)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/jai-platform.git
   cd jai-platform
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your MongoDB connection details
   ```

4. **Start MongoDB**
   ```bash
   # Windows
   mongod
   
   # Linux/Mac
   sudo systemctl start mongod
   ```

5. **Run the application**
   ```bash
   # Quick start (creates test users)
   python quick_start.py
   
   # Or start manually
   cd backend
   python main.py
   ```

6. **Access the application**
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs
   - Frontend: Open `pages/index.html` in your browser

## 🚀 Deployment

### Railway Deployment

1. **Connect to Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

2. **Environment Variables**
   Set these in your Railway dashboard:
   ```
   MONGODB_URL=your_mongodb_connection_string
   DATABASE_NAME=jai_database
   SECRET_KEY=your_secret_key
   PORT=8000
   ```

### Manual Deployment

The project includes deployment configuration files:
- `start.sh` - Deployment startup script
- `railway.toml` - Railway configuration
- `Procfile` - Process management
- `requirements.txt` - Python dependencies

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Users & Lawyers
- `GET /api/lawyers` - List all lawyers
- `POST /api/lawyers/profile` - Create lawyer profile
- `PUT /api/lawyers/profile` - Update lawyer profile

### Cases & Requests
- `GET /api/cases/` - Get user cases
- `POST /api/cases/` - Create new case
- `POST /api/requests/` - Send lawyer request
- `POST /api/requests/{id}/respond` - Respond to request

## 🧪 Test Credentials

The system includes pre-configured test accounts:

### Client Accounts
- **Email**: client@test.com | **Password**: password123
- **Email**: demo.client@jai.com | **Password**: demo123

### Lawyer Accounts
- **Email**: lawyer@test.com | **Password**: password123
- **Email**: demo.lawyer@jai.com | **Password**: demo123

## 📁 Project Structure

```
jai-platform/
├── backend/                 # FastAPI backend
│   ├── models/             # Database models
│   ├── routers/            # API route handlers
│   ├── main.py             # Application entry point
│   └── database.py         # Database configuration
├── pages/                  # Frontend HTML pages
│   ├── client-dashboard.html
│   ├── lawyer-dashboard.html
│   └── ...
├── start.sh               # Deployment script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the test credentials in `TEST_CREDENTIALS.md`

## 🔮 Future Enhancements

- Real-time chat between clients and lawyers
- Payment integration for legal services
- Document upload and management
- Advanced AI matching algorithms
- Mobile application (React Native)
- Video consultation integration