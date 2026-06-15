import axios from "axios";
import type { AnalysisResponse, RawAnalysisResponse } from "../types";
import { toCamelCaseResponse } from "./transform";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

export const analyzeAudio = async (file: File): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await API.post<RawAnalysisResponse>("/analyze", formData);

  return toCamelCaseResponse(response.data);
};
