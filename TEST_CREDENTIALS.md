# 🔑 J.A.I Test Login Credentials

Use these credentials to test the client and lawyer dashboards.

## 👤 Client Accounts

### Primary Test Client
- **Email:** `client@test.com`
- **Password:** `password123`
- **Dashboard:** Client Dashboard

### Demo Client
- **Email:** `demo.client@jai.com`
- **Password:** `demo123`
- **Dashboard:** Client Dashboard

## ⚖️ Lawyer Accounts

### Primary Test Lawyer
- **Email:** `lawyer@test.com`
- **Password:** `password123`
- **Dashboard:** Lawyer Dashboard

### Demo Lawyer
- **Email:** `demo.lawyer@jai.com`
- **Password:** `demo123`
- **Dashboard:** Lawyer Dashboard

## 🚀 Quick Start

### 1. Setup Test Users
```bash
cd backend
python create_test_users.py
```

### 2. Start Backend Server
```bash
cd backend
python start_server.py
```

### 3. Access Frontend
- **Client Login:** Open `pages/client-login.html`
- **Lawyer Login:** Open `pages/lawyer-login.html`

### 4. Login Flow
1. Use any of the credentials above
2. You'll be automatically redirected to the appropriate dashboard
3. Explore the features!

## 🌐 URLs

- **Frontend:** `http://localhost:5500` (if using live server)
- **Backend API:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/docs`

## 📋 Features to Test

### Client Dashboard
- ✅ View case statistics
- ✅ Post new cases
- ✅ Find lawyers
- ✅ View recommendations

### Lawyer Dashboard
- ✅ Complete lawyer profile
- ✅ Toggle availability
- ✅ View assigned cases
- ✅ Manage specializations

## 🔧 Troubleshooting

### If login fails:
1. Make sure MongoDB is running
2. Check that the backend server is running on port 8000
3. Run the test user creation script again
4. Check browser console for errors

### If dashboards don't load:
1. Check that you're using the correct user type login page
2. Verify the API calls in browser developer tools
3. Make sure CORS is properly configured

## 🎯 Test Scenarios

### Client Flow
1. Login as client → Client Dashboard
2. Post a new case
3. Search for lawyers
4. View case statistics

### Lawyer Flow
1. Login as lawyer → Lawyer Dashboard
2. Complete profile (if not done)
3. Toggle availability
4. View case matches
5. Update specializations

## 📊 Sample Data

The test setup includes:
- **4 test users** (2 clients, 2 lawyers)
- **Complete lawyer profiles** with specializations
- **3 sample cases** for testing
- **Realistic data** for demonstrations