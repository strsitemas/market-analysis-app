"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/analise", label: "Análise" },
  { href: "/ativos", label: "Ativos" },
  { href: "/favoritos", label: "Favoritos" },
  { href: "/alertas", label: "Alertas" },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { usuario, carregando, sair } = useAuth();

  function aoSair() {
    sair();
    router.push("/login");
  }

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <Link href="/dashboard" className="font-semibold text-slate-900">
            Análise de Bolsa
          </Link>
          <div className="flex items-center gap-1">
            {links.map((link) => {
              const active = pathname?.startsWith(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={
                    "px-3 py-2 rounded-md text-sm font-medium transition-colors " +
                    (active
                      ? "bg-slate-900 text-white"
                      : "text-slate-600 hover:bg-slate-100")
                  }
                >
                  {link.label}
                </Link>
              );
            })}

            <div className="ml-3 pl-3 border-l border-slate-200 flex items-center gap-2">
              {carregando ? null : usuario ? (
                <>
                  <span className="text-sm text-slate-500 hidden sm:inline">
                    {usuario.email}
                  </span>
                  <button
                    onClick={aoSair}
                    className="px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-100"
                  >
                    Sair
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-100"
                  >
                    Entrar
                  </Link>
                  <Link
                    href="/registrar"
                    className="px-3 py-2 rounded-md text-sm font-medium bg-slate-900 text-white hover:bg-slate-800"
                  >
                    Cadastrar
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}