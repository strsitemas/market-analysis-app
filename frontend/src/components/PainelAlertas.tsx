"use client";

import { useEffect, useState } from "react";
import {
  ativarAlerta,
  criarAlerta,
  listarAlertas,
  listarDisparos,
  marcarDisparoComoLido,
  pausarAlerta,
  removerAlerta,
  verificarAlertasAgora,
} from "@/lib/api";
import type { Alerta, AlertaDisparo, TipoAlerta } from "@/types/monitoramento";

const LABEL_TIPO: Record<TipoAlerta, string> = {
  preco_acima: "Preco acima de",
  preco_abaixo: "Preco abaixo de",
  rsi_acima: "RSI acima de",
  rsi_abaixo: "RSI abaixo de",
  sinal_igual: "Sinal igual a",
};

const USA_SINAL: TipoAlerta[] = ["sinal_igual"];

export function PainelAlertas() {
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [disparos, setDisparos] = useState<AlertaDisparo[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [verificando, setVerificando] = useState(false);

  const [novoTicker, setNovoTicker] = useState("");
  const [novoTipo, setNovoTipo] = useState<TipoAlerta>("preco_acima");
  const [novoValor, setNovoValor] = useState("");
  const [novoSinal, setNovoSinal] = useState("compra");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    carregar();
  }, []);

  function carregar() {
    setCarregando(true);
    Promise.all([listarAlertas(), listarDisparos()])
      .then(([a, d]) => {
        setAlertas(a);
        setDisparos(d);
      })
      .catch(() => setErro("Falha ao carregar alertas."))
      .finally(() => setCarregando(false));
  }

  function tickerDoAlerta(alertaId: number): string {
    return alertas.find((a) => a.id === alertaId)?.ticker ?? `#${alertaId}`;
  }

  async function handleCriar(e: React.FormEvent) {
    e.preventDefault();
    if (!novoTicker.trim()) {
      setErro("Informe um ticker.");
      return;
    }
    const parametros = USA_SINAL.includes(novoTipo)
      ? { sinal: novoSinal }
      : { valor: Number(novoValor) };

    if (!USA_SINAL.includes(novoTipo) && Number.isNaN(Number(novoValor))) {
      setErro("Informe um valor numerico valido.");
      return;
    }

    setSalvando(true);
    setErro(null);
    try {
      const criado = await criarAlerta(
        novoTicker.trim().toUpperCase(),
        novoTipo,
        parametros
      );
      setAlertas((atual) => [...atual, criado]);
      setNovoTicker("");
      setNovoValor("");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Falha ao criar alerta.");
    } finally {
      setSalvando(false);
    }
  }

  async function alternarAtivo(alerta: Alerta) {
    try {
      const atualizado = alerta.ativo
        ? await pausarAlerta(alerta.id)
        : await ativarAlerta(alerta.id);
      setAlertas((atual) =>
        atual.map((a) => (a.id === atualizado.id ? atualizado : a))
      );
    } catch {
      setErro("Falha ao atualizar o alerta.");
    }
  }

  async function excluir(id: number) {
    try {
      await removerAlerta(id);
      setAlertas((atual) => atual.filter((a) => a.id !== id));
    } catch {
      setErro("Falha ao remover o alerta.");
    }
  }

  async function marcarLido(id: number) {
    try {
      const atualizado = await marcarDisparoComoLido(id);
      setDisparos((atual) =>
        atual.map((d) => (d.id === atualizado.id ? atualizado : d))
      );
    } catch {
      setErro("Falha ao marcar disparo como lido.");
    }
  }

  async function verificarAgora() {
    setVerificando(true);
    try {
      await verificarAlertasAgora();
      const d = await listarDisparos();
      setDisparos(d);
    } catch {
      setErro("Falha ao verificar alertas.");
    } finally {
      setVerificando(false);
    }
  }

  if (carregando) {
    return <p className="text-sm text-slate-500">Carregando alertas...</p>;
  }

  return (
    <div className="space-y-8">
      {erro && <p className="text-sm text-rose-600">{erro}</p>}

      <form
        onSubmit={handleCriar}
        className="flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 p-4"
      >
        <div>
          <label className="block text-xs text-slate-500">Ticker</label>
          <input
            type="text"
            value={novoTicker}
            onChange={(e) => setNovoTicker(e.target.value)}
            placeholder="PETR4"
            className="mt-1 w-28 rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-500">Condicao</label>
          <select
            value={novoTipo}
            onChange={(e) => setNovoTipo(e.target.value as TipoAlerta)}
            className="mt-1 rounded-md border border-slate-300 px-2 py-1.5 text-sm"
          >
            {(Object.keys(LABEL_TIPO) as TipoAlerta[]).map((t) => (
              <option key={t} value={t}>
                {LABEL_TIPO[t]}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-500">Valor</label>
          {USA_SINAL.includes(novoTipo) ? (
            <select
              value={novoSinal}
              onChange={(e) => setNovoSinal(e.target.value)}
              className="mt-1 rounded-md border border-slate-300 px-2 py-1.5 text-sm"
            >
              <option value="compra">Compra</option>
              <option value="venda">Venda</option>
              <option value="atencao">Atencao</option>
              <option value="neutro">Neutro</option>
            </select>
          ) : (
            <input
              type="number"
              step="0.01"
              value={novoValor}
              onChange={(e) => setNovoValor(e.target.value)}
              placeholder="30.5"
              className="mt-1 w-24 rounded-md border border-slate-300 px-2 py-1.5 text-sm"
            />
          )}
        </div>
        <button
          type="submit"
          disabled={salvando}
          className="rounded-md bg-sky-600 px-4 py-1.5 text-sm text-white hover:bg-sky-700 disabled:opacity-50"
        >
          {salvando ? "Criando..." : "Criar alerta"}
        </button>
      </form>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-700">
            Alertas cadastrados
          </h2>
          <button
            type="button"
            onClick={verificarAgora}
            disabled={verificando}
            className="rounded-md border border-slate-300 px-3 py-1 text-xs text-slate-600 hover:bg-slate-50 disabled:opacity-50"
          >
            {verificando ? "Verificando..." : "Verificar agora"}
          </button>
        </div>
        {alertas.length === 0 ? (
          <p className="text-sm text-slate-500">Nenhum alerta cadastrado.</p>
        ) : (
          <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200">
            {alertas.map((a) => (
              <li
                key={a.id}
                className="flex items-center justify-between px-4 py-2 text-sm"
              >
                <span>
                  <strong>{a.ticker}</strong> — {LABEL_TIPO[a.tipo]}{" "}
                  {String(a.parametros.valor ?? a.parametros.sinal ?? "")}
                </span>
                <span className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => alternarAtivo(a)}
                    className={`rounded-full px-2 py-0.5 text-xs ${
                      a.ativo
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {a.ativo ? "Ativo" : "Pausado"}
                  </button>
                  <button
                    type="button"
                    onClick={() => excluir(a.id)}
                    className="text-xs text-rose-600 hover:underline"
                  >
                    Excluir
                  </button>
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold text-slate-700">
          Disparos recentes
        </h2>
        {disparos.length === 0 ? (
          <p className="text-sm text-slate-500">Nenhum disparo registrado ainda.</p>
        ) : (
          <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200">
            {disparos.map((d) => (
              <li
                key={d.id}
                className={`flex items-center justify-between px-4 py-2 text-sm ${
                  d.lido ? "opacity-50" : ""
                }`}
              >
                <span>
                  <strong>{tickerDoAlerta(d.alerta_id)}</strong> — valor no
                  momento: {d.valor_no_momento} —{" "}
                  {new Date(d.disparado_em).toLocaleString("pt-BR")}
                </span>
                {!d.lido && (
                  <button
                    type="button"
                    onClick={() => marcarLido(d.id)}
                    className="text-xs text-sky-600 hover:underline"
                  >
                    Marcar como lido
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}