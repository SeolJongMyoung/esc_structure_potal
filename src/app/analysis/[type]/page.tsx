import Link from "next/link";
import { use } from "react";

export default function AnalysisPlaceholderPage({ params }: { params: Promise<{ type: string }> }) {
    const { type } = use(params);

    const titles: Record<string, string> = {
        beam: "보 해석 (Beam Analysis)",
        column: "기둥 해석 (Column Analysis)",
        slab: "슬래브 해석 (Slab Analysis)",
        foundation: "기초 해석 (Foundation Analysis)",
    };

    const title = titles[type] || "구조 해석";

    return (
        <main className="min-h-screen p-8 flex flex-col items-center justify-center relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
                <div className="absolute top-[-10%] left-[50%] w-[40%] h-[40%] bg-amber-500/10 rounded-full blur-[120px] transform -translate-x-1/2" />
            </div>

            <div className="glass-panel p-12 rounded-2xl max-w-2xl w-full text-center space-y-8 border border-white/5 animate-fade-in">
                <div className="w-20 h-20 mx-auto rounded-full bg-slate-800/50 flex items-center justify-center text-amber-400 mb-6">
                    <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                </div>

                <h1 className="text-3xl font-bold text-white">{title}</h1>
                <p className="text-slate-400 text-lg">
                    현재 이 기능은 준비 중입니다.
                    <br />
                    곧 서비스가 제공될 예정입니다.
                </p>

                <div className="pt-8">
                    <Link href="/dashboard" className="btn-secondary">
                        대시보드로 돌아가기
                    </Link>
                </div>
            </div>
        </main>
    );
}
