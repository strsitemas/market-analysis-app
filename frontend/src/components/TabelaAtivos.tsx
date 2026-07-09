"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { AnaliseCompleta } from "@/types/analise";

type CampoOrdenacao = "ticker" | "preco" | "variacao" | "rsi" | "sinal";

interface Props {
  resultados: AnaliseCompleta[];
  erros: Record<string, string>;
}

function corSinal(sinal: string) {
  if (sinal === "compra") return "bg-emerald-100 text-emerald-700";
  if (sinal === "venda") return "bg-rose-100 text-rose-700";
  if (sinal === "atencao") return "bg-amber-100 text-amber-700";
  return "bg-slate-100 text-slate-600";
}

export function TabelaAtivos({ resultados, erros }: Props) {
  const [busca, setBusca] = useState("");
  const [filtroSinal, setFiltroSinal] = useState<string>("todos");
  const [filtroTendencia, setFiltroTendencia] = useState<string>("todos");
  const [ordenarPor, setOrdenarPor] = useState<CampoOrdenacao>("ticker");
  const [ordemAsc, setOrdemAsc] = useState(true);

  function alternarOrdenacao(campo: CampoOrdenacao) {
    if (ordenarPor === campo) {
      setOrdemAsc(!ordemAsc);
    } else {
      setOrdenarPor(campo);
      setOrdemAsc(true);
    }
  }
  const listaFiltrada = useMemo(() => {
    let lista = [...resultados];

    if (busca.trim()) {
      const termo = busca.trim().toUpperCase();
      lista = lista.filter((item) => item.ticker.toUpperCase().includes(termo));
    }

    if (filtroSinal !== "todos") {
      lista = lista.filter((item) => item.sinal.sinal === filtroSinal);
    }

    if (filtroTendencia !== "todos") {
      lista = lista.filter((item) => item.tecnico.tendencia === filtroTendencia);
    }

    lista.sort((a, b) => {
      let valorA: number | string;
      let valorB: number | string;

      switch (ordenarPor) {
        case "preco":
          valorA = a.tecnico.preco_atual;
          valorB = b.tecnico.preco_atual;
          break;
        case "variacao":
          valorA = a.tecnico.variacao_diaria_pct;
          valorB = b.tecnico.variacao_diaria_pct;
          break;
        case "rsi":
          valorA = a.tecnico.rsi_14;
          valorB = b.tecnico.rsi_14;
          break;
        case "sinal":
          valorA = a.sinal.sinal;
          valorB = b.sinal.sinal;
          break;
        default:
          valorA = a.ticker;
          valorB = b.ticker;
      }

      if (typeof valorA === "string" || typeof valorB === "string") {
        const comparacao = String(valorA).localeCompare(String(valorB));
        return ordemAsc ? comparacao : -comparacao;
      }
      return ordemAsc ? valorA - valorB : valorB - valorA;
    });

    return lista;
  }, [resultados, busca, filtroSinal, filtroTendencia, ordenarPor, ordemAsc]);

  function cabecalho(label: string, campo: CampoOrdenacao) {
    const ativo = ordenarPor === campo;
    return (
      <th
        onClick={() => alternarOrdenacao(campo)}
        className="cursor-pointer select-none px-4 py-2 text-left font-medium text-slate-600 hover:text-slate-900"
      >
        {label} {ativo ? (ordemAsc ? "▲" : "▼") : ""}
      </th>
    );
  }

  return (
    <div>
      <div className="mt-6 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Buscar ticker..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
        />
        <select
          value={filtroSinal}
          onChange={(e) => setFiltroSinal(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
        >
          <option value="todos">Todos os sinais</option>
          <option value="compra">Compra</option>
          <option value="venda">Venda</option>
          <option value="atencao">Atencao</option>
          <option value="neutro">Neutro</option>
        </select>
        <select
          value={filtroTendencia}
          onChange={(e) => setFiltroTendencia(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
        >
          <option value="todos">Todas as tendencias</option>
          <option value="alta">Alta</option>
          <option value="baixa">Baixa</option>
          <option value="lateral">Lateral</option>
        </select>
        <span className="flex items-center text-xs text-slate-500">
          {listaFiltrada.length} de {resultados.length} ativos
        </span>
      </div>

      <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              {cabecalho("Ticker", "ticker")}
              {cabecalho("Preco", "preco")}
              {cabecalho("Variacao", "variacao")}
              <th className="px-4 py-2 text-left font-medium text-slate-600">Tendencia</th>
              {cabecalho("RSI", "rsi")}
              {cabecalho("Sinal", "sinal")}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {listaFiltrada.map((item) => (
              <tr key={item.ticker} className="hover:bg-slate-50">
                <td className="px-4 py-2">
                  <Link href={`/ativos/${item.ticker}`} className="font-medium text-slate-900 hover:underline">
                    {item.ticker}
                  </Link>
                </td>
                <td className="px-4 py-2">R$ {item.tecnico.preco_atual.toFixed(2)}</td>
                <td className={`px-4 py-2 ${item.tecnico.variacao_diaria_pct >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                  {item.tecnico.variacao_diaria_pct.toFixed(2)}%
                </td>
                <td className="px-4 py-2 capitalize">{item.tecnico.tendencia}</td>
                <td className="px-4 py-2">{item.tecnico.rsi_14.toFixed(1)}</td>
                <td className="px-4 py-2">
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${corSinal(item.sinal.sinal)}`}>
                    {item.sinal.sinal}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {Object.keys(erros).length > 0 && (
        <p className="mt-4 text-xs text-rose-500">
          Alguns ativos nao puderam ser carregados: {Object.keys(erros).join(", ")}
        </p>
      )}
    </div>
  );
}
