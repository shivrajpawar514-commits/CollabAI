import Link from "next/link";
import { Sparkles, Code2, Terminal, Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/[0.08] bg-[#070911]/90 backdrop-blur-md py-12 mt-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center">
              <Code2 className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <p className="font-semibold text-white text-sm">CollabAI</p>
              <p className="text-xs text-slate-400">Student Engineering & Project Collaboration</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-6 text-sm text-slate-400">
            <Link href="/projects" className="hover:text-white transition-colors">
              Project Discovery
            </Link>
            <Link href="/projects/create" className="hover:text-white transition-colors">
              Project Planner
            </Link>
            <Link href="/privacy" className="hover:text-white transition-colors">
              Privacy Policy
            </Link>
            <Link href="/terms" className="hover:text-white transition-colors">
              Terms & Conditions
            </Link>
            <Link href="/status" className="flex items-center gap-1.5 hover:text-white transition-colors text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Status
            </Link>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 hover:text-white transition-colors"
            >
              <Code2 className="w-4 h-4" />
              GitHub
            </a>
          </div>

          <div className="text-xs text-slate-500 flex items-center gap-1">
            Released under the MIT License
          </div>
        </div>
      </div>
    </footer>
  );
}
