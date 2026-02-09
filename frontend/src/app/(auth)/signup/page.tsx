import { SignupForm } from '@/components/forms/signup-form'

export default function SignupPage() {
  return (
    <div>
      <div className="mb-8 text-center animate-fade-in-up">
        <h1 className="text-3xl font-bold gradient-text mb-2">Create Account</h1>
        <p className="text-muted-foreground">
          Sign up to get started with TaskFlow
        </p>
      </div>
      <SignupForm />
    </div>
  )
}