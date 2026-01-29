import Link from "next/link";
import styles from "./Hero.module.css";

export default function Hero() {
    return (
        <section className={styles.hero}>
            <div className={styles.container}>
                <div className={styles.content}>
                    <span className={styles.badge}>Cloud-Based Engineering Platform</span>
                    <h1 className={styles.headline}>
                        Structural Analysis &<br />Design Made Simple
                    </h1>
                    <p className={styles.subheadline}>
                        A powerful, all-in-one structural engineering platform.
                        Run complex analysis, design checks, and manage your projects from anywhere.
                    </p>
                    <div className={styles.actions}>
                        <Link href="/signup" className={styles.ctaBtn}>
                            Get Started for Free
                        </Link>
                        <Link href="/demo" className={styles.secondaryBtn}>
                            Book a Demo
                        </Link>
                    </div>
                </div>

                <div className={styles.visual}>
                    <div className={styles.gridPattern} />
                    <div className={styles.imageCard}>
                        {/* Placeholder for actual product screenshot or 3D view */}
                        <div className={styles.abstractShape}>
                            <div style={{ textAlign: "center" }}>
                                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" color="#cbd5e1">
                                    <path d="M2 12h20" />
                                    <path d="M12 2v20" />
                                    <path d="M7 7l10 10" />
                                    <path d="M17 7l-10 10" />
                                </svg>
                                <div style={{ marginTop: "1rem", fontWeight: 600, color: "#64748b" }}>
                                    Interactive 3D Model
                                </div>
                            </div>
                        </div>

                        {/* Floating Card Element */}
                        <div style={{
                            position: "absolute",
                            bottom: "-20px",
                            left: "-20px",
                            background: "white",
                            padding: "1rem",
                            borderRadius: "0.75rem",
                            boxShadow: "var(--shadow-lg)",
                            border: "1px solid var(--color-border)",
                            display: "flex",
                            alignItems: "center",
                            gap: "0.75rem",
                            minWidth: "200px"
                        }}>
                            <div style={{
                                width: "40px", height: "40px",
                                borderRadius: "50%", background: "#fef3c7",
                                display: "flex", alignItems: "center", justifyContent: "center",
                                color: "#d97706"
                            }}>✓</div>
                            <div>
                                <div style={{ fontSize: "0.875rem", fontWeight: "600", color: "#0f172a" }}>Analysis Complete</div>
                                <div style={{ fontSize: "0.75rem", color: "#64748b" }}>0.04s Process time</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
