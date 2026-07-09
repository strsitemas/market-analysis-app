"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listarFavoritos, removerFavorito } from "@/lib/api";
import type { Favorito } from "@/types/monitoramento";

export default function FavoritosPage() {
  const [favoritos, setFavoritos] = useState<Favorito[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [removendo, setRemovendo] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    carregar();
  }, []);

  function carregar() {
    setCarregando(true);
    listarFavoritos()
      .then(setFavoritos)
      .catch(() => setErro("Nao foi possivel carregar os favoritos."))
      .finally(() => setCarregando(false));
  }

  async function remover(ticker: string) {
    setRemovendo(ticker);
    try {
      await removerFavorito(ticker);
      setFavoritos((atual) => atual.filter((f) => f.ticker !== ticker));
    } catch {
      setErro(`Falha ao remover ${ticker}.`);
    } finally {
      setRemovendo(null);
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Meus favoritos</h1>
        <Link
          href="/analise"
          className="text-sm text-sky-600 hover:underline"
        >
          Voltar para analise
        </Link>
      </div>

      {erro && <p className="mb-4 text-sm text-rose-600">{erro}</p>}

      {carregando ? (
        <p className="text-sm text-slate-500">Carregando...</p>
      ) : favoritos.length === 0 ? (
        <p className="text-sm text-slate-500">
          Nenhum ativo favoritado ainda. Va em{" "}
          <Link href="/analise" className="text-sky-600 hover:underline">
            Analise
          </Link>{" "}
          e clique na estrela de um ativo.
        </p>
      ) : (
        <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200">
          {favoritos.map((f) => (
            <li
              key={f.id}
              className="flex items-center justify-between px-4 py-3"
            >
              <div>
                <p className="font-medium text-slate-800">{f.ticker}</p>
                <p className="text-xs text-slate-500">
                  Adicionado em {new Date(f.criado_em).toLocaleDateString("pt-BR")}
                </p>
              </div>
              <button
                type="button"
                onClick={() => remover(f.ticker)}
                disabled={removendo === f.ticker}
                className="rounded-md border border-rose-200 px-3 py-1 text-xs text-rose-600 hover:bg-rose-50 disabled:opacity-40"
              >
                {removendo === f.ticker ? "Removendo..." : "Remover"}
              </button>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}