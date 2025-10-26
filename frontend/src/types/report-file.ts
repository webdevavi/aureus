export const FileCategory = {
  source: "source",
  extract: "extract",
  output: "output",
} as const;
export type FileCategory = (typeof FileCategory)[keyof typeof FileCategory];

export const FileType = {
  pdf: "pdf",
  json: "json",
  txt: "txt",
} as const;
export type FileType = (typeof FileType)[keyof typeof FileType];

export const FileStatus = {
  pending: "pending",
  processing: "processing",
  done: "done",
  error: "error",
} as const;
export type FileStatus = (typeof FileStatus)[keyof typeof FileStatus];

export interface ReportFile {
  id: number;
  report_id: number;
  type: FileType;
  category: FileCategory;
  status: FileStatus;
  s3_bucket: string;
  s3_key: string;
  error?: string;
  created_at: string;
  updated_at: string;
}
