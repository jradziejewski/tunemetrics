import type { AnalysisResponse, RawAnalysisResponse } from "../types";

export const toCamelCaseResponse = (
  data: RawAnalysisResponse,
): AnalysisResponse => {
  return {
    filename: data.filename,
    durationSeconds: data.duration_seconds,
    tempoBpm: data.tempo_bpm,
    chromagram: {
      pitchClasses: data.chromagram.pitch_classes,
      meanEnergy: data.chromagram.mean_energy,
    },
    keyDetection: {
      note: data.key_detection.note,
      key: data.key_detection.key,
      confidence: data.key_detection.confidence,
    },
  };
};
