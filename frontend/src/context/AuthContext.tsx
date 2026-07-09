"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { login as apiLogin, logout as apiLogout, obterUsuarioAtual } from "@/lib/api";
import type { Usuario } from "@/types/auth";

interface AuthContextValue {
  usuario: Usuario | null;
  carregando: boolean;
  entrar: (email: string, senha: string) => Promise<void>;
  sair: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    // Nao ha token pra checar no localStorage: so tentamos buscar o
    // usuario atual. Se houver cookie de sessao valido, o backend
    // retorna os dados; senao, cai no catch e fica deslogado.
    obterUsuarioAtual()
      .then(setUsuario)
      .catch(() => setUsuario(null))
      .finally(() => setCarregando(false));
  }, []);

  async function entrar(email: string, senha: string) {
    await apiLogin(email, senha);
    const usuarioAtual = await obterUsuarioAtual();
    setUsuario(usuarioAtual);
  }

  async function sair() {
    await apiLogout().catch(() => undefined);
    setUsuario(null);
  }

  return (
    <AuthContext.Provider value={{ usuario, carregando, entrar, sair }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return ctx;
}