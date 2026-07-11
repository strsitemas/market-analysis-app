"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import {
  adicionarFavorito,
  listarFavoritos,
  obterAnaliseMultipla,
  removerFavorito,
} from "@/lib/api";
import type { AnaliseCompleta } from "@/types/analise";

type Coluna =
  | "ticker"
  | "preco"
  | "variacao"
  | "tendencia"
  | "rsi"
  | "volatilidade"
  | "risco"
  | "oportunidade"
  | "sinal";

const CORES_SINAL: Record<string, string> = {
  compra: "bg-emerald-100 text-emerald-700",
  venda: "bg-rose-100 text-rose-700",
  atencao: "bg-amber-100 text-amber-700",
  neutro: "bg-slate-100 text-slate-600",
  indeterminado: "bg-slate-100 text-slate-500",
};

export function TabelaAnalise({ tickers }: { tickers: string[] }) {
  const [dados, setDados] = useState<AnaliseCompleta[]>([]);
  const [erros, setErros] = useState<Record<string, string>>({});
  const [carregando, setCarregando] = useState(true);
  const [ordenarPor, setOrdenarPor] = useState<Coluna>("ticker");
  const [ordemAsc, setOrdemAsc] = useState(true);
  const [filtroTexto, setFiltroTexto] = useState("");
  const [filtroSinal, setFiltroSinal] = useState<string>("todos");
  const [favoritos, setFavoritos] = useState<Set<string>>(new Set());
  const [alternandoFavorito, setAlternandoFavorito] = useState<string | null>(null);
  const [avisoFavorito, setAvisoFavorito] = useState<string | null>(null);
  const [linhaExpandida, setLinhaExpandida] = useState<string | null>(null);

  useEffect(() => {
    setCarregando(true);
    obterAnaliseMultipla(tickers)
      .then((res) => {
        setDados(res.resultados);
        setErros(res.erros);
      })
      .catch(() => {
        setDados([]);
        setErros({ geral: "Nao foi possivel carregar a tabela agora. Tente novamente em instantes." });
      })
      .finally(() => setCarregando(false));
  }, [tickers]);

  useEffect(() => {
    listarFavoritos()
      .then((lista) => setFavoritos(new Set(lista.map((f) => f.ticker))))
      .catch(() => setFavoritos(new Set()));
  }, []);

  useEffect(() => {
    if (!avisoFavorito) return;
    const timeout = setTimeout(() => setAvisoFavorito(null), 4000);
    return () => clearTimeout(timeout);
  }, [avisoFavorito]);

  async function alternarFavorito(ticker: string) {
    setAlternandoFavorito(ticker);
    setAvisoFavorito(null);
    try {
      if (favoritos.has(ticker)) {
        await removerFavorito(ticker);
        setFavoritos((atual) => {
          const novo = new Set(atual);
          novo.delete(ticker);
          return novo;
        });
      } else {
        await adicionarFavorito(ticker);
        setFavoritos((atual) => new Set(atual).add(ticker));
      }
    } catch (erro) {
      const mensagem = erro instanceof Error ? erro.message : "Erro ao atualizar favorito";
      const naoAutenticado =
        mensagem.toLowerCase().includes("credenciais") ||
        mensagem.toLowerCase().includes("nao autenticado") ||
        mensagem.toLowerCase().includes("401");
      setAvisoFavorito(
        naoAutenticado
          ? "Faca login para favoritar ativos."
          : "Nao foi possivel atualizar o favorito agora."
      );
    } finally {
      setAlternandoFavorito(null);
    }
  }

  function alternarExpansao(ticker: string) {
    setLinhaExpandida((atual) => (atual === ticker ? null : ticker));
  }

  const linhas = useMemo(() => {
    let resultado = dados.filter((a) =>
      a.ticker.toLowerCase().includes(filtroTexto.toLowerCase())
    );

    if (filtroSinal !== "todos") {
      resultado = resultado.filter((a) => a.sinal.sinal === filtroSinal);
    }

    const valor = (a: AnaliseCompleta): number | string => {
      switch (ordenarPor) {
        case "ticker":
          return a.ticker;
        case "preco":
          return a.tecnico.preco_atual;
        case "variacao":
          return a.tecnico.variacao_diaria_pct;
        case "tendencia":
          return a.tecnico.tendencia;
        case "rsi":
          return a.tecnico.rsi_14;
        case "volatilidade":
          return a.estatisticas.volatilidade_anualizada_pct;
        case "risco":
          return a.scores.score_risco;
        case "oportunidade":
          return a.scores.score_oportunidade;
        case "sinal":
          return a.sinal.sinal;
      }
    };

    return [...resultado].sort((a, b) => {
      const va = valor(a);
      const vb = valor(b);
      const comparacao =
        typeof va === "string" && typeof vb === "string"
          ? va.localeCompare(vb)
          : Number(va) - Number(vb);
      return ordemAsc ? comparacao : -comparacao;
    });
  }, [dados, ordenarPor, ordemAsc, filtroTexto, filtroSinal]);

  function alternarOrdenacao(coluna: Coluna) {
    if (coluna === ordenarPor) {
      setOrdemAsc(!ordemAsc);
    } else {
      setOrdenarPor(coluna);
      setOrdemAsc(true);
    }
  }

  const colunas: { chave: Coluna; label: string }[] = [
    { chave: "ticker", label: "Ativo" },
    { chave: "preco", label: "Preco" },
    { chave: "variacao", label: "Variacao %" },
    { chave: "tendencia", label: "Tendencia" },
    { chave: "rsi", label: "RSI" },
    { chave: "volatilidade", label: "Volatilidade %" },
    { chave: "risco", label: "Score Risco" },
    { chave: "oportunidade", label: "Score Oport." },
    { chave: "sinal", label: "Sinal" },
  ];

  if (carregando) {
    return <p className="text-sm text-slate-500">Carregando analise...</p>;
  }

  return (
    <div>
      {avisoFavorito && (
        <div className="mb-3 rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          {avisoFavorito}
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Filtrar por ticker..."
          value={filtroTexto}
          onChange={(e) => setFiltroTexto(e.target.value)}
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
      </div>

      {Object.keys(erros).length > 0 && (
        <p className="mb-3 text-xs text-amber-600">
          Falha ao obter dados de: {Object.keys(erros).join(", ")}
        </p>
      )}

      <p className="mb-2 text-xs text-slate-400">
        Clique em uma linha para ver o motivo detalhado da classificacao do sinal.
      </p>

      <div className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="w-10 px-2 py-2"></th>
              {colunas.map((col) => (
                <th
                  key={col.chave}
                  onClick={() => alternarOrdenacao(col.chave)}
                  className="cursor-pointer whitespace-nowrap px-4 py-2 text-left font-medium text-slate-600 hover:text-slate-900"
                >
                  {col.label}
                  {ordenarPor === col.chave && (ordemAsc ? " ^" : " v")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {linhas.map((a) => {
              const ehFavorito = favoritos.has(a.ticker);
              const expandida = linhaExpandida === a.ticker;
              return (
                <Fragment key={a.ticker}>
                  <tr
                    onClick={() => alternarExpansao(a.ticker)}
                    className={`cursor-pointer hover:bg-slate-50 ${expandida ? "bg-slate-50" : ""}`}
                  >
                    <td className="px-2 py-2 text-center" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        onClick={() => alternarFavorito(a.ticker)}
                        disabled={alternandoFavorito === a.ticker}
                        title={ehFavorito ? "Remover dos favoritos" : "Adicionar aos favoritos"}
                        className={`text-lg leading-none transition-colors disabled:opacity-40 ${
                          ehFavorito ? "text-amber-500" : "text-slate-300 hover:text-amber-400"
                        }`}
                      >
                        {ehFavorito ? "*" : "o"}
                      </button>
                    </td>
                    <td className="px-4 py-2 font-medium">{a.ticker}</td>
                    <td className="px-4 py-2">R$ {a.tecnico.preco_atual.toFixed(2)}</td>
                    <td
                      className={`px-4 py-2 ${
                        a.tecnico.variacao_diaria_pct >= 0
                          ? "text-emerald-600"
                          : "text-rose-600"
                      }`}
                    >
                      {a.tecnico.variacao_diaria_pct.toFixed(2)}%
                    </td>
                    <td className="px-4 py-2 capitalize">{a.tecnico.tendencia}</td>
                    <td className="px-4 py-2">{a.tecnico.rsi_14.toFixed(1)}</td>
                    <td className="px-4 py-2">
                      {a.estatisticas.volatilidade_anualizada_pct.toFixed(1)}%
                    </td>
                    <td className="px-4 py-2">{a.scores.score_risco.toFixed(0)}</td>
                    <td className="px-4 py-2">{a.scores.score_oportunidade.toFixed(0)}</td>
                    <td className="px-4 py-2">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                          CORES_SINAL[a.sinal.sinal] ?? "bg-slate-100"
                        }`}
                      >
                        {a.sinal.sinal} {expandida ? "^" : "v"}
                      </span>
                    </td>
                  </tr>
                  {expandida && (
                    <tr className="bg-slate-50/60">
                      <td colSpan={10} className="px-4 py-3 text-sm text-slate-600">
                        <strong className="text-slate-800">Por que {a.sinal.sinal}?</strong>{" "}
                        {a.sinal.justificativa}
                        <div className="mt-2 grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-slate-500 sm:grid-cols-4">
                          <span>Suporte: R$ {a.tecnico.suporte.toFixed(2)}</span>
                          <span>Resistencia: R$ {a.tecnico.resistencia.toFixed(2)}</span>
                          <span>MACD: {a.tecnico.macd.macd.toFixed(3)}</span>
                          <span>Drawdown max.: {a.estatisticas.drawdown_maximo_pct.toFixed(1)}%</span>
                          <span>Retorno acumulado: {a.estatisticas.retorno_acumulado_pct.toFixed(1)}%</span>
                          <span>Correlacao Ibovespa: {a.estatisticas.correlacao_ibovespa.toFixed(2)}</span>
                          {a.fundamentos && (
                            <>
                              <span>P/L: {a.fundamentos.pl?.toFixed(1) ?? "-"}</span>
                              <span>Div. Yield: {a.fundamentos.dividend_yield_pct?.toFixed(2) ?? "-"}%</span>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}