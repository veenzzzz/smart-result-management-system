# 🎓 ResultHub Frontend

A modern, responsive frontend for the ResultHub Smart Result Management System built with React, TypeScript, and Tailwind CSS.

## ✨ Features

### 🎨 Modern UI/UX
- **Clean Design**: Professional, intuitive interface
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Automatic theme switching
- **Smooth Animations**: Delightful user interactions

### 🔐 Authentication
- **Role-based Login**: Admin, Staff, and Student roles
- **Secure Sessions**: Protected routes and API calls
- **Password Management**: Change password functionality

### 📊 Dashboard
- **Admin Dashboard**: Overview of system statistics
- **Student Dashboard**: Personal academic performance
- **Real-time Updates**: Live data from backend

### 👥 Student Management
- **Add Students**: Register new students with roll numbers
- **View Students**: Browse all student records
- **Edit Information**: Update student details
- **Delete Students**: Remove student records

### 📝 Result Management
- **Enter Marks**: Add student marks for subjects
- **Grade Calculation**: Automatic grade assignment
- **Publish Results**: Make results visible to students
- **Bulk Operations**: Manage multiple results

### 📈 Reports & Analytics
- **Student Reports**: Individual performance analysis
- **Class Reports**: Class-wise statistics
- **Merit Lists**: Top performers
- **Charts & Graphs**: Visual data representation

## 🛠️ Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI Framework |
| TypeScript | 5.0.2 | Type Safety |
| Vite | 4.4.5 | Build Tool |
| Tailwind CSS | 3.3.3 | Styling |
| React Router | 6.8.1 | Routing |
| Lucide React | 0.263.1 | Icons |
| Recharts | 2.5.0 | Charts |

## 📦 Installation

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend API running on port 5000

### Setup

1. **Install Dependencies**
```bash
npm install
```

2. **Start Development Server**
```bash
npm run dev
```

3. **Build for Production**
```bash
npm run build
```

## 🚀 Getting Started

### Development Server
The frontend runs on `http://localhost:3000` and automatically connects to the backend API at `http://localhost:5000`.

### Default Login Credentials
- **Admin**: `admin` / `admin123`
- **Student**: Use roll number and password provided by admin

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ui/           # Basic UI components
│   │   └── layout/       # Layout components
│   ├── contexts/         # React contexts
│   ├── pages/           # Page components
│   │   ├── admin/       # Admin pages
│   │   └── student/     # Student pages
│   ├── types/           # TypeScript types
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── index.html           # HTML template
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
└── vite.config.ts       # Vite config
```

## 🎨 Design System

### Colors
- **Primary**: Blue (#3B82F6)
- **Success**: Green (#10B981)
- **Warning**: Amber (#F59E0B)
- **Danger**: Red (#EF4444)

### Typography
- **Font Family**: Inter
- **Headings**: Bold, large sizes
- **Body**: Regular weight, readable sizes

## 🔐 Authentication

### Default Admin Credentials
- **Username**: admin
- **Password**: admin123

### Student Login
Students use their roll number and password provided by admin.

## 🌐 API Integration

The frontend expects a backend API at `/api` with the following endpoints:

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout

### Students
- `GET /api/students` - List students
- `POST /api/students` - Add student
- `PUT /api/students/:id` - Update student
- `DELETE /api/students/:id` - Delete student

### Results
- `GET /api/results/student/:id` - Get student results
- `POST /api/results` - Enter marks
- `PUT /api/results/publish` - Publish results

## 🚀 Build for Production

```bash
npm run build
```

The production build will be in the `dist` folder.

## 📱 Responsive Design

The application is fully responsive and works on:
- 📱 Mobile devices (320px+)
- 📱 Tablets (768px+)
- 💻 Desktops (1024px+)

## ✨ Key Features

- ✅ Modern, clean UI design
- ✅ Smooth animations and transitions
- ✅ Real-time grade calculation
- ✅ Role-based access control
- ✅ Responsive layout
- ✅ Toast notifications
- ✅ Loading states
- ✅ Error handling

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and focused

## 📞 Support

For issues or questions, please refer to the documentation or contact your system administrator.

---

**Made with ❤️ for educational institutions**