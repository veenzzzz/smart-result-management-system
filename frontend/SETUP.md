# 🚀 Frontend Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**

## Installation Steps

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

Using npm:
```bash
npm install
```

Or using yarn:
```bash
yarn install
```

This will install all required packages:
- React 19
- TypeScript
- Vite
- Tailwind CSS v4
- React Router v7
- Lucide React (icons)
- And other dependencies

### Step 3: Start Development Server

```bash
npm run dev
```

Or with yarn:
```bash
yarn dev
```

The application will start at `http://localhost:3000`

## 🔧 Configuration

### Backend API

The frontend is configured to proxy API requests to `http://localhost:5000`. If your backend runs on a different port, update `vite.config.ts`:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:YOUR_BACKEND_PORT',
      changeOrigin: true,
    }
  }
}
```

### Environment Variables

Create a `.env` file in the frontend directory if needed:

```env
VITE_API_URL=http://localhost:5000
```

## 🎯 First Run

1. **Start the backend server** (Python Flask/FastAPI)
2. **Start the frontend** with `npm run dev`
3. **Open browser** at `http://localhost:3000`
4. **Login** with default admin credentials:
   - Username: `admin`
   - Password: `admin123`

## 📦 Build for Production

To create a production build:

```bash
npm run build
```

The optimized files will be in the `dist` folder.

To preview the production build:

```bash
npm run preview
```

## 🐛 Troubleshooting

### Port Already in Use

If port 3000 is already in use, you can:

1. Change the port in `vite.config.ts`:
```typescript
server: {
  port: 3001, // Change to any available port
}
```

2. Or kill the process using port 3000

### Module Not Found Errors

If you see module not found errors:

```bash
# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install
```

### TypeScript Errors

If you encounter TypeScript errors:

```bash
# Clear TypeScript cache
rm -rf node_modules/.cache

# Restart the dev server
npm run dev
```

## 📱 Testing on Mobile

To test on mobile devices on the same network:

1. Find your computer's IP address
2. Start the dev server
3. Access from mobile: `http://YOUR_IP:3000`

## 🌐 Deployment

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

### Deploy to Netlify

1. Build the project:
```bash
npm run build
```

2. Deploy the `dist` folder to Netlify

## ✅ Verification

After setup, verify everything works:

- [ ] Frontend loads at `http://localhost:3000`
- [ ] Login page displays correctly
- [ ] Can login with admin credentials
- [ ] Dashboard loads after login
- [ ] No console errors
- [ ] API calls work (if backend is running)

## 📚 Next Steps

1. **Set up the backend** (Python Flask/FastAPI)
2. **Create API endpoints** to match frontend expectations
3. **Test all features** end-to-end
4. **Customize** the design as needed

## 🆘 Need Help?

If you encounter issues:

1. Check the browser console for errors
2. Check the terminal for build errors
3. Ensure all dependencies are installed
4. Verify Node.js version is 18+
5. Check that backend is running (if testing API calls)

---

**Happy Coding! 🎉**