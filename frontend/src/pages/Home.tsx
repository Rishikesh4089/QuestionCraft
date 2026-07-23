// // src/pages/Home.tsx
// import { useEffect, useState } from "react";
// import { FileText, PlusCircle, TrendingUp, Clock, ArrowRight, Sparkles } from "lucide-react";
// import { useAuth } from "@/contexts/AuthContext";
// import { supabase } from "@/lib/supabase";
// import Button from "@/components/ui/Button";
// import { Badge } from "@/components/ui/Badge";
// import { Spinner } from "@/components/ui/Spinner";

// interface Props { onNavigate: (page: string) => void }

// interface Stats { total: number; drafts: number; finals: number; recent: any[] }

// export default function Home({ onNavigate }: Props) {
//   const { user } = useAuth();
//   const [fullName, setFullName] = useState("");
//   const [stats, setStats] = useState<Stats>({ total: 0, drafts: 0, finals: 0, recent: [] });
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     if (!user) return;
//     (async () => {
//       const [profileRes, papersRes] = await Promise.all([
//         supabase.from("profiles").select("full_name").eq("id", user.id).single(),
//         supabase.from("previous_papers").select("*").eq("user_id", user.id).order("creation_date", { ascending: false }).limit(20),
//       ]);
//       if (profileRes.data?.full_name) setFullName(profileRes.data.full_name);
//       const papers = papersRes.data ?? [];
//       setStats({
//         total: papers.length,
//         drafts: papers.filter(p => p.status === "Draft").length,
//         finals: papers.filter(p => p.status === "Final").length,
//         recent: papers.slice(0, 4),
//       });
//       setLoading(false);
//     })();
//   }, [user]);

//   const greeting = () => {
//     const h = new Date().getHours();
//     if (h < 12) return "Good morning";
//     if (h < 17) return "Good afternoon";
//     return "Good evening";
//   };

//   const displayName = fullName || user?.email?.split("@")[0] || "there";

//   if (loading) {
//     return (
//       <div className="flex-1 flex items-center justify-center">
//         <Spinner size="lg" />
//       </div>
//     );
//   }

//   return (
//     <div className="flex-1 overflow-auto bg-slate-50">
//       <div className="max-w-5xl mx-auto px-8 py-10">

//         {/* Greeting */}
//         <div className="mb-10">
//           <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
//             {greeting()}, {displayName} 👋
//           </h1>
//           <p className="text-slate-500 mt-1">Here's your QuestionCraft workspace.</p>
//         </div>

//         {/* Stat cards */}
//         <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
//           {[
//             { label: "Total Papers", value: stats.total, icon: FileText, color: "bg-slate-900 text-white" },
//             { label: "Drafts", value: stats.drafts, icon: Clock, color: "bg-amber-50 text-amber-700 border border-amber-200" },
//             { label: "Finalised", value: stats.finals, icon: TrendingUp, color: "bg-emerald-50 text-emerald-700 border border-emerald-200" },
//             { label: "Sections avg", value: stats.total ? "3-4" : "—", icon: Sparkles, color: "bg-blue-50 text-blue-700 border border-blue-200" },
//           ].map(card => (
//             <div key={card.label} className={`rounded-xl p-5 flex flex-col gap-3 ${card.color}`}>
//               <card.icon className="w-5 h-5 opacity-80" />
//               <div>
//                 <p className="text-2xl font-bold">{card.value}</p>
//                 <p className="text-xs font-medium opacity-70">{card.label}</p>
//               </div>
//             </div>
//           ))}
//         </div>

//         {/* Quick action */}
//         <div className="bg-slate-900 rounded-2xl p-8 mb-8 flex flex-col sm:flex-row items-start sm:items-center gap-6">
//           <div className="flex-1">
//             <div className="flex items-center gap-2 mb-2">
//               <Sparkles className="w-4 h-4 text-slate-400" />
//               <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Quick action</span>
//             </div>
//             <h2 className="text-xl font-bold text-white mb-1">Generate a new paper</h2>
//             <p className="text-slate-400 text-sm">Upload your syllabus and get a complete question paper in minutes.</p>
//           </div>
//           <Button
//             variant="secondary"
//             size="lg"
//             icon={<PlusCircle className="w-4 h-4" />}
//             iconRight={<ArrowRight className="w-4 h-4" />}
//             onClick={() => onNavigate("generate")}
//           >
//             Start generating
//           </Button>
//         </div>

//         {/* Recent papers */}
//         {stats.recent.length > 0 && (
//           <div>
//             <div className="flex items-center justify-between mb-4">
//               <h3 className="text-base font-bold text-slate-900">Recent Papers</h3>
//               <button
//                 onClick={() => onNavigate("history")}
//                 className="text-sm text-slate-500 hover:text-slate-800 font-medium flex items-center gap-1 transition-colors"
//               >
//                 View all <ArrowRight className="w-3.5 h-3.5" />
//               </button>
//             </div>
//             <div className="space-y-2">
//               {stats.recent.map((paper: any) => {
//                 const statusVariant: Record<string, "warning" | "success" | "default"> = {
//                   Draft: "warning", Final: "success", Archived: "default",
//                 };
//                 return (
//                   <div
//                     key={paper.id}
//                     className="flex items-center justify-between bg-white border border-slate-200 rounded-xl px-5 py-3.5 hover:border-slate-300 hover:shadow-sm transition-all cursor-pointer"
//                     onClick={() => onNavigate("history")}
//                   >
//                     <div className="flex items-center gap-3 min-w-0">
//                       <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center shrink-0">
//                         <FileText className="w-4 h-4 text-slate-500" />
//                       </div>
//                       <div className="min-w-0">
//                         <p className="text-sm font-semibold text-slate-800 truncate">{paper.paper_title}</p>
//                         <p className="text-xs text-slate-400">{paper.total_marks} marks · {new Date(paper.creation_date).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}</p>
//                       </div>
//                     </div>
//                     <Badge variant={statusVariant[paper.status] ?? "default"}>{paper.status}</Badge>
//                   </div>
//                 );
//               })}
//             </div>
//           </div>
//         )}

//         {stats.total === 0 && (
//           <div className="text-center py-16 bg-white border border-dashed border-slate-300 rounded-2xl">
//             <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
//             <p className="text-slate-600 font-medium mb-1">No papers yet</p>
//             <p className="text-slate-400 text-sm mb-6">Generate your first question paper to get started.</p>
//             <Button onClick={() => onNavigate("generate")} icon={<PlusCircle className="w-4 h-4" />}>
//               Generate first paper
//             </Button>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }