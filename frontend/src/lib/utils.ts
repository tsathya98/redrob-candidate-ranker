import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function scoreColor(score: number): string {
  if (score >= 0.9) return "#34d399";
  if (score >= 0.7) return "#7c5cff";
  if (score >= 0.4) return "#fbbf24";
  return "#fb7185";
}
