import { useNavigate } from "react-router-dom";

import Navbar from "../../components/Navbar";
import Footer from "../../components/landing/Footer";

import Hero from "../../components/landing/Hero";
import Workflow from "../../components/landing/Workflow";
import Features from "../../components/landing/Features";
import Pricing from "../../components/landing/Pricing";
import CTA from "../../components/landing/CTA";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <main
      className="
        min-h-screen
        bg-[var(--qc-bg)]
        text-[var(--qc-text)]
      "
    >
      <Navbar
        onLogin={() => navigate("/login")}
        onGetStarted={() => navigate("/signup")}
      />

      <Hero
        onGetStarted={() => navigate("/signup")}
      />

      {/* Product Preview (Coming Soon) */}

      <Workflow />

      <Features />

      <Pricing />

      <CTA
        onGetStarted={() => navigate("/signup")}
      />

      <Footer />
    </main>
  );
}