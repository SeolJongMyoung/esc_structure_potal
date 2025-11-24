import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-900/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-amber-600/10 rounded-full blur-[120px]" />
      </div>

      <div className="glass-panel p-12 rounded-2xl max-w-2xl w-full text-center space-y-8 border border-white/5 animate-fade-in">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold title-gradient pb-2">
            구조 엔지니어의<br />방문을 환영합니다
          </h1>
          <p className="text-lg text-slate-400 leading-relaxed">
            토목구조 설계를 위한 전문 플랫폼입니다.
            <br />
            다양한 구조 해석 도구를 이용하시려면 로그인이 필요합니다.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
          <Link href="/login" className="btn-primary text-lg px-10 py-4 shadow-lg shadow-amber-500/20">
            로그인 / 회원가입
          </Link>
        </div>
      </div>
    </main>
  );
}
