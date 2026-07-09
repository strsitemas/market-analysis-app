"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { listarAtivosDisponiveis, obterAnaliseMultipla } from "@/lib/api";
import type { AnaliseCompleta } from "@/types/analise";
import { CardMetrica } from "./CardMetrica";

export function ResumoMercado() {
  const [resultados, setResultados] = useState<AnaliseCompleta[]>([]);
  const [erros, setErros] = useState<Record<string, string>>({});
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    let ativo = true;
    setCarregando(true);
    listarAtivosDisponiveis()
      .then((ativos) => obterAnaliseMultipla(ativos.map((a) => a.ticker)))
      .then((res) => {
        if (!ativo) return;
        setResultados(res.resultados);
        setErros(res.erros);
      })
      .finally(() => ativo && setCarregando(false));
    return () => {
      ativo = false;
    };
  }, []);

  const contagemSinais = useMemo(() => {
    const base = { compra: 0, venda: 0, atencao: 0, neutro: 0 };
    resultados.forEach((r) => {
      base[r.sinal.sinal] += 1;
    });
    return base;
  }, [resultados]);

  const topOportunidade = useMemo(
    () => [...resultados].sort((a, b) => b.scores.score_oportunidade - a.scores.score_oportunidade).slice(0, 5),
    [resultados]
  );

  const topRisco = useMemo(
    () => [...resultados].sort((a, b) => b.scores.score_risco - a.scores.score_risco).slice(0, 5),
    [resultados]
  );

  if (carregando) {
    return <p className="text-sm text-slate-500">Carregando visao geral do mercado...</p>;
  }
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
        <CardMetrica titulo="Ativos analisados" valor={String(resultados.length)} />
        <CardMetrica titulo="Compra" valor={String(contagemSinais.compra)} corValor="text-emerald-600" />
        <CardMetrica titulo="Venda" valor={String(contagemSinais.venda)} corValor="text-rose-600" />
        <CardMetrica titulo="Atencao" valor={String(contagemSinais.atencao)} corValor="text-amber-600" />
        <CardMetrica titulo="Neutro" valor={String(contagemSinais.neutro)} corValor="text-slate-600" />
      </div>

      {Object.keys(erros).length > 0 && (
        <p className="text-xs text-amber-600">
          {Object.keys(erros).length} ativo(s) nao puderam ser analisados agora.
        </p>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-lg border border-slate-200 p-4">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Maior score de oportunidade</h3>
          <ul className="space-y-2">
            {topOportunidade.map((r) => (
              <li key={r.ticker} className="flex items-center justify-between text-sm">
                <Link href={`/ativos/${r.ticker}`} className="font-medium text-slate-800 hover:underline">
                  {r.ticker}
                </Link>
                <span className="font-semibold text-emerald-600">
                  {r.scores.score_oportunidade.toFixed(0)}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-lg border border-slate-200 p-4">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Maior score de risco</h3>
          <ul className="space-y-2">
            {topRisco.map((r) => (
              <li key={r.ticker} className="flex items-center justify-between text-sm">
                <Link href={`/ativos/${r.ticker}`} className="font-medium text-slate-800 hover:underline">
                  {r.ticker}
                </Link>
                <span className="font-semibold text-rose-600">{r.scores.score_risco.toFixed(0)}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
