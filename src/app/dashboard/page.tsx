import AnalysisCard from "@/components/AnalysisCard";

export default function DashboardPage() {
    const FolderIcon = (
        <svg style={{ width: '80px', height: '80px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
    );

    const tools = [
        {
            title: "RC 단면 철근량 검토(RC Beam Rebar Calculator)",
            description: "RC 단면의 철근량을 검토합니다.",
            href: "/analysis/beam",
            icon: FolderIcon,
        },
        {
            title: "기둥 해석 (Column Analysis)",
            description: "축하중과 모멘트를 받는 기둥의 안정성 및 단면 설계를 수행합니다.",
            href: "/analysis/column",
            icon: FolderIcon,
        },
        {
            title: "슬래브 해석 (Slab Analysis)",
            description: "1방향 및 2방향 슬래브의 하중 분배와 철근 배근을 계산합니다.",
            href: "/analysis/slab",
            icon: FolderIcon,
        },
        {
            title: "기초 해석 (Foundation Analysis)",
            description: "독립기초, 복합기초 등 다양한 기초 형식의 지지력과 침하를 검토합니다.",
            href: "/analysis/foundation",
            icon: FolderIcon,
        },
    ];

    return (
        <main style={{ minHeight: '100vh', position: 'relative', backgroundColor: '#f8fafc', color: '#475569', WebkitFontSmoothing: 'antialiased' }}>
            {/* Premium Background System */}
            <div style={{ position: 'fixed', inset: 0, overflow: 'hidden', zIndex: -1, pointerEvents: 'none' }}>
                {/* Mesh Gradients (Light Mode Optimized) */}
                <div style={{ position: 'absolute', top: '-10%', left: '-10%', width: '40%', height: '40%', backgroundColor: 'rgba(59, 130, 246, 0.08)', borderRadius: '50%', filter: 'blur(120px)' }} />
                <div style={{ position: 'absolute', bottom: '10%', right: '-5%', width: '35%', height: '35%', backgroundColor: 'rgba(245, 158, 11, 0.05)', borderRadius: '50%', filter: 'blur(100px)' }} />
                <div style={{ position: 'absolute', top: '20%', right: '10%', width: '25%', height: '25%', backgroundColor: 'rgba(99, 102, 241, 0.06)', borderRadius: '50%', filter: 'blur(80px)' }} />

                {/* Engineering Dot Pattern Overlay */}
                <div style={{ position: 'absolute', inset: 0, opacity: 0.4, backgroundImage: 'radial-gradient(#cbd5e1 1px, transparent 1px)', backgroundSize: '1.5rem 1.5rem' }} />

                {/* Subtle Grid Lines */}
                <div style={{ position: 'absolute', inset: 0, opacity: 0.03, backgroundImage: 'linear-gradient(to right, #000000 1px, transparent 1px), linear-gradient(to bottom, #000000 1px, transparent 1px)', backgroundSize: '5rem 5rem' }} />
            </div>

            <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '3rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '3rem', position: 'relative', zIndex: 10 }}>
                <header className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '2rem', borderRadius: '1.5rem', border: '1px solid rgba(255, 255, 255, 0.8)', backgroundColor: 'rgba(255, 255, 255, 0.5)', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02)' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
                            <span style={{ padding: '0.125rem 0.5rem', borderRadius: '0.25rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.2)', fontSize: '10px', fontWeight: 'bold', color: '#d97706', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Premium Portal</span>
                            <h1 style={{ fontSize: '1.875rem', fontWeight: '900', color: '#0f172a', margin: 0, letterSpacing: '-0.025em' }}>ENGINX <span style={{ color: '#d97706' }}>DASHBOARD</span></h1>
                        </div>
                        <p style={{ color: '#64748b', fontSize: '1.125rem', fontWeight: '500', margin: 0 }}>성공적인 설계를 기원합니다, <span style={{ color: '#1e293b', fontStyle: 'italic', fontWeight: '700' }}>Seol JongMyoung</span> 엔지니어님</p>
                    </div>
                    <div style={{ position: 'relative' }}>
                        <div style={{ width: '3.5rem', height: '3.5rem', borderRadius: '50%', background: 'linear-gradient(to bottom right, #fbbf24, #d97706)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ffffff', fontSize: '1.25rem', fontWeight: '900', boxShadow: '0 10px 15px -3px rgba(217, 119, 6, 0.3)', position: 'relative', zIndex: 1, border: '2px solid rgba(255, 255, 255, 0.4)' }}>
                            E
                        </div>
                    </div>
                </header>

                <section style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ height: '2rem', width: '4px', backgroundColor: '#d97706', borderRadius: '2px' }} />
                        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e293b', margin: 0, letterSpacing: '-0.025em' }}>구조 해석 엔지니어링 도구</h2>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '2rem' }}>
                        {tools.map((tool) => (
                            <AnalysisCard key={tool.href} {...tool} />
                        ))}
                    </div>
                </section>
            </div>
        </main>
    );
}
