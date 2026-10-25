"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Sparkles,
  Users,
  FolderKanban,
  PlusCircle,
  LogIn,
  LogOut,
  Bell,
  Check,
  ExternalLink,
  Code2,
} from "lucide-react";
import { getAuthToken, clearAuthTokens, api, User, Notification } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [isScrolled, setIsScrolled] = useState(false);

  // Notifications state
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      api.getMe()
        .then((u) => {
          setUser(u);
          // Fetch notifications
          api.getNotifications()
            .then(setNotifications)
            .catch(() => {});
          api.getUnreadCount()
            .then((res) => setUnreadCount(res.unread_count))
            .catch(() => {});
        })
        .catch(() => {
          clearAuthTokens();
          setUser(null);
        });
    }
  }, [pathname]);

  const handleLogout = () => {
    clearAuthTokens();
    setUser(null);
    window.location.href = "/";
  };

  const handleMarkAllRead = async () => {
    try {
      await api.markAllNotificationsRead();
      setUnreadCount(0);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {}
  };

  const handleNotificationClick = async (notif: Notification) => {
    if (!notif.is_read) {
      api.markNotificationRead(notif.id).catch(() => {});
      setNotifications((prev) =>
        prev.map((n) => (n.id === notif.id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    }
    setShowNotifications(false);
  };

  const navLinks = [
    { name: "Discover Projects", href: "/projects", icon: FolderKanban },
    { name: "Find Teammates", href: "/projects?tab=teammates", icon: Users },
    { name: "Create Project", href: "/projects/create", icon: PlusCircle },
  ];

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-300 ${
        isScrolled
          ? "bg-[#090b14]/85 backdrop-blur-md border-b border-white/10 shadow-lg"
          : "bg-transparent border-b border-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 p-[1.5px] shadow-md shadow-blue-500/20 group-hover:shadow-blue-500/30 transition-all">
            <div className="w-full h-full bg-[#0d101d] rounded-[10px] flex items-center justify-center">
              <Code2 className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg tracking-tight text-white flex items-center gap-1.5">
              Collab<span className="text-gradient">AI</span>
            </span>
            <span className="text-[10px] font-medium text-slate-400 -mt-1 tracking-wider uppercase">
              Student Platform
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1 bg-white/[0.03] border border-white/[0.08] p-1.5 rounded-xl backdrop-blur-md">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={`flex items-center gap-2 px-3.5 py-1.5 text-sm font-medium rounded-lg transition-all ${
                  isActive
                    ? "bg-blue-600/20 text-blue-300 border border-blue-500/30 shadow-sm"
                    : "text-slate-300 hover:text-white hover:bg-white/[0.06]"
                }`}
              >
                <Icon className="w-4 h-4 text-slate-400" />
                {link.name}
              </Link>
            );
          })}
        </nav>

        {/* Auth / Profile Actions */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              {/* Notifications Bell */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-all relative"
                  title="Notifications"
                >
                  <Bell className="w-4 h-4" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 w-4 h-4 rounded-md bg-cyan-500 text-black text-[10px] font-extrabold flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </button>

                {/* Notifications Popover */}
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 glass-panel rounded-2xl border border-white/15 p-4 shadow-2xl bg-[#0d101d] space-y-3 z-50 animate-in fade-in duration-200">
                    <div className="flex items-center justify-between pb-2 border-b border-white/10">
                      <span className="font-bold text-white text-xs">Notifications</span>
                      {unreadCount > 0 && (
                        <button
                          onClick={handleMarkAllRead}
                          className="text-[10px] text-cyan-400 hover:text-cyan-300 font-semibold"
                        >
                          Mark all as read
                        </button>
                      )}
                    </div>

                    <div className="max-h-64 overflow-y-auto space-y-2 pr-1">
                      {notifications.map((notif) => (
                        <Link
                          key={notif.id}
                          href={notif.link || "#"}
                          onClick={() => handleNotificationClick(notif)}
                          className={`block p-2.5 rounded-xl border text-xs transition-all ${
                            notif.is_read
                              ? "bg-white/[0.02] border-white/[0.04] text-slate-400"
                              : "bg-indigo-500/10 border-indigo-500/30 text-white"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-white">{notif.title}</span>
                            <span className="text-[9px] text-slate-500">
                              {new Date(notif.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-300 mt-1 line-clamp-2">
                            {notif.message}
                          </p>
                        </Link>
                      ))}

                      {notifications.length === 0 && (
                        <p className="text-center py-4 text-xs text-slate-500">
                          No notifications yet.
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Profile Link */}
              <Link
                href="/profile/onboarding"
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-medium text-white transition-all"
              >
                <div className="w-6 h-6 rounded-full overflow-hidden bg-indigo-500/20 flex items-center justify-center text-xs text-indigo-300 font-bold">
                  {user.full_name.charAt(0)}
                </div>
                <span className="hidden sm:inline">{user.full_name}</span>
              </Link>

              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all"
                title="Log out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/auth/login"
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-white/5 rounded-lg transition-all"
              >
                <LogIn className="w-4 h-4 text-slate-400" />
                Sign In
              </Link>
              <Link
                href="/auth/login?tab=register"
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-lg shadow-sm shadow-blue-900/30 transition-all"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
