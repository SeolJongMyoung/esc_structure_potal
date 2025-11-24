import Link from "next/link";

export default function LoginPage() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
                <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-900/20 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-amber-600/10 rounded-full blur-[120px]" />
            </div>

            <div className="glass-panel p-8 md:p-12 rounded-2xl max-w-md w-full space-y-8 border border-white/5 animate-fade-in">
                <div className="text-center space-y-2">
                    <h1 className="text-3xl font-bold text-white">로그인</h1>
                    <p className="text-slate-400">서비스 이용을 위해 로그인해주세요</p>
                </div>

                <div className="space-y-4">
                    {/* Mock Google Login Button */}
                    <Link
                        href="/dashboard"
                        className="flex items-center justify-center gap-3 w-full bg-white text-slate-900 font-semibold py-3 px-4 rounded-lg hover:bg-slate-100 transition-colors"
                    >
                        <svg className="w-5 h-5" viewBox="0 0 24 24">
                            <path
                                fill="#EA4335"
                                d="M24 12.276c0-.816-.073-1.641-.21-2.433H12.24v4.62h6.615c-.293 1.549-1.164 2.855-2.484 3.734v3.107h4.017c2.352-2.165 3.712-5.357 3.712-9.028z"
                            />
                            <path
                                fill="#34A853"
                                d="M12.24 24c3.24 0 5.957-1.074 7.942-2.906l-4.017-3.107c-1.076.721-2.454 1.146-3.925 1.146-3.124 0-5.77-2.11-6.714-4.953H1.364v3.116C3.362 21.233 7.486 24 12.24 24z"
                            />
                            <path
                                fill="#FBBC05"
                                d="M5.526 14.18c-.247-.74-.388-1.532-.388-2.36s.14-1.62.388-2.36V6.344H1.364C.493 8.084 0 10.06 0 12.18s.493 4.096 1.364 5.836l4.162-3.836z"
                            />
                            <path
                                fill="#4285F4"
                                d="M12.24 4.36c1.76 0 3.344.605 4.586 1.791l3.438-3.438C18.192.802 15.475 0 12.24 0 7.486 0 3.362 2.767 1.364 6.344l4.162 3.836c.944-2.843 3.59-4.953 6.714-4.953z"
                            />
                        </svg>
                        Google 계정으로 로그인
                    </Link>

                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/10"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-2 bg-[#020617] text-slate-500">또는</span>
                        </div>
                    </div>

                    <form className="space-y-4">
                        <div className="space-y-2">
                            <label htmlFor="email" className="text-sm font-medium text-slate-300">이메일</label>
                            <input
                                id="email"
                                type="email"
                                placeholder="name@example.com"
                                className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-slate-600 focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all"
                            />
                        </div>
                        <div className="space-y-2">
                            <label htmlFor="password" className="text-sm font-medium text-slate-300">비밀번호</label>
                            <input
                                id="password"
                                type="password"
                                className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all"
                            />
                        </div>
                        <Link href="/dashboard" className="btn-primary w-full justify-center">
                            로그인
                        </Link>
                    </form>
                </div>

                <div className="text-center text-sm text-slate-500">
                    계정이 없으신가요? <Link href="#" className="text-amber-400 hover:text-amber-300">회원가입</Link>
                </div>
            </div>
        </main>
    );
}
