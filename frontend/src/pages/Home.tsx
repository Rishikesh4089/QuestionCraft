import { motion } from "framer-motion";
import { useAuth } from "../contexts/AuthContext";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";
import { Component as CoolBlobEffect } from "../components/ui/cool-blob-effect";
import { supabase } from "../lib/supabase"; // ✅ make sure you have this

const FloatingBalls = () => {
  return (
    <div className="relative flex justify-center items-center mt-10">
      <motion.div
        className="absolute w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 shadow-lg"
        animate={{
          y: [0, -30, 0],
          x: [0, 20, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-orange-500 shadow-lg"
        animate={{
          y: [0, 30, 0],
          x: [0, -20, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 1 }}
      />
    </div>
  );
};

export default function Home({ onNavigate }: { onNavigate: (page: string) => void }) 
{
  const { user } = useAuth();
  const [hover, setHover] = useState(false);
  const [fullName, setFullName] = useState<string | null>(null);

  // 🧠 Fetch full_name from Supabase
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        if (!user) return;
        const { data, error } = await supabase
          .from("profiles")
          .select("full_name")
          .eq("id", user.id)
          .single();

        if (error) {
          console.error("❌ Error fetching profile:", error.message);
        } else if (data?.full_name) {
          setFullName(data.full_name);
        }
      } catch (err) {
        console.error("⚠️ Unexpected error fetching profile:", err);
      }
    };

    fetchProfile();
  }, [user]);

  return (
    <div className="relative flex flex-col justify-center items-center h-screen w-full overflow-hidden bg-transparent">

      {/* 🌈 Animated Blob Background */}
      <div className="absolute inset-0 z-0 opacity-80">
        <CoolBlobEffect />
      </div>

      {/* 🎈 Floating Motion Balls */}
      <FloatingBalls />

      {/* 💎 Glassmorphic Welcome Card */}
      <motion.div
        className={cn(
          "backdrop-blur-xl bg-white/40 border border-white/30 rounded-3xl shadow-2xl px-10 py-12 text-center max-w-lg mt-20"
        )}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
      >
        <h1 className="text-4xl font-semibold text-slate-800 mb-4">
          Welcome{fullName ? `, ${fullName}` : user?.email ? `, ${user.email}` : ""}
        </h1>
        <p className="text-slate-600 mb-6 text-lg">
          Ready to generate your next mind-blowing university paper?  
          Explore, create, and innovate effortlessly with{" "}
          <span className="font-semibold text-indigo-600">
            QuestionCraft
          </span>.
        </p>

        <motion.button
  onMouseEnter={() => setHover(true)}
  onMouseLeave={() => setHover(false)}
  onClick={() => onNavigate("generate")} // 👈 navigate using useState
  className={cn(
    "px-6 py-3 rounded-full font-medium transition-all duration-300",
    hover
      ? "bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-xl scale-105"
      : "bg-indigo-100 text-indigo-700 shadow-sm"
  )}
>
  Start Generating →
</motion.button>

      </motion.div>
    </div>
  );
}
