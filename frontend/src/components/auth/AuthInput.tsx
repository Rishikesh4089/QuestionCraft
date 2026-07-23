interface AuthInputProps {
  label: string;
  type: string;
  placeholder: string;
  value: string;
  onChange: (e: any) => void;
}

export default function AuthInput({
  label,
  type,
  placeholder,
  value,
  onChange,
}: AuthInputProps) {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="
            w-full
            rounded-xl
            border
            border-[var(--qc-border)]
            bg-white
            px-4
            py-3

            text-[var(--qc-text)]

            placeholder:text-[var(--qc-text-muted)]

            transition-all

            focus:border-[var(--qc-primary)]
            focus:ring-2
            focus:ring-[var(--qc-primary-light)]
            focus:outline-none
            "
      />
    </div>
  );
}