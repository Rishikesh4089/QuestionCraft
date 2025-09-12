import React from "react";

interface Props {
  size?: "small" | "large";
}

const Spinner: React.FC<Props> = ({ size = "small" }) => (
  <svg
    className={`animate-spin ${size === "large" ? "h-10 w-10" : "h-5 w-5"} text-blue-600`}
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
  >
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z"
    />
  </svg>
);

export default Spinner;
