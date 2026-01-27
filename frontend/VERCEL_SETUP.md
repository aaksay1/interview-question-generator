# Vercel Deployment Setup

## Environment Variables

To connect your Vercel frontend to your Render backend, you need to set the environment variable in Vercel:

### Steps:

1. Go to your Vercel project dashboard: https://vercel.com/dashboard
2. Select your project: `interview-question-generator-mocha`
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Add the following:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://interview-question-generator-lqa9.onrender.com`
   - **Environment**: Select all (Production, Preview, Development) or just Production
6. Click **Save**
7. **Redeploy** your application (or it will auto-deploy if connected to Git)

### Note:

Even if you don't set the environment variable, the app will default to the production backend URL. However, it's best practice to set it explicitly.

### Verify:

After deployment, check the browser console (F12) to see what API URL is being used. You should see logs if there are connection issues.
