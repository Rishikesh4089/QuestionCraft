import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { supabase } from "@/lib/supabase";

import AuthLayout from "@/components/auth/AuthLayout";
import AuthIllustration from "@/components/auth/AuthIllustration";
import AuthCard from "@/components/auth/AuthCard";
import SignupForm from "@/components/auth/SignupForm";
import { useAuth } from "@/contexts/AuthContext";

export default function SignupPage() {

  const navigate = useNavigate();

  const { signInWithGoogle } = useAuth();

  const [fullName, setFullName] = useState("");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  async function handleSubmit(
    e: React.FormEvent
  ) {
    e.preventDefault();

    setError("");

    setLoading(true);

    try {

      if (password !== confirmPassword) {

        throw new Error(
          "Passwords do not match."
        );

      }

      const { error: authError } =
        await supabase.auth.signUp({

          email,

          password,

          options: {

            data: {

              full_name: fullName,

            },

          },

        });

      if (authError) throw authError;

      navigate("/login");

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
        title="Create Account"
        subtitle="Generate professional examination papers with AI."
      >
        <SignupForm
          fullName={fullName}
          email={email}
          password={password}
          confirmPassword={confirmPassword}
          loading={loading}
          error={error}
          onFullNameChange={setFullName}
          onEmailChange={setEmail}
          onPasswordChange={setPassword}
          onConfirmPasswordChange={setConfirmPassword}
          onSubmit={handleSubmit}
          onGoogleSignIn={signInWithGoogle}
          onSwitchToLogin={() => navigate("/login")}
        />
      </AuthCard>
    </AuthLayout>
  );
}