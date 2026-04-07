import { FileText, Sparkles, Settings, Clock, Shield, Zap } from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
}

export default function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <nav className="px-6 py-4 bg-white/80 backdrop-blur-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <img
        src="/logo.png"
        alt="QuestionCraft Logo"
        className="w-17 h-17 object-contain"
      />
            <span className="text-2xl font-bold text-slate-800">QuestionCraft</span>
          </div>
          <button
            onClick={onGetStarted}
            className="px-6 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors font-medium"
          >
            Get Started
          </button>
        </div>
      </nav>

      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6 leading-tight">
            Generate Custom Question Papers
            <br />
            <span className="text-slate-600">In Minutes, Not Hours</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto mb-8">
            Leverage AI to create comprehensive, balanced question papers from your study materials.
            Perfect for educators, institutions, and trainers.
          </p>
          <button
            onClick={onGetStarted}
            className="px-8 py-4 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-all font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            Start Creating Papers
          </button>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-20">
          <FeatureCard
            icon={<Sparkles className="w-6 h-6" />}
            title="AI-Powered Generation"
            description="Advanced algorithms analyze your materials to create balanced, comprehensive question papers"
          />
          <FeatureCard
            icon={<Settings className="w-6 h-6" />}
            title="Fully Customizable"
            description="Control difficulty levels, unit distribution, question types, and marks allocation"
          />
          <FeatureCard
            icon={<Clock className="w-6 h-6" />}
            title="Save Time"
            description="Generate papers in minutes that would traditionally take hours to create manually"
          />
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-12 mb-20">
          <h2 className="text-3xl font-bold text-slate-900 mb-8 text-center">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <Step
              number="1"
              title="Upload Materials"
              description="Add your study materials: PDFs, images, presentations, or text files"
            />
            <Step
              number="2"
              title="Configure Pattern"
              description="Set paper structure, marks distribution, and difficulty levels"
            />
            <Step
              number="3"
              title="Set Distribution"
              description="Define unit-wise weightage and question type percentages"
            />
            <Step
              number="4"
              title="Generate & Export"
              description="Get your custom question paper ready for distribution"
            />
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-20">
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-slate-900 mb-4">For Educators</h3>
            <ul className="space-y-3 text-slate-600">
              <li className="flex items-start">
                <span className="text-slate-800 mr-2">•</span>
                Create diverse question papers for different batches
              </li>
              <li className="flex items-start">
                <span className="text-slate-800 mr-2">•</span>
                Maintain consistency across multiple assessments
              </li>
              <li className="flex items-start">
                <span className="text-slate-800 mr-2">•</span>
                Save templates for reuse across semesters
              </li>
              <li className="flex items-start">
                <span className="text-slate-800 mr-2">•</span>
                Generate papers matching past paper patterns
              </li>
            </ul>
          </div>

          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-slate-900 mb-4">For Institutions</h3>
            <ul className="space-y-3 text-slate-600">
              <li className="flex items-start">
                <span className="text-slate-800 mr-2">•</span>
                Standardize assessment quality across departments
              </li>
              <li className="flex items-start">
                <span className="text-slate-800 mr-2">•</span>
                Reduce paper setting time by up to 80%
              </li>
              <li className="flex items-start">
                <span className="text-slate-800 mr-2">•</span>
                Ensure balanced coverage of curriculum
              </li>
              <li className="flex items-start">
                <span className="text-slate-800 mr-2">•</span>
                Maintain question paper repository
              </li>
            </ul>
          </div>
        </div>

        <div className="bg-slate-800 rounded-2xl p-12 text-center text-white">
          <Shield className="w-16 h-16 mx-auto mb-6 text-slate-300" />
          <h2 className="text-3xl font-bold mb-4">Secure & Private</h2>
          <p className="text-slate-300 max-w-2xl mx-auto mb-8">
            Your study materials and generated papers are encrypted and stored securely.
            We never share your content with third parties.
          </p>
          <div className="flex items-center justify-center space-x-8 text-sm text-slate-400">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4" />
              <span>End-to-End Encryption</span>
            </div>
            <div className="flex items-center space-x-2">
              <Zap className="w-4 h-4" />
              <span>GDPR Compliant</span>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 py-8 bg-white">
        <div className="max-w-7xl mx-auto px-6 text-center text-slate-600">
          <p>© 2025 QuestionCraft AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center mb-4 text-slate-800">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  );
}

function Step({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-slate-800 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
        {number}
      </div>
      <h4 className="text-lg font-semibold text-slate-900 mb-2">{title}</h4>
      <p className="text-slate-600 text-sm">{description}</p>
    </div>
  );
}
