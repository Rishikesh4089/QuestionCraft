import { ReactNode } from "react";

import Button from "@/components/ui/Button";

import AuthInput from "./AuthInput";
import Divider from "./Divider";
import SocialButton from "./SocialButton";

interface LoginFormProps {
  email: string;
  password: string;

  loading?: boolean;
  error?: string;

  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;

  onSubmit: (e: React.FormEvent) => void;

  onGoogleSignIn?: () => void;

  onSwitchToSignup: () => void;

  googleIcon?: ReactNode;
}

export default function LoginForm({
  email,
  password,

  loading = false,
  error,

  onEmailChange,
  onPasswordChange,

  onSubmit,

  onGoogleSignIn,

  onSwitchToSignup,

  googleIcon,
}: LoginFormProps) {
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

      {/* Email */}

      <AuthInput
        label="Email"
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) => onEmailChange(e.target.value)}
      />

      {/* Password */}

      <AuthInput
        label="Password"
        type="password"
        placeholder="Enter your password"
        value={password}
        onChange={(e) => onPasswordChange(e.target.value)}
      />

      {/* Remember + Forgot */}

      <div className="flex items-center justify-between text-sm">

        <label
          className="
            flex
            items-center
            gap-2
            cursor-pointer
            text-[var(--qc-text-secondary)]
        "
        >
          <input
            type="checkbox"
            className="
              h-4
              w-4
              rounded
              accent-[var(--qc-primary)]
            "
          />

          Remember me
        </label>

        <button
          type="button"
          className="
            text-[var(--qc-primary)]
            font-medium
            hover:underline
          "
        >
          Forgot password?
        </button>

      </div>

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

      {/* Login */}

      <Button
        type="submit"
        loading={loading}
        className="
          w-full
          h-14
          rounded-full
        "
      >
        Log In
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
        Don't have an account?{" "}

        <button
          type="button"
          onClick={onSwitchToSignup}
          className="
            font-semibold
            text-[var(--qc-primary)]
            hover:underline
          "
        >
          Sign Up
        </button>
      </p>
    </form>
  );
}