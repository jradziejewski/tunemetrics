export interface AnalysisResponse {
  filename: string;
  durationSeconds: number;
  tempoBpm: number;
  chromagram: {
    pitchClasses: string[];
    meanEnergy: number[];
  };
  keyDetection: {
    note: string;
    key?: string;
    confidence?: number;
  };
}

export interface RawAnalysisResponse {
  filename: string;
  duration_seconds: number;
  tempo_bpm: number;
  chromagram: {
    pitch_classes: string[];
    mean_energy: number[];
  };
  key_detection: {
    note: string;
    key?: string;
    confidence?: number;
  };
}
