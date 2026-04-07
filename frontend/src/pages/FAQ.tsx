import { useState } from "react";
import { ChevronDown, ChevronUp, HelpCircle } from "lucide-react";
import CoolBlobEffect from "@/components/ui/cool-blob-effect";

interface FAQItem {
  id: string;
  question: string;
  answer: string;
}

export default function FAQ() {
  const [openId, setOpenId] = useState<string | null>(null);

  const faqs: FAQItem[] = [
    {
      id: "1",
      question: "What file formats are supported for study materials?",
      answer:
        "QuestionCraft AI supports PDF, JPG, PNG, PowerPoint (PPT/PPTX), and text files (TXT). You can upload up to 15 files with a maximum size of 50MB each.",
    },
    {
      id: "2",
      question: "How does the AI generate questions from my materials?",
      answer:
        "Our advanced LLM analyzes your study materials to understand key concepts, topics, and difficulty levels. It then generates balanced questions based on your configured pattern, ensuring comprehensive coverage of the material.",
    },
    {
      id: "3",
      question: "Can I control the difficulty level of questions?",
      answer:
        "Yes! You can specify the percentage distribution of easy, medium, and hard questions. The AI will generate questions matching your specified difficulty distribution.",
    },
    {
      id: "4",
      question: "How do I set unit-wise distribution?",
      answer:
        "During configuration, you can assign each uploaded file to a specific unit and then set the percentage weightage for each unit. The AI will generate questions proportionally based on your settings.",
    },
    {
      id: "5",
      question: "Can I use a past paper as a template?",
      answer:
        "Absolutely! Upload a past paper during configuration, and our AI will extract its pattern including question types, marks distribution, and structure. You can then use this pattern to generate new papers.",
    },
    {
      id: "6",
      question: "How long does it take to generate a paper?",
      answer:
        "Most question papers are generated within 1–3 minutes, depending on the number of materials uploaded and complexity of the pattern. You will see real-time progress updates during generation.",
    },
    {
      id: "7",
      question: "Can I edit the generated paper?",
      answer:
        "Yes! After generation, you can review and edit any question, adjust marks, or regenerate specific sections before finalizing the paper.",
    },
    {
      id: "8",
      question: "In what formats can I export the papers?",
      answer:
        "Generated papers can be exported in PDF, Word (DOCX), and plain text formats. You can also print directly from the application.",
    },
    {
      id: "9",
      question: "Is my data secure?",
      answer:
        "Yes, we take security seriously. All uploaded materials and generated papers are encrypted and stored securely. We never share your content with third parties, and you maintain full ownership of your data.",
    },
    {
      id: "10",
      question: "Can I save paper templates for reuse?",
      answer:
        "Yes! You can save any configuration as a template and reuse it across multiple paper generations. This is particularly useful for recurring assessments.",
    },
    {
      id: "11",
      question: "How many papers can I generate?",
      answer:
        "There is no limit to the number of papers you can generate. All your papers are saved in your history for future reference.",
    },
    {
      id: "12",
      question: "What if I need help or support?",
      answer:
        "We offer comprehensive support through email and in-app chat. For urgent issues, you can reach out to our support team at support@questioncraft.com.",
    },
  ];

  const toggleFAQ = (id: string) => {
    setOpenId(openId === id ? null : id);
  };

  return (
    <div className="relative flex-1 overflow-auto bg-slate-50 min-h-screen">
      {/* 🌈 Cool Blob Background */}
      <div className="absolute inset-0 z-2 opacity-60 pointer-events-none">
        <CoolBlobEffect />
      </div>

      {/* 📘 FAQ Content */}
      <div className="relative z-10 max-w-4xl mx-auto p-8">
        <div className="mb-8 text-center">
          <HelpCircle className="w-16 h-16 text-slate-800 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Frequently Asked Questions
          </h1>
          <p className="text-slate-600">
            Find answers to common questions about QuestionCraft
          </p>
        </div>

        <div className="bg-white/90 rounded-xl shadow-lg backdrop-blur-sm">
          <div className="divide-y divide-slate-200">
            {faqs.map((faq) => (
              <div key={faq.id} className="p-6 transition-all">
                <button
                  onClick={() => toggleFAQ(faq.id)}
                  className="w-full flex items-start justify-between text-left"
                >
                  <span className="font-medium text-slate-900 pr-8">
                    {faq.question}
                  </span>
                  {openId === faq.id ? (
                    <ChevronUp className="w-5 h-5 text-slate-600 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-slate-600 flex-shrink-0" />
                  )}
                </button>
                {openId === faq.id && (
                  <p className="mt-3 text-slate-600 leading-relaxed">
                    {faq.answer}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 💬 Support Section */}
        <div className="mt-8 bg-slate-800/90 backdrop-blur-sm rounded-xl p-8 text-center text-white shadow-md">
          <h2 className="text-2xl font-bold mb-3">Still have questions?</h2>
          <p className="text-slate-300 mb-6">
            Our support team is here to help you get the most out of
            QuestionCraft.
          </p>

          {/* 📧 Email link */}
          <a
            href={`mailto:rishikesh.prabhu.4089@gmail.com?subject=${encodeURIComponent(
              "QuestionCraft Support Request"
            )}&body=${encodeURIComponent(
              "Hi Rishikesh,\n\nI need help with QuestionCraft. Please assist.\n\nDetails:\n- Account email:\n- Issue:\n\nThanks."
            )}`}
            className="inline-block px-6 py-3 bg-white text-slate-800 rounded-lg hover:bg-slate-100 transition-colors font-medium"
            role="button"
            aria-label="Contact support via email"
          >
            Contact Support
          </a>
        </div>
      </div>
    </div>
  );
}
