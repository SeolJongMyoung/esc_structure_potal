import Link from "next/link";
import styles from "./Footer.module.css";

export default function Footer() {
    return (
        <footer className={styles.footer}>
            <div className={styles.container}>
                <div className={styles.grid}>
                    <div className={styles.brandCol}>
                        <Link href="/" className={styles.logo}>
                            CivilPortal
                        </Link>
                        <p className={styles.tagline}>
                            Professional structural analysis and design software for modern civil engineers.
                        </p>
                    </div>

                    <div className={styles.column}>
                        <h4>Product</h4>
                        <ul className={styles.links}>
                            <li><Link href="#" className={styles.link}>Structural Analysis</Link></li>
                            <li><Link href="#" className={styles.link}>Design Checks</Link></li>
                            <li><Link href="#" className={styles.link}>Reporting</Link></li>
                            <li><Link href="#" className={styles.link}>API Access</Link></li>
                        </ul>
                    </div>

                    <div className={styles.column}>
                        <h4>Resources</h4>
                        <ul className={styles.links}>
                            <li><Link href="#" className={styles.link}>Documentation</Link></li>
                            <li><Link href="#" className={styles.link}>Tutorials</Link></li>
                            <li><Link href="#" className={styles.link}>Community</Link></li>
                            <li><Link href="#" className={styles.link}>Blog</Link></li>
                        </ul>
                    </div>

                    <div className={styles.column}>
                        <h4>Company</h4>
                        <ul className={styles.links}>
                            <li><Link href="#" className={styles.link}>About Us</Link></li>
                            <li><Link href="#" className={styles.link}>Careers</Link></li>
                            <li><Link href="#" className={styles.link}>Contact</Link></li>
                            <li><Link href="#" className={styles.link}>Privacy</Link></li>
                        </ul>
                    </div>
                </div>

                <div className={styles.bottom}>
                    <p>&copy; {new Date().getFullYear()} CivilPortal Inc. All rights reserved.</p>
                    <div style={{ display: "flex", gap: "1.5rem" }}>
                        <Link href="#" className={styles.link}>Terms</Link>
                        <Link href="#" className={styles.link}>Privacy</Link>
                        <Link href="#" className={styles.link}>Cookies</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
