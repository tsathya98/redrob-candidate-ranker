// Typed API client for the FastAPI demo backend. Relative base => same-origin in prod, proxied in dev.

export interface Brief {
  candidate_id: string;
  name: string;
  title: string;
  company: string;
  country: string;
  location: string;
  yoe: number;
}

export interface Components {
  relevance: number;
  title_career: number;
  experience: number;
  skill_depth: number;
  education: number;
}

export interface RankedRow extends Brief {
  status: "ranked";
  rank: number;
  score: number;
  components: Components;
  modifier: number;
  penalty_multiplier: number;
  concerns: string[];
  matched_concepts: string[];
  reasoning: string;
  naive_score: number;
}

export interface HoneypotRow extends Brief {
  status: "honeypot_filtered";
  score: number;
  honeypot_flags: string[];
  naive_score: number;
}

export interface RankStats {
  total: number;
  ranked: number;
  honeypots_filtered: number;
  naive_top10: string[];
  smart_top10: string[];
  overlap_top10: number;
}

export interface RankResponse {
  results: RankedRow[];
  honeypots: HoneypotRow[];
  stats: RankStats;
}

export interface JdRubric {
  title: string;
  experience_band: string;
  location: string;
  must_have: { name: string; weight: number }[];
  nice_to_have: { name: string }[];
  negative: { name: string; penalty?: string }[];
  component_weights: Record<string, number>;
}

export interface CandidateDetail extends Brief {
  summary: string;
  headline: string;
  career_history: {
    company: string; title: string; start_date: string; end_date: string | null;
    duration_months: number; is_current: boolean; description: string;
  }[];
  education: { institution: string; degree: string; field_of_study: string; tier: string }[];
  skills: { name: string; proficiency: string; endorsements: number; duration_months: number }[];
  redrob_signals: Record<string, unknown>;
  is_honeypot: boolean;
  honeypot_flags: string[];
  score: number;
  components: Components;
  modifier: number;
  penalties: string[];
  concerns: string[];
  reading_between_lines: { concept: string; snippets: string[] }[];
  gaps: string[];
  reasoning: string;
}

async function get<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

export const api = {
  health: () => get<{ status: string; demo_candidates: number; llm_enabled: boolean }>("/api/health"),
  jd: () => get<JdRubric>("/api/jd"),
  rank: async (): Promise<RankResponse> => {
    const r = await fetch("/api/rank", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: "{}",
    });
    if (!r.ok) throw new Error(`${r.status}`);
    return r.json();
  },
  candidate: (id: string) => get<CandidateDetail>(`/api/candidate/${id}`),
  explain: async (id: string): Promise<{ explanation: string; model: string }> => {
    const r = await fetch("/api/explain", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate_id: id }),
    });
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `${r.status}`);
    return r.json();
  },
};
