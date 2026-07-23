import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

import AuthLayout from "@/components/auth/AuthLayout";
import AuthIllustration from "@/components/auth/AuthIllustration";
import AuthCard from "@/components/auth/AuthCard";
import LoginForm from "@/components/auth/LoginForm";

export default function LoginPage() {
  const navigate = useNavigate();

  const { signIn, signInWithGoogle} = useAuth();

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  async function handleSubmit(
    e: React.FormEvent
  ) {
    e.preventDefault();

    setLoading(true);

    setError("");

    try {

      await signIn(email, password);

      navigate("/dashboard");

    } catch (err) {

      if (err instanceof Error) {
        setError(err.message);
      }

    } finally {

      setLoading(false);

    }
  }

  return (
    <AuthLayout
      illustration={<AuthIllustration />}
    >
      <AuthCard
        title="Welcome Back"
        subtitle="Sign in to continue creating professional assessments."
      >
        <LoginForm
          email={email}
          password={password}
          loading={loading}
          error={error}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onSubmit={handleSubmit}
          onGoogleSignIn={signInWithGoogle}
          onSwitchToSignup={() => navigate("/signup")}
        />
      </AuthCard>
    </AuthLayout>
  );
}