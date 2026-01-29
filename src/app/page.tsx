import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main style={{ minHeight: "100vh", backgroundColor: "var(--color-bg-main)" }}>
      <Navbar />
      <Hero />
      <Features />
      <Footer />
    </main>
  );
}

