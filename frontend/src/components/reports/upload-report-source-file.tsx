import { useCreatePresignedUploadUrl } from "@/api/mutations/use-get-presigned-url-for-file-upload";
import { useUpdateFileStatus } from "@/api/mutations/use-update-file-status";
import { useFileUpload } from "@/hooks/use-file-upload";
import { FileCategory, FileStatus, FileType } from "@/types/report-file";
import axios from "axios";
import { AlertCircle, CheckCircle2, FileText, Loader2, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "../ui/button";

export interface UploadReportSourceFileProps {
  report_id: number;
}

export const UploadReportSourceFile: React.FC<UploadReportSourceFileProps> = ({
  report_id,
}) => {
  const maxSizeMB = 50;
  const maxSize = maxSizeMB * 1024 * 1024;

  const [
    { files, isDragging, errors },
    {
      handleDragEnter,
      handleDragLeave,
      handleDragOver,
      handleDrop,
      openFileDialog,
      getInputProps,
      removeFile,
    },
  ] = useFileUpload({
    accept: ".pdf,.txt",
    maxSize,
  });

  const file = files[0];
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadedKey, setUploadedKey] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const { mutateAsync: createPresignedUploadUrl } =
    useCreatePresignedUploadUrl(report_id);
  const { mutateAsync: updateFile } = useUpdateFileStatus(report_id);

  useEffect(() => {
    if (!file) return;
    let isCancelled = false;

    const uploadFile = async () => {
      try {
        setIsUploading(true);
        setUploadError(null);
        setUploadProgress(0);

        const { upload_url, s3_key, file_id } = await createPresignedUploadUrl({
          category: FileCategory.source,
          file_type: file.type === "text/plain" ? FileType.txt : FileType.pdf,
        });

        await axios.put(upload_url, file, {
          headers: { "Content-Type": "application/pdf" },
          onUploadProgress: (evt) => {
            if (!evt.total) return;
            const percent = Math.round((evt.loaded / evt.total) * 100);
            if (!isCancelled) setUploadProgress(percent);
          },
        });

        if (isCancelled) return;

        await updateFile({ file_id, status: FileStatus.done });
        setUploadedKey(s3_key);
      } catch (err: any) {
        if (!isCancelled)
          setUploadError(
            err?.response?.data?.message ||
              err.message ||
              "File upload failed. Please try again."
          );
      } finally {
        if (!isCancelled) setIsUploading(false);
      }
    };

    uploadFile();
    return () => {
      isCancelled = true;
    };
  }, [file, createPresignedUploadUrl, updateFile]);

  return (
    <div className="flex flex-col gap-2">
      <div className="relative">
        <div
          role="button"
          onClick={openFileDialog}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          data-dragging={isDragging || undefined}
          className="relative flex min-h-24 flex-col items-center justify-center overflow-hidden rounded-xl border border-dashed border-input p-4 transition-colors hover:bg-accent/50 data-[dragging=true]:bg-accent/50"
        >
          <input
            {...getInputProps()}
            className="sr-only"
            aria-label="Upload PDF or Text"
          />

          {file ? (
            <div className="flex w-full items-center justify-between gap-3 rounded-lg bg-muted/40 px-3 py-2">
              <div className="flex items-center gap-2 truncate">
                <FileText className="size-4 text-muted-foreground shrink-0" />
                <span className="text-sm font-medium truncate">
                  {file.name}
                </span>
              </div>

              {isUploading ? (
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Loader2 className="size-3 animate-spin" />
                  <span>{uploadProgress}%</span>
                </div>
              ) : uploadedKey ? (
                <div className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                  <CheckCircle2 className="size-3" />
                  <span>Uploaded</span>
                </div>
              ) : null}

              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => removeFile(file.name)}
                aria-label="Remove file"
                disabled={isUploading}
              >
                <X className="size-4" />
              </Button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center px-2 py-2 text-center">
              <div className="mb-2 flex size-12 shrink-0 items-center justify-center rounded-full border bg-background">
                <FileText className="size-4 opacity-60" />
              </div>
              <p className="mb-1.5 text-sm font-medium">
                Drop your PDF or Text file here or click to browse
              </p>
              <p className="text-xs text-muted-foreground">
                Only PDF or Text files, up to {maxSizeMB} MB
              </p>
            </div>
          )}
        </div>
      </div>

      {uploadError && (
        <div
          className="flex items-center gap-1 text-xs text-destructive"
          role="alert"
        >
          <AlertCircle className="size-3 shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}
      {errors.length > 0 && (
        <div
          className="flex items-center gap-1 text-xs text-destructive"
          role="alert"
        >
          <AlertCircle className="size-3 shrink-0" />
          <span>{errors[0]}</span>
        </div>
      )}
    </div>
  );
};
