import Link from "next/link";
import styles from "./Navbar.module.css";

export default function Navbar() {
    return (
        <header className={styles.header}>
            <nav className={styles.navContainer}>
                <Link href="/" className={styles.logo}>
                    <svg
                        width="32"
                        height="32"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className={styles.logoIcon}
                    >
                        <path d="M2 22h20" />
                        <path d="M12 2v20" />
                        <path d="M2.5 7l9.5 5 9.5-5" />
                        <path d="M12 6l-9.5 5 9.5 5 9.5-5" />
                    </svg>
                    Civil<span className={styles.logoAccent}>Portal</span>
                </Link>
                <div className={styles.navLinks}>
                    <Link href="#" className={styles.link}>Products</Link>
                    <Link href="#" className={styles.link}>Solutions</Link>
                    <Link href="#" className={styles.link}>Resources</Link>
                    <Link href="#" className={styles.link}>Pricing</Link>
                </div>
                <div className={styles.authButtons}>
                    <Link href="/login" className={styles.loginBtn}>
                        Sign In
                    </Link>
                    <Link href="/signup" className={styles.signupBtn}>
                        Get Started
                    </Link>
                </div>
            </nav>
        </header>
    );
}
