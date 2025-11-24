import AnalysisCard from "@/components/AnalysisCard";

export default function DashboardPage() {
    const tools = [
        {
            title: "보 해석 (Beam Analysis)",
            description: "단순보, 연속보 등 다양한 보 구조물의 휨 모멘트 및 전단력을 계산합니다.",
            href: "/analysis/beam",
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                </svg>
            ),
        },
        {
            title: "기둥 해석 (Column Analysis)",
            description: "축하중과 모멘트를 받는 기둥의 안정성 및 단면 설계를 수행합니다.",
            href: "/analysis/column",
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
                </svg>
            ),
        },
        {
            title: "슬래브 해석 (Slab Analysis)",
            description: "1방향 및 2방향 슬래브의 하중 분배와 철근 배근을 계산합니다.",
            href: "/analysis/slab",
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
            ),
        },
        {
            title: "기초 해석 (Foundation Analysis)",
            description: "독립기초, 복합기초 등 다양한 기초 형식의 지지력과 침하를 검토합니다.",
            href: "/analysis/foundation",
            icon: (
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
            ),
        },
    ];

    return (
        <main className="min-h-screen p-4 md:p-8 relative">
            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
                <div className="absolute top-[-20%] left-[20%] w-[60%] h-[60%] bg-blue-900/10 rounded-full blur-[150px]" />
            </div>

            <div className="container mx-auto space-y-8">
                <header className="flex justify-between items-center py-4 border-b border-white/5">
                    <div>
                        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                        <p className="text-slate-400 text-sm">안녕하세요, 엔지니어님</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-amber-500 flex items-center justify-center text-slate-900 font-bold">
                        E
                    </div>
                </header>

                <section>
                    <h2 className="text-xl font-semibold text-white mb-6">구조 해석 도구</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {tools.map((tool) => (
                            <AnalysisCard key={tool.href} {...tool} />
                        ))}
                    </div>
                </section>
            </div>
        </main>
    );
}
