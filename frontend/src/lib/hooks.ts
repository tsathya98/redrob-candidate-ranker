import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "./api";

export const useHealth = () => useQuery({ queryKey: ["health"], queryFn: api.health });
export const useJd = () => useQuery({ queryKey: ["jd"], queryFn: api.jd });
export const useRanking = () => useQuery({ queryKey: ["rank"], queryFn: api.rank });
export const useCandidate = (id: string | null) =>
  useQuery({ queryKey: ["candidate", id], queryFn: () => api.candidate(id!), enabled: !!id });
export const useExplain = () =>
  useMutation({ mutationFn: (id: string) => api.explain(id) });
