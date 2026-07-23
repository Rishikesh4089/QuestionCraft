import { ReactNode } from "react";

import Button from "@/components/ui/Button";

import AuthInput from "./AuthInput";
import Divider from "./Divider";
import SocialButton from "./SocialButton";

interface SignupFormProps {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;

  loading?: boolean;
  error?: string;

  onFullNameChange: (value: string) => void;
  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onConfirmPasswordChange: (value: string) => void;

  onSubmit: (e: React.FormEvent) => void;

  onGoogleSignIn?: () => void;

  onSwitchToLogin: () => void;

  googleIcon?: ReactNode;
}

export default function SignupForm({
  fullName,
  email,
  password,
  confirmPassword,

  loading = false,
  error,

  onFullNameChange,
  onEmailChange,
  onPasswordChange,
  onConfirmPasswordChange,

  onSubmit,

  onGoogleSignIn,

  onSwitchToLogin,

  googleIcon,
}: SignupFormProps) {
  return (
    <form
      onSubmit={onSubmit}
      className="space-y-5"
    >
      {/* Google */}

      <SocialButton
        onClick={onGoogleSignIn}
        icon={
          googleIcon ?? (
            <img
              src="/google.svg"
              alt="Google"
              className="w-5 h-5"
            />
          )
        }
      >
        Continue with Google
      </SocialButton>

      <Divider text="or continue with email" />

      {/* Inputs */}

      <AuthInput
        label="Full Name"
        type="text"
        placeholder="John Smith"
        value={fullName}
        onChange={(e) => onFullNameChange(e.target.value)}
      />

      <AuthInput
        label="Email"
        type="email"
        placeholder="john@email.com"
        value={email}
        onChange={(e) => onEmailChange(e.target.value)}
      />

      <AuthInput
        label="Password"
        type="password"
        placeholder="Minimum 6 characters"
        value={password}
        onChange={(e) => onPasswordChange(e.target.value)}
      />

      <AuthInput
        label="Confirm Password"
        type="password"
        placeholder="Re-enter your password"
        value={confirmPassword}
        onChange={(e) => onConfirmPasswordChange(e.target.value)}
      />

      {/* Error */}

      {error && (
        <div
          className="
            rounded-xl
            border
            border-red-200
            bg-red-50
            px-4
            py-3
            text-sm
            text-red-600
          "
        >
          {error}
        </div>
      )}

      {/* Button */}

      <Button
        type="submit"
        loading={loading}
        className="
          w-full
          h-14
          rounded-full
        "
      >
        Create Account
      </Button>

      {/* Footer */}

      <p
        className="
          pt-2
          text-center
          text-sm
          text-[var(--qc-text-secondary)]
        "
      >
        Already have an account?{" "}

        <button
          type="button"
          onClick={onSwitchToLogin}
          className="
            font-semibold
            text-[var(--qc-primary)]
            hover:underline
          "
        >
          Sign In
        </button>
      </p>
    </form>
  );
}