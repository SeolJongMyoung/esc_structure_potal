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
            <div className="glass-panel h-full p-6 rounded-xl border border-white/5 hover:border-amber-500/30 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-glow relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                    {icon}
                </div>
                <div className="space-y-4 relative z-10">
                    <div className="w-12 h-12 rounded-lg bg-slate-800/50 flex items-center justify-center text-amber-400 group-hover:bg-amber-500/10 transition-colors">
                        {icon}
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-slate-100 mb-2 group-hover:text-amber-400 transition-colors">{title}</h3>
                        <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
                    </div>
                </div>
            </div>
        </Link>
    );
}
