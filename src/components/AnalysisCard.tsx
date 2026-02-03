import Link from "next/link";

interface AnalysisCardProps {
    title: string;
    description: string;
    href: string;
    icon?: React.ReactNode;
}

export default function AnalysisCard({ title, description, href, icon }: AnalysisCardProps) {
    return (
        <Link href={href} className="group">
            <div className="glass-panel" style={{ height: '100%', padding: '2rem', borderRadius: '1.5rem', border: '1px solid rgba(255, 255, 255, 0.1)', transition: 'all 0.5s', position: 'relative', overflow: 'hidden' }}>
                {/* Decorative Background Glow */}
                <div style={{ position: 'absolute', top: '-6rem', right: '-6rem', width: '12rem', height: '12rem', backgroundColor: 'rgba(245, 158, 11, 0.05)', borderRadius: '50%', filter: 'blur(48px)' }} />

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '2rem', position: 'relative', zIndex: 10, textAlign: 'center' }}>
                    {/* Icon Container with Floating Effect */}
                    <div style={{ position: 'relative' }}>
                        <div style={{ width: '140px', height: '140px', borderRadius: '24px', backgroundColor: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ef4444', boxShadow: '0 10px 30px rgba(0,0,0,0.2)', position: 'relative', zIndex: 10, transition: 'transform 0.5s' }}>
                            <div style={{ width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))' }}>
                                {icon}
                            </div>
                        </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <h3 style={{ fontSize: '1.5rem', fontWeight: '900', color: 'white', transition: 'color 0.3s', margin: 0, letterSpacing: '-0.025em' }}>{title}</h3>
                        <div style={{ width: '3rem', height: '4px', backgroundColor: 'rgba(245, 158, 11, 0.2)', margin: '0 auto', borderRadius: '9999px', transition: 'all 0.5s' }} />
                        <p style={{ color: '#94a3b8', fontSize: '1rem', lineHeight: '1.6', fontWeight: '500', opacity: 0.8, margin: 0 }}>{description}</p>
                    </div>

                    {/* Action Hint */}
                    <div style={{ paddingTop: '1rem', opacity: '0', transition: 'opacity 0.5s' }} className="group-hover:opacity-100">
                        <span style={{ color: '#f59e0b', fontSize: '0.875rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                            시작하기
                            <svg style={{ width: '16px', height: '16px' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                            </svg>
                        </span>
                    </div>
                </div>
            </div>
        </Link>
    );
}
