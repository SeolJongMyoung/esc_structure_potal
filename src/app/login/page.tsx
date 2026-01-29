import Link from "next/link";
import styles from "./login.module.css";

export default function LoginPage() {
    return (
        <main className={styles.main}>
            {/* Top Logo / Brand Name */}
            <div className={styles.brand}>
                <Link href="/" className={styles.brand}>
                    <div className={styles.logoIcon}>C</div>
                    <span className={styles.brandText}>CivilPortal</span>
                </Link>
            </div>

            <div className={styles.container}>
                <div className={styles.header}>
                    <h1 className={styles.title}>환영합니다</h1>
                    <p className={styles.subtitle}>로그인이 필요한 서비스입니다.</p>
                </div>

                <div className={styles.formSection}>
                    <form className={styles.form}>
                        <div className={styles.inputGroup}>
                            <label htmlFor="email" className={styles.label}>이메일 주소</label>
                            <input
                                id="email"
                                type="email"
                                placeholder="name@example.com"
                                className={styles.input}
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <div className={styles.labelRow}>
                                <label htmlFor="password" className={styles.label}>비밀번호</label>
                                <Link href="#" className={styles.forgotLink}>비밀번호 찾기</Link>
                            </div>
                            <input
                                id="password"
                                type="password"
                                placeholder="비밀번호를 입력하세요"
                                className={styles.input}
                            />
                        </div>

                        <button
                            type="button"
                            className={styles.loginButton}
                        >
                            로그인
                        </button>
                    </form>

                    <div className={styles.dividerContainer}>
                        <div className={styles.dividerLine}></div>
                        <span className={styles.dividerText}>또는</span>
                    </div>

                    <button
                        type="button"
                        className={styles.socialButton}
                    >
                        <svg className="w-5 h-5" viewBox="0 0 24 24" width="20" height="20">
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
                        Google 계정으로 계속하기
                    </button>
                </div>

                <div className={styles.signupContainer}>
                    계정이 없으신가요? <Link href="#" className={styles.signupLink}>지금 가입하세요</Link>
                </div>
            </div>

            {/* Bottom Footer Links */}
            <div className={styles.footer}>
                <Link href="#" className={styles.footerLink}>개인정보 처리방침</Link>
                <Link href="#" className={styles.footerLink}>서비스 이용약관</Link>
                <Link href="#" className={styles.footerLink}>고객지원</Link>
            </div>
        </main>
    );
}
