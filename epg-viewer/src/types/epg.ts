export interface Channel {
  sourceId: number;
  id: string;
  name: string;
  icon: string | null;
}

export interface Rating {
  system: string | null;
  value: string;
  icon: string | null;
}

export interface Program {
  title: string;
  subTitle: string | null;
  start: string;
  stop: string;
  channel: string;
  description: string | null;
  categories: string[] | null;
  credits: Record<string, string | string[]> | null;
  year: number | null;
  country: string | null;
  icon: string | null;
  episodeSeason: number | null;
  episodeNumber: number | null;
  rating: Rating[] | null;
}

export interface EPGData {
  channels: Channel[];
  programs: Record<string, Program[]>;
}