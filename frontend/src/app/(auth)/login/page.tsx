import { LoginForm } from '@/components/forms/login-form'

export default function LoginPage() {
  return (
    <div>
      <div className="mb-8 text-center animate-fade-in-up">
        <h1 className="text-3xl font-bold gradient-text mb-2">Welcome Back</h1>
        <p className="text-muted-foreground">
          Sign in to your account to continue
        </p>
      </div>
      <LoginForm />
    </div>
  )
}